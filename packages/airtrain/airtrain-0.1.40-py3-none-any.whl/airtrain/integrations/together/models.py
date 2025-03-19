from typing import List, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path


class TogetherAIImageInput(BaseModel):
    """Schema for Together AI image generation input"""

    prompt: str = Field(..., description="Text prompt for image generation")
    model: str = Field(
        default="black-forest-labs/FLUX.1-schnell-Free",
        description="Together AI image model to use",
    )
    steps: int = Field(default=10, description="Number of inference steps", ge=1, le=50)
    n: int = Field(default=1, description="Number of images to generate", ge=1, le=4)
    size: str = Field(
        default="1024x1024", description="Image size in format WIDTHxHEIGHT"
    )
    negative_prompt: Optional[str] = Field(
        default=None, description="Things to exclude from the generation"
    )
    seed: Optional[int] = Field(
        default=None, description="Random seed for reproducibility"
    )

    @validator("size")
    def validate_size(cls, v):
        try:
            width, height = map(int, v.split("x"))
            if width <= 0 or height <= 0:
                raise ValueError
            return v
        except:
            raise ValueError("Size must be in format WIDTHxHEIGHT (e.g., 1024x1024)")


class GeneratedImage(BaseModel):
    """Individual generated image data"""

    b64_json: str = Field(..., description="Base64 encoded image data")
    seed: Optional[int] = Field(None, description="Seed used for this image")
    finish_reason: Optional[str] = Field(
        None, description="Reason for finishing generation"
    )


class TogetherAIImageOutput(BaseModel):
    """Schema for Together AI image generation output"""

    images: List[GeneratedImage] = Field(..., description="List of generated images")
    model: str = Field(..., description="Model used for generation")
    prompt: str = Field(..., description="Original prompt used")
    total_time: float = Field(..., description="Time taken for generation in seconds")
    usage: dict = Field(
        default_factory=dict, description="Usage statistics and billing information"
    )
