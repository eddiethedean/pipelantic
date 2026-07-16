"""Pipelantic — typed, contract-driven data pipeline modeling.

0.3 adds multi-phase validation, profiles, SecretRef, scoped registries,
schema-drift and reliability models, and an immutable PipelinePlan IR.
"""

from __future__ import annotations

import warnings
from typing import Any

from pipelantic._version import __version__
from pipelantic.capabilities import CapabilityDecision, PluginCapabilities
from pipelantic.contracts import Data, load_data_contract, write_odcs
from pipelantic.diagnostics import (
    Diagnostic,
    DiagnosticAction,
    Severity,
    SourceLocation,
    ValidationReport,
)
from pipelantic.exceptions import (
    ModelDefinitionError,
    PipelanticError,
    PipelineValidationError,
)
from pipelantic.interchange import (
    ArtifactProvenance,
    ContractBundle,
    ProvenanceKind,
    diff_data_contracts,
    diff_pipelines,
    diff_transformations,
    generate_contracts,
    graphs_equivalent,
    load_bundle,
    normalize_pipeline,
    write_contracts,
)
from pipelantic.model import Edge, LogicalGraph, Node, NodeKind
from pipelantic.pipeline import Pipeline, Sink, Source, SubpipelineInstance
from pipelantic.plan import (
    ArtifactRef,
    ArtifactStrategy,
    PipelinePlan,
    explain_plan,
    plan_pipeline,
)
from pipelantic.policy import ValidationPolicy
from pipelantic.ports import Input, Output, Parameter
from pipelantic.profile import (
    Profile,
    development_profile,
    load_profile,
    production_profile,
    resolve_profile,
    test_profile,
    write_profile,
)
from pipelantic.refs import OutputRef
from pipelantic.registry import (
    BindingDescriptor,
    ImplementationDescriptor,
    PlanningContext,
    PluginDescriptor,
    RegistryBundle,
    builtin_stub_registry,
)
from pipelantic.reliability import (
    BackfillDeclaration,
    FreshnessExpectation,
    IdempotencyDeclaration,
    MaterializationIntent,
    MaterializationMode,
    PartitionCompletenessExpectation,
    ReconciliationDeclaration,
    ReliabilityEvidence,
    RepairDeclaration,
    RetrySafetyDeclaration,
    WriteIntent,
    WriteMode,
)
from pipelantic.schema_drift import (
    DriftImpact,
    NormalizedSchema,
    SchemaChange,
    SchemaChangeSet,
    SchemaObservation,
    diff_contract_schemas,
    diff_normalized_schemas,
    normalize_schema_from_model,
)
from pipelantic.secrets import SecretRef
from pipelantic.transformation import ImplementationRecord, Step, Transformation

__all__ = [
    "ArtifactProvenance",
    "ArtifactRef",
    "ArtifactStrategy",
    "BackfillDeclaration",
    "BindingDescriptor",
    "CapabilityDecision",
    "ContractBundle",
    "Data",
    "DataContractModel",
    "Diagnostic",
    "DiagnosticAction",
    "DriftImpact",
    "Edge",
    "FreshnessExpectation",
    "IdempotencyDeclaration",
    "ImplementationDescriptor",
    "ImplementationRecord",
    "Input",
    "LogicalGraph",
    "MaterializationIntent",
    "MaterializationMode",
    "ModelDefinitionError",
    "Node",
    "NodeKind",
    "NormalizedSchema",
    "Output",
    "OutputRef",
    "Parameter",
    "PartitionCompletenessExpectation",
    "PipelanticError",
    "Pipeline",
    "PipelinePlan",
    "PipelineValidationError",
    "PlanningContext",
    "PluginCapabilities",
    "PluginDescriptor",
    "Profile",
    "ProvenanceKind",
    "ReconciliationDeclaration",
    "RegistryBundle",
    "ReliabilityEvidence",
    "RepairDeclaration",
    "RetrySafetyDeclaration",
    "SchemaChange",
    "SchemaChangeSet",
    "SchemaObservation",
    "SecretRef",
    "Severity",
    "Sink",
    "Source",
    "SourceLocation",
    "Step",
    "SubpipelineInstance",
    "Transformation",
    "ValidationPolicy",
    "ValidationReport",
    "WriteIntent",
    "WriteMode",
    "__version__",
    "builtin_stub_registry",
    "development_profile",
    "diff_contract_schemas",
    "diff_data_contracts",
    "diff_normalized_schemas",
    "diff_pipelines",
    "diff_transformations",
    "explain_plan",
    "generate_contracts",
    "graphs_equivalent",
    "load_bundle",
    "load_data_contract",
    "load_profile",
    "normalize_pipeline",
    "normalize_schema_from_model",
    "plan_pipeline",
    "production_profile",
    "resolve_profile",
    "test_profile",
    "write_contracts",
    "write_odcs",
    "write_profile",
]


def __getattr__(name: str) -> Any:
    if name == "DataContractModel":
        warnings.warn(
            "DataContractModel is deprecated; use pipelantic.Data instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return Data
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
