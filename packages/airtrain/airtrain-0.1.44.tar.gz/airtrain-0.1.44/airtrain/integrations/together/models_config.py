from typing import Dict, NamedTuple


class ModelConfig(NamedTuple):
    organization: str
    display_name: str
    context_length: int
    quantization: str


TOGETHER_MODELS: Dict[str, ModelConfig] = {
    # DeepSeek Models
    "deepseek-ai/DeepSeek-R1": ModelConfig(
        organization="DeepSeek",
        display_name="DeepSeek-R1",
        context_length=131072,
        quantization="FP8",
    ),
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": ModelConfig(
        organization="DeepSeek",
        display_name="DeepSeek R1 Distill Llama 70B",
        context_length=131072,
        quantization="FP16",
    ),
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B": ModelConfig(
        organization="DeepSeek",
        display_name="DeepSeek R1 Distill Qwen 1.5B",
        context_length=131072,
        quantization="FP16",
    ),
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B": ModelConfig(
        organization="DeepSeek",
        display_name="DeepSeek R1 Distill Qwen 14B",
        context_length=131072,
        quantization="FP16",
    ),
    "deepseek-ai/DeepSeek-V3": ModelConfig(
        organization="DeepSeek",
        display_name="DeepSeek-V3",
        context_length=131072,
        quantization="FP8",
    ),
    # Meta Models
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3.3 70B Instruct Turbo",
        context_length=131072,
        quantization="FP8",
    ),
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3.1 8B Instruct Turbo",
        context_length=131072,
        quantization="FP8",
    ),
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3.1 70B Instruct Turbo",
        context_length=131072,
        quantization="FP8",
    ),
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3.1 405B Instruct Turbo",
        context_length=130815,
        quantization="FP8",
    ),
    "meta-llama/Meta-Llama-3-8B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3 8B Instruct Turbo",
        context_length=8192,
        quantization="FP8",
    ),
    "meta-llama/Meta-Llama-3-70B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3 70B Instruct Turbo",
        context_length=8192,
        quantization="FP8",
    ),
    "meta-llama/Llama-3.2-3B-Instruct-Turbo": ModelConfig(
        organization="Meta",
        display_name="Llama 3.2 3B Instruct Turbo",
        context_length=131072,
        quantization="FP16",
    ),
    "meta-llama/Meta-Llama-3-8B-Instruct-Lite": ModelConfig(
        organization="Meta",
        display_name="Llama 3 8B Instruct Lite",
        context_length=8192,
        quantization="INT4",
    ),
    "meta-llama/Meta-Llama-3-70B-Instruct-Lite": ModelConfig(
        organization="Meta",
        display_name="Llama 3 70B Instruct Lite",
        context_length=8192,
        quantization="INT4",
    ),
    "meta-llama/Llama-3-8b-chat-hf": ModelConfig(
        organization="Meta",
        display_name="Llama 3 8B Instruct Reference",
        context_length=8192,
        quantization="FP16",
    ),
    "meta-llama/Llama-3-70b-chat-hf": ModelConfig(
        organization="Meta",
        display_name="Llama 3 70B Instruct Reference",
        context_length=8192,
        quantization="FP16",
    ),
    "meta-llama/Llama-2-13b-chat-hf": ModelConfig(
        organization="Meta",
        display_name="LLaMA-2 Chat (13B)",
        context_length=4096,
        quantization="FP16",
    ),
    # Nvidia Models
    "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF": ModelConfig(
        organization="Nvidia",
        display_name="Llama 3.1 Nemotron 70B",
        context_length=32768,
        quantization="FP16",
    ),
    # Qwen Models
    "Qwen/Qwen2.5-Coder-32B-Instruct": ModelConfig(
        organization="Qwen",
        display_name="Qwen 2.5 Coder 32B Instruct",
        context_length=32768,
        quantization="FP16",
    ),
    "Qwen/QwQ-32B-Preview": ModelConfig(
        organization="Qwen",
        display_name="QwQ-32B-Preview",
        context_length=32768,
        quantization="FP16",
    ),
    "Qwen/Qwen2.5-7B-Instruct-Turbo": ModelConfig(
        organization="Qwen",
        display_name="Qwen 2.5 7B Instruct Turbo",
        context_length=32768,
        quantization="FP8",
    ),
    "Qwen/Qwen2.5-72B-Instruct-Turbo": ModelConfig(
        organization="Qwen",
        display_name="Qwen 2.5 72B Instruct Turbo",
        context_length=32768,
        quantization="FP8",
    ),
    "Qwen/Qwen2-72B-Instruct": ModelConfig(
        organization="Qwen",
        display_name="Qwen 2 Instruct (72B)",
        context_length=32768,
        quantization="FP16",
    ),
    "Qwen/Qwen2-VL-72B-Instruct": ModelConfig(
        organization="Qwen",
        display_name="Qwen2 VL 72B Instruct",
        context_length=32768,
        quantization="FP16",
    ),
    # Microsoft Models
    "microsoft/WizardLM-2-8x22B": ModelConfig(
        organization="Microsoft",
        display_name="WizardLM-2 8x22B",
        context_length=65536,
        quantization="FP16",
    ),
    # Google Models
    "google/gemma-2-27b-it": ModelConfig(
        organization="Google",
        display_name="Gemma 2 27B",
        context_length=8192,
        quantization="FP16",
    ),
    "google/gemma-2-9b-it": ModelConfig(
        organization="Google",
        display_name="Gemma 2 9B",
        context_length=8192,
        quantization="FP16",
    ),
    "google/gemma-2b-it": ModelConfig(
        organization="Google",
        display_name="Gemma Instruct (2B)",
        context_length=8192,
        quantization="FP16",
    ),
    # Databricks Models
    "databricks/dbrx-instruct": ModelConfig(
        organization="databricks",
        display_name="DBRX Instruct",
        context_length=32768,
        quantization="FP16",
    ),
    # Gryphe Models
    "Gryphe/MythoMax-L2-13b": ModelConfig(
        organization="Gryphe",
        display_name="MythoMax-L2 (13B)",
        context_length=4096,
        quantization="FP16",
    ),
    # Mistral AI Models
    "mistralai/Mistral-Small-24B-Instruct-2501": ModelConfig(
        organization="mistralai",
        display_name="Mistral Small 3 Instruct (24B)",
        context_length=32768,
        quantization="FP16",
    ),
    "mistralai/Mistral-7B-Instruct-v0.1": ModelConfig(
        organization="mistralai",
        display_name="Mistral (7B) Instruct",
        context_length=8192,
        quantization="FP16",
    ),
    "mistralai/Mistral-7B-Instruct-v0.2": ModelConfig(
        organization="mistralai",
        display_name="Mistral (7B) Instruct v0.2",
        context_length=32768,
        quantization="FP16",
    ),
    "mistralai/Mistral-7B-Instruct-v0.3": ModelConfig(
        organization="mistralai",
        display_name="Mistral (7B) Instruct v0.3",
        context_length=32768,
        quantization="FP16",
    ),
    "mistralai/Mixtral-8x7B-Instruct-v0.1": ModelConfig(
        organization="mistralai",
        display_name="Mixtral-8x7B Instruct (46.7B)",
        context_length=32768,
        quantization="FP16",
    ),
    "mistralai/Mixtral-8x22B-Instruct-v0.1": ModelConfig(
        organization="mistralai",
        display_name="Mixtral-8x22B Instruct (141B)",
        context_length=65536,
        quantization="FP16",
    ),
    # NousResearch Models
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": ModelConfig(
        organization="NousResearch",
        display_name="Nous Hermes 2 - Mixtral 8x7B-DPO (46.7B)",
        context_length=32768,
        quantization="FP16",
    ),
    # Upstage Models
    "upstage/SOLAR-10.7B-Instruct-v1.0": ModelConfig(
        organization="upstage",
        display_name="Upstage SOLAR Instruct v1 (11B)",
        context_length=4096,
        quantization="FP16",
    ),
}


def get_model_config(model_id: str) -> ModelConfig:
    """Get model configuration by model ID"""
    if model_id not in TOGETHER_MODELS:
        raise ValueError(f"Model {model_id} not found in Together AI models")
    return TOGETHER_MODELS[model_id]


def list_models_by_organization(organization: str) -> Dict[str, ModelConfig]:
    """Get all models for a specific organization"""
    return {
        model_id: config
        for model_id, config in TOGETHER_MODELS.items()
        if config.organization.lower() == organization.lower()
    }


def get_default_model() -> str:
    """Get the default model ID"""
    return "meta-llama/Llama-3.3-70B-Instruct-Turbo"


if __name__ == "__main__":
    print(len(TOGETHER_MODELS))
    print(get_model_config("meta-llama/Llama-3.3-70B-Instruct-Turbo"))
