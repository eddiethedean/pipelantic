# Specifications

This directory contains normative specifications owned by the ETLantic
ecosystem.

- [DTCS 2.0 Specification](https://github.com/eddiethedean/dtcs/blob/main/SPEC.md)
  is the canonical transformation-semantics specification. Version 2.0.0 adds
  the Portable Relational Profile and `dtcs.transform-plan/1`.
- [Vendored DTCS 1.0 snapshot](DTCS_SPEC.md) is retained only for historical
  comparison and must not be treated as current authority.
- [DPCS 1.0 Specification](DPCS_SPEC.md) defines pipeline-contract semantics.
- [Portable Transformation IR](PORTABLE_TRANSFORM_IR_SPEC.md) now records
  ETLantic's authoring and compiler requirements on top of the published DTCS
  2.0 plan/profile semantics. The canonical models live in `dtcs>=0.12`; the
  ETLantic authoring API is not implemented in ETLantic 0.10.

ODCS is an external standard and is not copied into this repository. See the
[ODCS Integration Guide](../03_DATA_CONTRACTS/ODCS.md) for ETLantic's
relationship with the upstream specification.

## Normative Versus Integration Documentation

Normative specifications define contract meaning with requirement language such
as `MUST`, `SHOULD`, and `MAY`.

Integration guides explain how ETLantic authors, loads, validates,
generates, and references those contracts:

- [ODCS Integration](../03_DATA_CONTRACTS/ODCS.md)
- [DTCS Integration](../04_TRANSFORMATIONS/DTCS.md)
- [DPCS Integration](../05_PIPELINES/DPCS.md)

ETLantic implementation details must not silently redefine normative
contract semantics.

The canonical current DTCS publication is
[DTCS `SPEC.md`](https://github.com/eddiethedean/dtcs/blob/main/SPEC.md). The
vendored `DTCS_SPEC.md` supports local documentation navigation and may lag the
publisher's latest revision; when they differ, the published DTCS repository is
authoritative.

The publication history and remaining ETLantic integration gaps are tracked in
the [DTCS Portable Relational Publication Record](../11_DEVELOPMENT/DTCS_PORTABLE_SPEC_PROPOSAL.md).
