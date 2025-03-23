import pytest

from .bqx import MagicsContext

pytest.skip("skip", allow_module_level=True)


def test_context():
    ctx = MagicsContext()
    # ctx.set_field("max-rows", "1000")
    # ctx.set_field("dry-run", "true")
    ctx = ctx.update(max_rows="1000", dry_run="True", exclude_fields="a,b")
    assert ctx.max_rows == 1000
    assert ctx.dry_run
    assert ctx.exclude_fields == ["a", "b"]


def test_dry_run_query():
    ctx = MagicsContext()
    ctx = ctx.update(max_rows="1000", dry_run="True", exclude_fields="a,b,SamplingRandomNumber")
    df = ctx.run_query("select * from `vix-one.temp_sg.treatments`")
    assert df is None


def test_run_query_with_result():
    ctx = MagicsContext()
    ctx = ctx.update(max_rows="1000", dry_run="false", exclude_fields="a,b,SamplingRandomNumber")
    df = ctx.run_query("select * from `vix-one.temp_sg.treatments`")
    assert df is not None
