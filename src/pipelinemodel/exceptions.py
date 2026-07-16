"""Public exception hierarchy for PipelineModel."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipelinemodel.diagnostics import ValidationReport


class PipelineModelError(Exception):
    """Base class for public PipelineModel exceptions."""


class ModelDefinitionError(PipelineModelError):
    """Raised when a class definition cannot form a usable model."""


class PipelineValidationError(PipelineModelError):
    """Raised when validation fails and the caller requested an exception."""

    def __init__(self, message: str, *, report: ValidationReport) -> None:
        super().__init__(message)
        self.report = report


class InternalPipelineModelError(PipelineModelError):
    """Raised when an internal invariant is violated."""
