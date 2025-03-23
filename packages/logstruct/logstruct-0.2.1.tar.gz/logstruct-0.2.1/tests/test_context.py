import asyncio

import pytest

from logstruct import add_context, clear_scope, context_scope, get_context, remove_context


@pytest.fixture(autouse=True)
def clean_implicit_context(request: pytest.FixtureRequest) -> None:
    request.addfinalizer(clear_scope)


def test_context() -> None:
    with context_scope(a=11, b=22):
        assert get_context() == {"a": 11, "b": 22}

        add_context(p="pushed")
        assert get_context() == {"a": 11, "b": 22, "p": "pushed"}

        with context_scope(a=222, c=333):
            assert get_context() == {"a": 222, "b": 22, "p": "pushed", "c": 333}

        assert get_context() == {"a": 11, "b": 22, "p": "pushed"}

        remove_context("p")
        assert get_context() == {"a": 11, "b": 22}
    assert get_context() == {}


def test_remove_context_removing_keys_from_topmost_context() -> None:
    """Ensure that ``remove_context`` can clear context added with `context_scope`."""
    with context_scope(a=1, b=2):
        assert get_context() == {"a": 1, "b": 2}

        remove_context("b")
        assert get_context() == {"a": 1}


def test_remove_context_not_removing_grandparent_context() -> None:
    """Ensure that ``remove_context`` won't clear keys from scopes enclosing the current scope."""
    with context_scope(a=1), context_scope(b=2), context_scope(c=3):
        assert get_context() == {"a": 1, "b": 2, "c": 3}

        remove_context("a", "b")
        assert get_context() == {"a": 1, "b": 2, "c": 3}

        remove_context("a", "b", "c")
        assert get_context() == {"a": 1, "b": 2}


def test_context_clear() -> None:
    with context_scope(root="root"):
        with context_scope(nested="nested"):
            assert get_context() == {"root": "root", "nested": "nested"}

            add_context(var="variable")
            assert get_context() == {"root": "root", "nested": "nested", "var": "variable"}

            clear_scope()
            assert get_context() == {"root": "root"}, "Only the current scope should get cleared"

        assert get_context() == {"root": "root"}
        clear_scope()
        assert get_context() == {}


def test_implicit_context() -> None:
    """Test contextvars without `context_scope`."""
    assert get_context() == {}

    add_context(k1=1)
    assert get_context() == {"k1": 1}
    add_context(k2=2)
    assert get_context() == {"k1": 1, "k2": 2}

    clear_scope()
    assert get_context() == {}


def test_explicit_context_inside_implicit_context() -> None:
    """Test `context_scope` inside a pre-existing implicit scope."""
    assert get_context() == {}

    add_context(implicit="scope1")
    assert get_context() == {"implicit": "scope1"}

    with context_scope(explicit="scope2"):
        assert get_context() == {"implicit": "scope1", "explicit": "scope2"}

    assert get_context() == {"implicit": "scope1"}
    clear_scope()
    assert get_context() == {}


def test_empty_context_scope() -> None:
    """Test contextvars without `context_scope`."""
    with context_scope():
        assert get_context() == {}
        add_context()
        assert get_context() == {}
        remove_context()
        assert get_context() == {}
        clear_scope()
        assert get_context() == {}

    with context_scope(), context_scope():
        assert get_context() == {}

    with context_scope(a=1), context_scope():
        assert get_context() == {"a": 1}
    assert get_context() == {}


def test_empty_operations_with_nonempty_scope() -> None:
    with context_scope(a=1):
        assert get_context() == {"a": 1}
        add_context()
        assert get_context() == {"a": 1}
        remove_context()
        assert get_context() == {"a": 1}


def test_empty_operations_with_implicit_scope() -> None:
    assert get_context() == {}
    add_context()
    assert get_context() == {}
    remove_context()
    assert get_context() == {}
    clear_scope()
    assert get_context() == {}

    add_context(a=1)
    assert get_context() == {"a": 1}
    add_context()
    assert get_context() == {"a": 1}
    remove_context()
    assert get_context() == {"a": 1}


@pytest.mark.asyncio
async def test_context_forking() -> None:
    """Ensure that forked contexts see the variables from the parent context."""
    second_var_set = asyncio.Event()
    first_var_unset = asyncio.Event()
    nested_scope_entered = asyncio.Event()
    context_exited = asyncio.Event()

    async def job() -> None:
        expected_stable_context = {"root": "root", "first_var": "first"}

        for caller_progress in [second_var_set, first_var_unset, nested_scope_entered, context_exited]:
            await caller_progress.wait()
            assert get_context() == expected_stable_context

    with context_scope(root="root"):
        add_context(first_var="first")

        running_job = asyncio.create_task(job())

        add_context(second_var="second")
        second_var_set.set()

        remove_context("first_var")
        first_var_unset.set()

        with context_scope(nested="nested"):
            nested_scope_entered.set()

    context_exited.set()
    await running_job


@pytest.mark.asyncio
async def test_subcontext_isolation() -> None:
    """Ensure that changes made by sub-contexts don't affect the parent scope."""
    job_set_context = asyncio.Event()
    test_validated_context = asyncio.Event()

    async def job(expected_root_context: dict[str, object]) -> None:
        with context_scope(sub_root=1):
            add_context(k="v")
            assert get_context() == {**expected_root_context, "sub_root": 1, "k": "v"}
            job_set_context.set()
            await test_validated_context.wait()

    job_1 = asyncio.create_task(job(expected_root_context={}))
    await job_set_context.wait()
    assert get_context() == {}
    test_validated_context.set()
    await job_1

    job_set_context.clear()
    test_validated_context.clear()

    with context_scope(root="root"):
        job_2 = asyncio.create_task(job(expected_root_context={"root": "root"}))
        await job_set_context.wait()
        assert get_context() == {"root": "root"}
        test_validated_context.set()
        await job_2
