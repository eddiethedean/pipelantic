"""Unit tests for identity helpers."""

from pipelinemodel.identity import (
    contract_id,
    implementation_id,
    node_id,
    port_id,
    qualified_type_id,
)


def test_qualified_type_id_is_stable() -> None:
    class Demo:
        pass

    first = qualified_type_id(Demo)
    second = qualified_type_id(Demo)
    assert first == second
    assert "Demo" in first
    assert ":" in first


def test_node_and_port_ids() -> None:
    assert node_id("pkg:Pipe", "raw") == "pkg:Pipe/raw"
    assert port_id("pkg:Pipe/raw", "result") == "pkg:Pipe/raw:result"
    assert implementation_id("pkg:T", "polars") == "pkg:T/polars"


def test_contract_id_uses_type() -> None:
    from tests.conftest import Customer

    assert contract_id(Customer) == qualified_type_id(Customer)
