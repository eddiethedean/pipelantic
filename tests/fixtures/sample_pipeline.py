"""Sample pipeline fixture for CLI tests."""

from pipelantic import Data, Input, Output, Pipeline, Sink, Source, Transformation


class Row(Data):
    id: int


class Identity(Transformation):
    rows: Input[Row]
    result: Output[Row]


class SamplePipeline(Pipeline):
    raw: Source[Row] = Source(binding="rows")
    step = Identity.step(rows=raw)
    out: Sink[Row] = Sink(input=step.result, binding="out")
