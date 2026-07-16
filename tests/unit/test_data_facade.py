"""0.3 authoring surface: Data facade and compatibility."""

from __future__ import annotations

import warnings

from contractmodel import ContractModel

from pipelantic import Data, Input, Output, Pipeline, Sink, Source, Transformation


class Customer(Data):
    id: int
    name: str


class Normalize(Transformation):
    customers: Input[Customer]
    result: Output[Customer]


class CustomerPipeline(Pipeline):
    raw: Source[Customer] = Source(binding="customers")
    normalized = Normalize.step(customers=raw)
    out: Sink[Customer] = Sink(input=normalized.result, binding="curated")


def test_data_is_contract_model() -> None:
    assert Data is ContractModel


def test_datacontractmodel_deprecated() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        from pipelantic import DataContractModel

        assert DataContractModel is Data
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_author_with_data() -> None:
    report = CustomerPipeline.validate()
    assert report.valid
    assert "structural" in report.phases
