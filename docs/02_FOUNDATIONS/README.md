# Foundations

The Foundations section defines ETLantic's product identity, architectural
boundaries, vocabulary, and documentation stability model.

## Recommended Order

1. [Vision](VISION.md)
2. [Why ETLantic](WHY_ETLANTIC.md)
3. [FastAPI Philosophy](FASTAPI_PHILOSOPHY.md)
4. [Design Principles](DESIGN_PRINCIPLES.md)
5. [Core Concepts](CORE_CONCEPTS.md)
6. [Architecture](ARCHITECTURE.md)
7. [Security Model](SECURITY.md)
8. [Documentation Status](DOCUMENTATION_STATUS.md)
9. [Glossary](GLOSSARY.md)

## Foundation in One Sentence

> ETLantic uses typed Python declarations and three portable contract
> standards to build a validated logical pipeline, resolves that pipeline into
> a deterministic `PipelinePlan`, and delegates realization to external
> backends through plugins.

## Non-Negotiable Boundaries

- ODCS, DTCS, and DPCS own contract semantics.
- ContractModel operationalizes data contracts.
- ETLantic owns typed authoring, validation, planning, and coordination.
- Plugins own backend adaptation.
- External systems perform computation, scheduling, and persistence.
