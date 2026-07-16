"""Package import smoke tests."""

import pipelinemodel


def test_version() -> None:
    assert pipelinemodel.__version__ == "0.1.0"


def test_root_exports() -> None:
    assert hasattr(pipelinemodel, "Pipeline")
    assert hasattr(pipelinemodel, "Transformation")
    assert hasattr(pipelinemodel, "Input")
    assert hasattr(pipelinemodel, "Output")
    assert hasattr(pipelinemodel, "Parameter")
    assert hasattr(pipelinemodel, "Source")
    assert hasattr(pipelinemodel, "Sink")
    assert hasattr(pipelinemodel, "OutputRef")
    assert hasattr(pipelinemodel, "DataContractModel")
