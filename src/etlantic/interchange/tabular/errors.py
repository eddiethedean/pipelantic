"""Errors raised by tabular interchange contracts."""

from __future__ import annotations


class InterchangeError(ValueError):
    """Base error for tabular interchange."""


class InterchangeSelectionError(InterchangeError):
    """Raised when no contract-safe interchange mechanism can be selected."""


class InterchangeDescriptorError(InterchangeError):
    """Raised when an interchange descriptor fails closed validation."""
