"""Airtrain - A platform for building and deploying AI agents with structured skills"""

__version__ = "0.1.45"

# Core imports
from .core.skills import Skill, ProcessingError
from .core.schemas import InputSchema, OutputSchema
from .core.credentials import BaseCredentials

# Integration imports - Credentials
from .integrations.openai.credentials import OpenAICredentials
from .integrations.aws.credentials import AWSCredentials
from .integrations.google.credentials import GoogleCloudCredentials
from .integrations.anthropic.credentials import AnthropicCredentials
from .integrations.groq.credentials import GroqCredentials
from .integrations.together.credentials import TogetherAICredentials
from .integrations.ollama.credentials import OllamaCredentials
from .integrations.sambanova.credentials import SambanovaCredentials
from .integrations.cerebras.credentials import CerebrasCredentials

# Integration imports - Skills
from .integrations.openai.skills import OpenAIChatSkill, OpenAIParserSkill
from .integrations.anthropic.skills import AnthropicChatSkill
from .integrations.aws.skills import AWSBedrockSkill
from .integrations.google.skills import GoogleChatSkill
from .integrations.groq.skills import GroqChatSkill
from .integrations.together.skills import TogetherAIChatSkill
from .integrations.ollama.skills import OllamaChatSkill
from .integrations.sambanova.skills import SambanovaChatSkill
from .integrations.cerebras.skills import CerebrasChatSkill

__all__ = [
    # Core
    "Skill",
    "ProcessingError",
    "InputSchema",
    "OutputSchema",
    "BaseCredentials",
    # Credentials
    "OpenAICredentials",
    "AWSCredentials",
    "GoogleCloudCredentials",
    "AnthropicCredentials",
    "GroqCredentials",
    "TogetherAICredentials",
    "OllamaCredentials",
    "SambanovaCredentials",
    "CerebrasCredentials",
    # Skills
    "OpenAIChatSkill",
    "OpenAIParserSkill",
    "AnthropicChatSkill",
    "AWSBedrockSkill",
    "GoogleChatSkill",
    "GroqChatSkill",
    "TogetherAIChatSkill",
    "OllamaChatSkill",
    "SambanovaChatSkill",
    "CerebrasChatSkill",
]
