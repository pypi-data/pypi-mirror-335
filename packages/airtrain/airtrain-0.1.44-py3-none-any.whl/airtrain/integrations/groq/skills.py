from typing import Generator, Optional, Dict, Any, List
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import GroqCredentials
from groq import Groq


class GroqInput(InputSchema):
    """Schema for Groq input"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the model's behavior",
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of previous conversation messages in [{'role': 'user|assistant', 'content': 'message'}] format",
    )
    model: str = Field(
        default="deepseek-r1-distill-llama-70b-specdec", description="Groq model to use"
    )
    max_tokens: int = Field(default=131072, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    stream: bool = Field(
        default=False, description="Whether to stream the response progressively"
    )


class GroqOutput(OutputSchema):
    """Schema for Groq output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(
        default_factory=dict, description="Usage statistics from the API"
    )


class GroqChatSkill(Skill[GroqInput, GroqOutput]):
    """Skill for Groq chat"""

    input_schema = GroqInput
    output_schema = GroqOutput

    def __init__(self, credentials: Optional[GroqCredentials] = None):
        super().__init__()
        self.credentials = credentials or GroqCredentials.from_env()
        self.client = Groq(api_key=self.credentials.groq_api_key.get_secret_value())

    def _build_messages(self, input_data: GroqInput) -> List[Dict[str, str]]:
        """
        Build messages list from input data including conversation history.

        Args:
            input_data: The input data containing system prompt, conversation history, and user input

        Returns:
            List[Dict[str, str]]: List of messages in the format required by Groq
        """
        messages = [{"role": "system", "content": input_data.system_prompt}]

        # Add conversation history if present
        if input_data.conversation_history:
            messages.extend(input_data.conversation_history)

        # Add current user input
        messages.append({"role": "user", "content": input_data.user_input})

        return messages

    def process_stream(self, input_data: GroqInput) -> Generator[str, None, None]:
        """Process the input and stream the response token by token."""
        try:
            messages = self._build_messages(input_data)

            stream = self.client.chat.completions.create(
                model=input_data.model,
                messages=messages,
                temperature=input_data.temperature,
                max_tokens=input_data.max_tokens,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise ProcessingError(f"Groq streaming failed: {str(e)}")

    def process(self, input_data: GroqInput) -> GroqOutput:
        """Process the input and return the complete response."""
        try:
            if input_data.stream:
                response_chunks = []
                for chunk in self.process_stream(input_data):
                    response_chunks.append(chunk)
                response = "".join(response_chunks)
                usage = {}  # Usage stats not available in streaming
            else:
                messages = self._build_messages(input_data)
                completion = self.client.chat.completions.create(
                    model=input_data.model,
                    messages=messages,
                    temperature=input_data.temperature,
                    max_tokens=input_data.max_tokens,
                    stream=False,
                )
                response = completion.choices[0].message.content
                usage = {
                    "total_tokens": completion.usage.total_tokens,
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                }

            return GroqOutput(
                response=response, used_model=input_data.model, usage=usage
            )

        except Exception as e:
            raise ProcessingError(f"Groq processing failed: {str(e)}")
