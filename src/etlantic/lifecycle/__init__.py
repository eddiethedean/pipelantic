"""Lifecycle extension package."""

from __future__ import annotations

from etlantic.lifecycle.callbacks import (
    CallbackRegistry,
    FailureAction,
    StepFailureContext,
)
from etlantic.lifecycle.middleware import MiddlewareStack
from etlantic.lifecycle.outbound import Emit, OutboundEvent
from etlantic.lifecycle.resources import Inject, ResourceManager
from etlantic.lifecycle.runtime import PipelineRuntime

__all__ = [
    "CallbackRegistry",
    "Emit",
    "FailureAction",
    "Inject",
    "MiddlewareStack",
    "OutboundEvent",
    "PipelineRuntime",
    "ResourceManager",
    "StepFailureContext",
]
