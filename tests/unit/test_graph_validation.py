"""Graph validation and Mermaid tests."""

from pipelinemodel import Input, Output, Pipeline, Sink, Source, Transformation
from tests.conftest import Customer, RawCustomer


class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    result: Output[Customer]


class Echo(Transformation):
    customers: Input[Customer]
    result: Output[Customer]


def test_missing_input_diagnostic() -> None:
    class Pipe(Pipeline):
        raw: Source[RawCustomer] = Source(binding="raw")
        # intentionally omit customers binding via a broken step — use empty by hacking
        normalized = NormalizeCustomers.step()  # type: ignore[call-arg]
        out: Sink[Customer] = Sink(input=normalized.result, binding="out")

    report = Pipe.validate()
    assert not report.valid
    assert "PMTRN101" in report.codes()


def test_cycle_diagnostic() -> None:
    class Pipe(Pipeline):
        raw: Source[Customer] = Source(binding="raw")
        a = Echo.step(customers=raw)
        b = Echo.step(customers=a.result)
        # create cycle by wiring a sink-like self reference is hard with authoring API;
        # build a cycle by making b feed a — not expressible cleanly in class body
        # after a is defined. Instead mutate graph validation via crafted class:
        out: Sink[Customer] = Sink(input=b.result, binding="out")

    # Force a cyclic edge set by validating a synthetic scenario through
    # the public graph and then checking acyclic happy path is valid.
    assert Pipe.validate().valid

    from pipelinemodel.model import Edge, LogicalGraph, Node, NodeKind
    from pipelinemodel.validation import _detect_cycles

    graph = LogicalGraph(
        pipeline_id="test:Cycle",
        pipeline_name="Cycle",
        nodes=(
            Node(name="a", kind=NodeKind.STEP, identity="a"),
            Node(name="b", kind=NodeKind.STEP, identity="b"),
        ),
        edges=(
            Edge("a", "result", "b", "customers"),
            Edge("b", "result", "a", "customers"),
        ),
    )
    diags = _detect_cycles(graph)
    assert any(d.code == "PMPIPE301" for d in diags)


def test_mermaid_contains_nodes_and_edges() -> None:
    class Pipe(Pipeline):
        raw: Source[RawCustomer] = Source(binding="raw")
        normalized = NormalizeCustomers.step(customers=raw)
        out: Sink[Customer] = Sink(input=normalized.result, binding="out")

    text = Pipe.to_mermaid()
    assert text.startswith("flowchart LR")
    assert "Source: raw" in text
    assert "NormalizeCustomers" in text
    assert "Sink: out" in text
