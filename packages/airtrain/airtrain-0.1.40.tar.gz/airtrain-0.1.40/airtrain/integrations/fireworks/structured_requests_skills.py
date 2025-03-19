from typing import Type, TypeVar, Optional, List, Dict, Any, Generator, Union
from pydantic import BaseModel, Field, create_model
import requests
import json
from loguru import logger
import re

from airtrain.core.skills import Skill, ProcessingError
from airtrain.core.schemas import InputSchema, OutputSchema
from .credentials import FireworksCredentials

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class FireworksStructuredRequestInput(InputSchema):
    """Schema for Fireworks AI structured output input using requests"""

    user_input: str = Field(..., description="User's input text")
    system_prompt: str = Field(
        default="You are a helpful assistant that provides structured data.",
        description="System prompt to guide the model's behavior",
    )
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of previous conversation messages",
    )
    model: str = Field(
        default="accounts/fireworks/models/deepseek-r1",
        description="Fireworks AI model to use",
    )
    temperature: float = Field(
        default=0.7, description="Temperature for response generation", ge=0, le=1
    )
    max_tokens: int = Field(default=4096, description="Maximum tokens in response")
    response_model: Type[ResponseT]
    stream: bool = Field(
        default=False, description="Whether to stream the response token by token"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description=(
            "A list of tools the model may use. "
            "Currently only functions supported."
        ),
    )
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None,
        description=(
            "Controls which tool is called by the model. "
            "'none', 'auto', or specific tool."
        ),
    )

    class Config:
        arbitrary_types_allowed = True


class FireworksStructuredRequestOutput(OutputSchema):
    """Schema for Fireworks AI structured output"""

    parsed_response: Any
    used_model: str
    usage: Dict[str, int]
    reasoning: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Tool calls generated by the model"
    )


