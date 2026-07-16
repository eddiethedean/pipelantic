"""PipelineModel — typed, contract-driven data pipeline modeling.

0.1 provides the authoring model, logical graph construction, topology and
compatibility diagnostics, inspection, and Mermaid output.

Data contracts are provided by ContractModel. This package re-exports
``DataContractModel`` as an alias of ``contractmodel.ContractModel`` for
documentation-aligned imports.
"""

from pipelinemodel._version import __version__
from pipelinemodel.contracts import DataContractModel
from pipelinemodel.diagnostics import Diagnostic, Severity, ValidationReport
from pipelinemodel.exceptions import (
    ModelDefinitionError,
    PipelineModelError,
    PipelineValidationError,
)
from pipelinemodel.model import Edge, LogicalGraph, Node, NodeKind
from pipelinemodel.pipeline import Pipeline, Sink, Source, SubpipelineInstance
from pipelinemodel.ports import Input, Output, Parameter
from pipelinemodel.refs import OutputRef
from pipelinemodel.transformation import ImplementationRecord, Step, Transformation

__all__ = [
    "DataContractModel",
    "Diagnostic",
    "Edge",
    "ImplementationRecord",
    "Input",
    "LogicalGraph",
    "ModelDefinitionError",
    "Node",
    "NodeKind",
    "Output",
    "OutputRef",
    "Parameter",
    "Pipeline",
    "PipelineModelError",
    "PipelineValidationError",
    "Severity",
    "Sink",
    "Source",
    "Step",
    "SubpipelineInstance",
    "Transformation",
    "ValidationReport",
    "__version__",
]
