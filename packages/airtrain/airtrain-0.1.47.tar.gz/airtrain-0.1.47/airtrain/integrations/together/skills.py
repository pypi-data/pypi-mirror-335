from typing import Optional, Dict, Any, List, Generator
from pydantic import Field
from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import TogetherAICredentials
from .models import TogetherAIImageInput, TogetherAIImageOutput, GeneratedImage
from pathlib import Path
import base64
import time
from together import Together


class TogetherAIInput(InputSchema):
    """Schema for Together AI input"""

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
        default="deepseek-ai/DeepSeek-R1", description="Together AI model to use"
    )
    max_tokens: int = Field(default=1024, description="Maximum tokens in response")
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    stream: bool = Field(default=False, description="Whether to stream the response")


class TogetherAIOutput(OutputSchema):
    """Schema for Together AI output"""

    response: str = Field(..., description="Model's response text")
    used_model: str = Field(..., description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Usage statistics")


class TogetherAIChatSkill(Skill[TogetherAIInput, TogetherAIOutput]):
    """Skill for Together AI chat"""

    input_schema = TogetherAIInput
    output_schema = TogetherAIOutput

    def __init__(self, credentials: Optional[TogetherAICredentials] = None):
        super().__init__()
        self.credentials = credentials or TogetherAICredentials.from_env()
        self.client = Together(
            api_key=self.credentials.together_api_key.get_secret_value()
        )

    def _build_messages(self, input_data: TogetherAIInput) -> List[Dict[str, str]]:
        """
        Build messages list from input data including conversation history.

        Args:
            input_data: The input data containing system prompt, conversation history, and user input

        Returns:
            List[Dict[str, str]]: List of messages in the format required by Together AI
        """
        messages = [{"role": "system", "content": input_data.system_prompt}]

        # Add conversation history if present
        if input_data.conversation_history:
            messages.extend(input_data.conversation_history)

        # Add current user input
        messages.append({"role": "user", "content": input_data.user_input})

        return messages

    def process_stream(self, input_data: TogetherAIInput) -> Generator[str, None, None]:
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
            raise ProcessingError(f"Together AI streaming failed: {str(e)}")

    def process(self, input_data: TogetherAIInput) -> TogetherAIOutput:
        """Process the input and return the complete response."""
        try:
            if input_data.stream:
                response_chunks = []
                for chunk in self.process_stream(input_data):
                    response_chunks.append(chunk)
                response = "".join(response_chunks)
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

            return TogetherAIOutput(
                response=response,
                used_model=input_data.model,
                usage=(
                    completion.usage.model_dump()
                    if hasattr(completion, "usage")
                    else {}
                ),
            )

        except Exception as e:
            raise ProcessingError(f"Together AI processing failed: {str(e)}")


class TogetherAIImageSkill(Skill[TogetherAIImageInput, TogetherAIImageOutput]):
    """Skill for Together AI image generation"""

    input_schema = TogetherAIImageInput
    output_schema = TogetherAIImageOutput

    def __init__(self, credentials: Optional[TogetherAICredentials] = None):
        super().__init__()
        self.credentials = credentials or TogetherAICredentials.from_env()
        self.client = Together(
            api_key=self.credentials.together_api_key.get_secret_value()
        )

    def process(self, input_data: TogetherAIImageInput) -> TogetherAIImageOutput:
        try:
            start_time = time.time()

            # Generate images
            response = self.client.images.generate(
                prompt=input_data.prompt,
                model=input_data.model,
                steps=input_data.steps,
                n=input_data.n,
                size=input_data.size,
                negative_prompt=input_data.negative_prompt,
                seed=input_data.seed,
            )

            # Calculate total time
            total_time = time.time() - start_time

            # Convert response to our output format
            generated_images = [
                GeneratedImage(
                    b64_json=img.b64_json,
                    seed=getattr(img, "seed", None),
                    finish_reason=getattr(img, "finish_reason", None),
                )
                for img in response.data
            ]

            return TogetherAIImageOutput(
                images=generated_images,
                model=input_data.model,
                prompt=input_data.prompt,
                total_time=total_time,
                usage=getattr(response, "usage", {}),
            )

        except Exception as e:
            raise ProcessingError(f"Together AI image generation failed: {str(e)}")

    def save_images(
        self, output: TogetherAIImageOutput, output_dir: Path
    ) -> List[Path]:
        """
        Save generated images to disk

        Args:
            output (TogetherAIImageOutput): Generation output containing images
            output_dir (Path): Directory to save images

        Returns:
            List[Path]: List of paths to saved images
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []
        for i, img in enumerate(output.images):
            output_path = output_dir / f"image_{i}.png"
            image_data = base64.b64decode(img.b64_json)

            with open(output_path, "wb") as f:
                f.write(image_data)

            saved_paths.append(output_path)

        return saved_paths
