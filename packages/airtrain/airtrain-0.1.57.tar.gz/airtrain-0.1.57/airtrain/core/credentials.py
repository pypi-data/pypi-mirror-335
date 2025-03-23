from typing import Dict, List, Optional, Set
import os
import json
from pathlib import Path
from abc import ABC, abstractmethod
import dotenv
from pydantic import BaseModel, Field, SecretStr
import yaml


class CredentialError(Exception):
    """Base exception for credential-related errors"""

    pass


class CredentialNotFoundError(CredentialError):
    """Raised when a required credential is not found"""

    pass


class CredentialValidationError(CredentialError):
    """Raised when credentials fail validation"""

    pass


class BaseCredentials(BaseModel):
    """Base class for all credential configurations"""

    _loaded: bool = False
    _required_credentials: Set[str] = set()

    def load_to_env(self) -> None:
        """Load credentials into environment variables"""
        for field_name, field_value in self:
            if isinstance(field_value, SecretStr):
                value = field_value.get_secret_value()
            else:
                value = str(field_value)
            os.environ[field_name.upper()] = value
        self._loaded = True

    @classmethod
    def from_env(cls) -> "BaseCredentials":
        """Create credentials instance from environment variables"""
        field_values = {}
        for field_name in cls.model_fields:
            env_key = field_name.upper()
            if env_value := os.getenv(env_key):
                field_values[field_name] = env_value
        return cls(**field_values)

    @classmethod
    def from_file(cls, file_path: Path) -> "BaseCredentials":
        """Load credentials from a file (supports .env, .json, .yaml)"""
        if not file_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {file_path}")

        if file_path.suffix == ".env":
            dotenv.load_dotenv(file_path)
            return cls.from_env()

        elif file_path.suffix == ".json":
            with open(file_path) as f:
                data = json.load(f)
            return cls(**data)

        elif file_path.suffix in {".yaml", ".yml"}:
            with open(file_path) as f:
                data = yaml.safe_load(f)
            return cls(**data)

        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def save_to_file(self, file_path: Path) -> None:
        """Save credentials to a file"""
        data = self.model_dump(exclude={"_loaded"})

        # Convert SecretStr to plain strings for saving
        for key, value in data.items():
            if isinstance(value, SecretStr):
                data[key] = value.get_secret_value()

        if file_path.suffix == ".env":
            with open(file_path, "w") as f:
                for key, value in data.items():
                    f.write(f"{key.upper()}={value}\n")

        elif file_path.suffix == ".json":
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)

        elif file_path.suffix in {".yaml", ".yml"}:
            with open(file_path, "w") as f:
                yaml.dump(data, f)

        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    async def validate_credentials(self) -> bool:
        """Validate that all required credentials are present"""
        missing = []
        for field_name in self._required_credentials:
            value = getattr(self, field_name, None)
            if value is None or (
                isinstance(value, SecretStr) and not value.get_secret_value()
            ):
                missing.append(field_name)

        if missing:
            raise CredentialValidationError(
                f"Missing required credentials: {', '.join(missing)}"
            )
        return True

    def clear_from_env(self) -> None:
        """Remove credentials from environment variables"""
        for field_name in self.model_fields:
            env_key = field_name.upper()
            if env_key in os.environ:
                del os.environ[env_key]
        self._loaded = False
