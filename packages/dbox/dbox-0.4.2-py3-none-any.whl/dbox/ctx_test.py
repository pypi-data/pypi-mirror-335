from asyncio import sleep

import pytest

from dbox.ctx import set_context, use_factory


@pytest.mark.asyncio
async def test_context():
    use_limit = use_factory(int, "limit")
    use_username = use_factory(str, "username")
    with set_context(limit=10):
        await sleep(0.001)
        with set_context(username="john"):
            with set_context(limit=5):
                assert use_limit() == 5
            assert use_limit() == 10
            assert use_username() == "john"

            use_else = use_factory(str, "else")
            assert use_else(None) is None
            with pytest.raises(RuntimeError):
                use_else()
