# Examples

The Examples section demonstrates how to build real-world pipelines using
PipelineModel.

While the rest of the documentation focuses on architecture, specifications,
and APIs, this section shows complete working examples that combine data
contracts, transformation contracts, pipeline contracts, planning, execution,
and visualization into practical solutions.

Each example follows PipelineModel best practices and is intended to be runnable,
understandable, and extensible.

## Goals

Examples should:

- Demonstrate recommended patterns.
- Showcase real-world workflows.
- Teach one concept at a time.
- Build from simple to advanced.
- Highlight reusable design patterns.
- Encourage portable pipeline design.

## Philosophy

Learn by building.

```text
Data Contracts
      │
      ▼
Transformations
      │
      ▼
Pipeline
      │
      ▼
Planning
      │
      ▼
Execution
      │
      ▼
Documentation
```

Every example should demonstrate the complete PipelineModel lifecycle.

## Organization

Suggested progression:

### Beginner

- Hello World
- Single Transformation
- CSV to CSV
- Validation Basics
- Parameters
- Callbacks

### Intermediate

- Multiple Transformations
- Branching Pipelines
- Subpipelines
- Async Pipelines
- Error Handling
- Profiles

### Advanced

- Multiple Dataframe Engines
- Airflow Execution
- Resource Providers
- Plugin Development
- Incremental Processing
- Distributed Execution

### End-to-End Projects

- Customer ETL
- Data Warehouse Load
- Lakehouse Pipeline
- Feature Engineering
- ML Inference Pipeline
- Streaming Analytics
- Data Quality Monitoring

## Example Structure

Each example should include:

- Problem statement
- Architecture diagram
- Data contracts
- Transformation contracts
- Pipeline definition
- Execution profile
- Generated Pipeline Plan
- Generated documentation
- Expected outputs
- Testing guidance

## Standards Coverage

Examples should demonstrate:

- ODCS
- DTCS
- DPCS

alongside PipelineModel APIs.

## Visualization

Where practical, examples should include:

- Mermaid diagrams
- Graphviz diagrams
- Lineage graphs
- HTML documentation
- Generated pipeline specifications

These artifacts should be generated automatically from the example pipeline.

## Testing

Every example should include automated tests covering:

- Validation
- Planning
- Execution
- Output verification
- Documentation generation

Examples should be suitable for CI execution.

## Repository Layout

A suggested directory structure:

```text
examples/
├── hello_world/
├── csv_to_csv/
├── customer_etl/
├── async_pipeline/
├── airflow/
├── plugin_sdk/
└── lakehouse/
```

Each example should be self-contained with its own README.

## Best Practices

- Keep examples focused.
- Build complexity gradually.
- Use generated documentation.
- Prefer realistic datasets.
- Demonstrate portable designs.
- Include tests.

## Anti-Patterns

Avoid:

- Oversized examples that teach too many concepts.
- Hidden dependencies.
- Backend-specific pipeline definitions.
- Skipping validation.
- Manually maintained diagrams.

## Key Principle

> Examples are executable documentation. They should demonstrate not only how
to use PipelineModel, but also why its contract-first, planner-driven
architecture enables portable, maintainable, and technology-independent data
pipelines.

## Next Step

Continue with [CSV to CSV](CSV_TO_CSV.md) to build the smallest complete
PipelineModel example currently included in this documentation set.
