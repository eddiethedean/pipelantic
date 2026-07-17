# DTCS and Portable Transformation Evolution

Status: Internal standards and release plan  
Owner: ETLantic/DTCS publisher and maintainers  
Applies to: ETLantic 0.11+

## Decision

DTCS is the normative and executable semantic kernel for portable
transformations. ETLantic does not maintain a second transformation-plan model.

The `dtcs` package will expose the canonical, versioned Transformation Plan
types, portable type system, operation/function identities, semantic metadata,
capability requirements, canonical serialization, and validation hooks.

ETLantic provides:

- the PySpark-inspired `etlantic.transform` authoring facade
- `@Transformation.portable` lifecycle and source-aware diagnostics
- DTCS plan attachment to transformation contracts
- pipeline planning and compiler selection
- backend compiler protocols, execution, lineage, and reports
- shared plugin conformance orchestration

Plugins consume a validated DTCS Transformation Plan. They do not consume an
independent ETLantic expression model.

## Publishing authority

ETLantic and DTCS share a publisher. The publisher can evolve the DTCS
specification and `dtcs` package when portable transformation requirements
expose missing concepts or ambiguous semantics.

Shared authority reduces coordination latency; it does not remove compatibility
discipline. Every standards change still requires:

- explicit normative specification text
- a versioned DTCS schema and Python package release
- canonical fixtures and compatibility classification
- ETLantic dependency-range and adapter updates
- compiler capability and conformance updates
- migration guidance for breaking changes

ETLantic documentation must not describe unpublished DTCS behavior as if it
were already normative.

## Versioned boundaries

Three identifiers remain distinct:

| Boundary | Proposed identifier | Authority |
|---|---|---|
| Transformation semantics and plan schema | `dtcs.transform-plan/1` | DTCS |
| Python authoring profile | `etlantic.transform/1` | ETLantic |
| Compiler plugin protocol | `etlantic.transform-compiler/1` | ETLantic Plugin SDK |

The authoring profile MUST normalize losslessly to the DTCS plan. The compiler
protocol MUST declare which DTCS plan versions it accepts. Matching an ETLantic
authoring version does not imply compiler or DTCS compatibility.

## Dependency direction

```text
DTCS specification
        ↓
dtcs package: canonical plan + semantics
        ↓
ETLantic authoring facade + planner
        ↓
ETLantic compiler protocol
        ↓
Polars / PySpark / Pandas / SQL compilers
```

The `dtcs` package must remain free of ETLantic and backend dependencies.
ETLantic may depend on a compatible `dtcs` range. Plugins may consume public
DTCS models through ETLantic's compiler context but must not import ETLantic
private adapters.

## Standards change workflow

### 1. Capture a semantic requirement

Start from an engine-independent use case and identify whether DTCS already
defines it. Backend convenience alone is not sufficient.

### 2. Specify meaning in DTCS

Add or clarify:

- semantic action or expression node
- function/operator identity
- types, coercion, nullability, and errors
- determinism, ordering, and state behavior
- capability requirement
- canonical examples and edge cases

### 3. Release the `dtcs` package

Publish canonical models, validation, serialization, and fixtures. The package
version and supported specification version must be inspectable independently.

### 4. Expose ETLantic authoring syntax

Add the PySpark-inspired facade only after the DTCS package can represent the
meaning. ETLantic syntax constructs public DTCS plan objects or a thin builder
that normalizes immediately to them.

### 5. Implement at least two compilers

New semantic families require two independent compiler implementations before
they are considered portable and stable. Experimental single-compiler support
must be labeled and capability-gated.

### 6. Publish conformance and migration evidence

Update shared fixtures, golden plans, compiler matrices, changelogs, dependency
ranges, and migration guidance before release.

## Change classification

| Change | Expected version treatment |
|---|---|
| Add optional operation/function | DTCS minor; compiler capability opt-in |
| Clarify wording without changing results | DTCS patch plus fixture if useful |
| Add required field with defaultable meaning | DTCS minor with compatibility adapter |
| Change null/type/error/order semantics | DTCS plan major |
| Remove or rename operation/function identity | DTCS plan major with migration |
| Change ETLantic spelling only | ETLantic authoring-profile version |
| Change compiler lifecycle only | compiler-protocol version |

## Required DTCS package surface

The 0.11 work should propose public imports similar to:

```python
from dtcs.plan import (
    ColumnExpression,
    DatasetExpression,
    TransformationPlan,
)
from dtcs.semantics import (
    FunctionDefinition,
    OperationDefinition,
    PortableType,
    SemanticRegistry,
)
from dtcs.validation import validate_transformation_plan
```

Names remain proposals until released by DTCS. ETLantic must depend only on
public DTCS imports and must not duplicate their Pydantic/dataclass models.

## Release train

Each ETLantic portable milestone begins with a DTCS readiness gate:

| ETLantic | DTCS prerequisite |
|---|---|
| 0.11 | canonical kernel plan, types, expressions, serialization, validation |
| 0.12 | compiler capability requirements and explain metadata |
| 0.13 | joins, unions, grouping, aggregation, and ordering semantics |
| 0.14 | conformance manifest and differential fixture schema |
| 0.15 | SQL lowering requirements, windows, and advanced function semantics |

The exact `dtcs` package versions are selected when those releases are
published. ETLantic dependency bounds must never claim compatibility before CI
passes the corresponding cross-project fixtures.

## Governance artifacts

Every portable feature proposal should link:

1. DTCS specification change or clarification
2. `dtcs` package release/version
3. ETLantic authoring API and plan mapping
4. compiler capability identifiers
5. conformance fixtures
6. migration and compatibility notes

This chain keeps standards meaning, authoring ergonomics, and backend execution
aligned while allowing both projects to evolve quickly under shared
publishing authority.