class FireworksStructuredRequestSkill(
    Skill[FireworksStructuredRequestInput, FireworksStructuredRequestOutput]
):
    """Skill for getting structured responses from Fireworks AI using requests"""

    input_schema = FireworksStructuredRequestInput
    output_schema = FireworksStructuredRequestOutput
    BASE_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

    def __init__(self, credentials: Optional[FireworksCredentials] = None):
        """Initialize the skill with optional credentials"""
        super().__init__()
        self.credentials = credentials or FireworksCredentials.from_env()
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.credentials.fireworks_api_key.get_secret_value()}",
        }

    def _build_messages(
        self, input_data: FireworksStructuredRequestInput
    ) -> List[Dict[str, Any]]:
        """Build messages list from input data including conversation history."""
        messages = [{"role": "system", "content": input_data.system_prompt}]

        if input_data.conversation_history:
            messages.extend(input_data.conversation_history)

        messages.append({"role": "user", "content": input_data.user_input})
        return messages

    def _build_payload(
        self, input_data: FireworksStructuredRequestInput
    ) -> Dict[str, Any]:
        """Build the request payload."""
        payload = {
            "model": input_data.model,
            "messages": self._build_messages(input_data),
            "temperature": input_data.temperature,
            "max_tokens": input_data.max_tokens,
            "stream": input_data.stream,
            "response_format": {"type": "json_object"},
        }

        # Add tool-related parameters if provided
        if input_data.tools:
            payload["tools"] = input_data.tools
        
        if input_data.tool_choice:
            payload["tool_choice"] = input_data.tool_choice

        return payload

    def process_stream(
        self, input_data: FireworksStructuredRequestInput
    ) -> Generator[Dict[str, Any], None, None]:
        """Process the input and stream the response."""
        try:
            payload = self._build_payload(input_data)
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                data=json.dumps(payload),
                stream=True,
            )
            response.raise_for_status()

            json_buffer = []
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8").removeprefix("data: "))
                        if data["choices"][0]["delta"].get("content"):
                            content = data["choices"][0]["delta"]["content"]
                            json_buffer.append(content)
                            yield {"chunk": content}
                    except json.JSONDecodeError:
                        continue

            # Once complete, parse the full response with think tags
            if not json_buffer:
                # If no data was collected, raise error
                raise ProcessingError("No data received from Fireworks API")

            complete_response = "".join(json_buffer)
            reasoning, json_str = self._parse_response_content(complete_response)

            try:
                parsed_response = input_data.response_model.model_validate_json(
                    json_str
                )
                yield {"complete": parsed_response, "reasoning": reasoning}
            except Exception as e:
                raise ProcessingError(f"Failed to parse JSON response: {str(e)}")

        except Exception as e:
            raise ProcessingError(f"Fireworks streaming request failed: {str(e)}")

    def _parse_response_content(self, content: str) -> tuple[Optional[str], str]:
        """Parse response content to extract reasoning and JSON."""
        # Extract reasoning if present
        reasoning_match = re.search(r"<think>(.*?)</think>", content, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else None

        # Extract JSON
        json_match = re.search(r"</think>\s*(\{.*\})", content, re.DOTALL)
        json_str = json_match.group(1).strip() if json_match else content

        return reasoning, json_str

    def process(
        self, input_data: FireworksStructuredRequestInput
    ) -> FireworksStructuredRequestOutput:
        """Process the input and return structured response."""
        try:
            if input_data.stream:
                # For streaming, collect and parse the entire response
                json_buffer = []
                parsed_response = None
                reasoning = None

                for chunk in self.process_stream(input_data):
                    if "chunk" in chunk:
                        json_buffer.append(chunk["chunk"])
                    elif "complete" in chunk:
                        parsed_response = chunk["complete"]
                        reasoning = chunk.get("reasoning")

                if parsed_response is None:
                    raise ProcessingError("Failed to parse streamed response")
                
                # Make a non-streaming call to get tool calls if tools were provided
                tool_calls = None
                if input_data.tools:
                    # Create a non-streaming request to get tool calls
                    non_stream_payload = self._build_payload(input_data)
                    non_stream_payload["stream"] = False
                    
                    response = requests.post(
                        self.BASE_URL,
                        headers=self.headers,
                        data=json.dumps(non_stream_payload),
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Check for tool calls
                    if (result["choices"][0]["message"].get("tool_calls")):
                        tool_calls = [
                            {
                                "id": tool_call["id"],
                                "type": tool_call["type"],
                                "function": {
                                    "name": tool_call["function"]["name"],
                                    "arguments": tool_call["function"]["arguments"]
                                }
                            }
                            for tool_call in result["choices"][0]["message"]["tool_calls"]
                        ]

                return FireworksStructuredRequestOutput(
                    parsed_response=parsed_response,
                    used_model=input_data.model,
                    usage={"total_tokens": 0},  # Can't get usage stats from streaming
                    reasoning=reasoning,
                    tool_calls=tool_calls,
                )
            else:
                # For non-streaming, use regular request
                payload = self._build_payload(input_data)
                payload["stream"] = False  # Ensure it's not streaming

                response = requests.post(
                    self.BASE_URL, headers=self.headers, data=json.dumps(payload)
                )
                response.raise_for_status()
                result = response.json()

                # Get the content from the response
                if "choices" not in result or not result["choices"]:
                    raise ProcessingError("Invalid response format from Fireworks API")

                content = result["choices"][0]["message"].get("content", "")
                
                # Check for tool calls
                tool_calls = None
                if (result["choices"][0]["message"].get("tool_calls")):
                    tool_calls = [
                        {
                            "id": tool_call["id"],
                            "type": tool_call["type"],
                            "function": {
                                "name": tool_call["function"]["name"],
                                "arguments": tool_call["function"]["arguments"]
                            }
                        }
                        for tool_call in result["choices"][0]["message"]["tool_calls"]
                    ]

                # Parse the response content
                reasoning, json_str = self._parse_response_content(content)
                try:
                    parsed_response = input_data.response_model.model_validate_json(
                        json_str
                    )
                except Exception as e:
                    raise ProcessingError(f"Failed to parse JSON response: {str(e)}")

                return FireworksStructuredRequestOutput(
                    parsed_response=parsed_response,
                    used_model=input_data.model,
                    usage={
                        "total_tokens": result["usage"]["total_tokens"],
                        "prompt_tokens": result["usage"]["prompt_tokens"],
                        "completion_tokens": result["usage"]["completion_tokens"],
                    },
                    reasoning=reasoning,
                    tool_calls=tool_calls,
                )

        except Exception as e:
            raise ProcessingError(f"Fireworks structured request failed: {str(e)}")
