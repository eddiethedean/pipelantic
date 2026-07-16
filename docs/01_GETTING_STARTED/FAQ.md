# Frequently Asked Questions

## What is PipelineModel?

PipelineModel is a Python framework for building typed, contract-driven
ETL pipelines. It models data pipelines using Python classes and type
annotations, validates them, generates portable contracts, and delegates
execution to external execution engines.

------------------------------------------------------------------------

## Is PipelineModel an orchestration framework?

No.

PipelineModel models pipelines and produces resolved `PipelinePlan` objects. It intentionally
delegates scheduling and orchestration to external systems such as
Airflow or other orchestration plugins.

------------------------------------------------------------------------

## Is PipelineModel an ETL engine?

No.

PipelineModel does not implement dataframe operations, database
connectors, schedulers, or distributed execution.

Instead, it coordinates existing tools through a common typed model.

------------------------------------------------------------------------

## Why create PipelineModel instead of using Airflow or Dagster?

Airflow and Dagster are excellent orchestration systems.

PipelineModel solves a different problem.

Its focus is:

-   typed pipeline modeling
-   contract generation
-   validation
-   portability
-   execution abstraction

PipelineModel can generate plans and backend artifacts for multiple orchestration
systems without changing pipeline definitions.

------------------------------------------------------------------------

## Why is PipelineModel inspired by FastAPI?

FastAPI demonstrated that Python type annotations can become the
foundation for an outstanding developer experience.

PipelineModel applies the same philosophy to data engineering.

Types define interfaces.

Everything else can be inferred.

------------------------------------------------------------------------

## What are Data Contracts?

Data contracts describe datasets.

PipelineModel uses ContractModel-compatible Pydantic models as the
source of truth and generates Open Data Contract Standard (ODCS)
documents from those models.

------------------------------------------------------------------------

## What are Transformation Contracts?

Transformation contracts describe the logical interface of a
transformation.

They specify:

-   inputs
-   outputs
-   parameters
-   metadata

They intentionally do not specify implementation details.

------------------------------------------------------------------------

## What are Pipeline Contracts?

Pipeline contracts describe how data contracts and transformation
contracts are connected together.

PipelineModel can generate Data Pipeline Contract Standard (DPCS)
documents directly from pipeline classes.

------------------------------------------------------------------------

## Why are execution engines separate?

Keeping execution separate allows the same logical pipeline to execute
through different runtimes.

Examples include:

-   Polars
-   Pandas
-   Airflow
-   local Python
-   future plugins

Business logic remains unchanged.

------------------------------------------------------------------------

## Which dataframe engine should I use?

PipelineModel is dataframe-engine neutral.

For new projects, Polars is generally recommended because of its modern
execution model and performance characteristics.

Pandas remains a fully supported execution option.

------------------------------------------------------------------------

## Does PipelineModel support asynchronous execution?

Yes.

Users may write synchronous (`def`) or asynchronous (`async def`)
implementations.

PipelineModel normalizes invocation internally so authors do not need to
manage event loops, worker threads, or execution scheduling.

------------------------------------------------------------------------

## Do I have to write YAML contracts?

No.

The preferred workflow is code-first.

PipelineModel generates ODCS, DTCS, and DPCS contracts automatically
from Python definitions.

Existing contracts can also be loaded and consumed.

------------------------------------------------------------------------

## Can I use existing ODCS contracts?

Yes.

PipelineModel supports loading existing ODCS contracts and integrating
them into typed pipeline definitions.

------------------------------------------------------------------------

## Is validation optional?

Validation is a core feature.

PipelineModel validates contracts, pipeline wiring, parameter types, and
implementation compatibility before execution whenever possible.

------------------------------------------------------------------------

## Can one transformation have multiple implementations?

Yes.

For example, the same transformation contract may have:

-   a Polars implementation
-   a Pandas implementation
-   a Spark implementation

The logical transformation remains unchanged.

------------------------------------------------------------------------

## Is PipelineModel tied to a specific cloud provider?

No.

PipelineModel is designed to be cloud-agnostic.

Cloud-specific integrations are implemented through plugins.

------------------------------------------------------------------------

## Can PipelineModel generate documentation?

Yes.

PipelineModel is designed to generate:

-   contract documentation
-   pipeline documentation
-   lineage diagrams
-   Mermaid graphs
-   Graphviz graphs
-   execution plans

from the same Python source code.

------------------------------------------------------------------------

## Who should use PipelineModel?

PipelineModel is intended for:

-   data engineers
-   analytics engineers
-   platform engineers
-   ETL framework authors
-   organizations adopting contract-first data engineering

------------------------------------------------------------------------

## Where should I go next?

Continue with the **Foundations** section to learn the design
philosophy, architecture, and core concepts behind PipelineModel.
