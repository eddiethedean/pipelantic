"""Runtime secret resolution package."""

from __future__ import annotations

from etlantic.secrets.cache import SecretCache
from etlantic.secrets.env import EnvSecretProvider
from etlantic.secrets.file import MountedFileSecretProvider
from etlantic.secrets.provider import (
    ProviderContext,
    SecretProvider,
    SecretProviderCapabilities,
    SecretProviderDescriptor,
    SecretResolutionContext,
)
from etlantic.secrets.ref import SecretRef
from etlantic.secrets.value import SecretSerializationError, SecretValue

__all__ = [
    "EnvSecretProvider",
    "MountedFileSecretProvider",
    "ProviderContext",
    "SecretCache",
    "SecretProvider",
    "SecretProviderCapabilities",
    "SecretProviderDescriptor",
    "SecretRef",
    "SecretResolutionContext",
    "SecretSerializationError",
    "SecretValue",
]
