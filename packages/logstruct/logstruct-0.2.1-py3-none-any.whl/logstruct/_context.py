"""Context variables.

Context is a singly-linked list of context variable dictionaries forming a stack of scopes. Each
scope points to a parent scope. Scopes are pushed and popped by the ``context_scope`` decorator.
Scopes can shadow each keys of parent scopes.

``add_context`` and ``remove_context`` affect the variables in the nearest scope. Their effect is rolled back
when ``context_scope`` exits. These functions rewrite the nearest context dictionary, rather than mutating it,
so the context stack can be safely shared across different tasks, like threads or coroutines.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Optional, Union

# Vars, tail - using a raw tuple as a premature optimisation.
_Cell = tuple[dict, Union[None, "_Cell"]]

# Context needs to remain private so data type held by it can change.
_CONTEXT: ContextVar[Optional[_Cell]] = ContextVar("_CONTEXT", default=None)


@contextmanager
def context_scope(**kwargs: object) -> Iterator[None]:
    """Push variables to the context on enter, restore context on exit.

    >>> from logstruct import context_scope, get_context
    >>> with context_scope(a=11, b=22):
    ...     print(get_context())
    ...
    ...     with context_scope(a=222, c=33):
    ...         print(get_context())
    ...     print(get_context())
    {'a': 11, 'b': 22}
    {'a': 222, 'c': 33, 'b': 22}
    {'a': 11, 'b': 22}
    """
    prev_cell = _CONTEXT.get()
    new_cell = (kwargs, prev_cell)
    reset_token = _CONTEXT.set(new_cell)
    try:
        yield
    finally:
        _CONTEXT.reset(reset_token)


def add_context(**kwargs: object) -> None:
    """Associate context key-value pairs with the current scope.

    If running without a scope, key-value pairs will be associated with the global scope. They will remain
    there until cleared.
    """
    top_cell = _CONTEXT.get()
    if top_cell is None:
        top_cell = (kwargs, None)
        _CONTEXT.set(top_cell)
        return

    top_vars, tail = top_cell
    new_vars = {**top_vars, **kwargs}
    _CONTEXT.set((new_vars, tail))


def remove_context(*keys: str) -> None:
    """Disassociate keys from the current scope, leaving other scopes unaffected."""
    top_cell = _CONTEXT.get()
    if top_cell is None:
        return

    top_vars, tail = top_cell
    # This is somewhat optimised in case `remove_context` is used in a tight loop - a comprehension would be
    # slower than copying the dictionary.
    new_vars = top_vars.copy()
    for k in keys:
        try:  # noqa: SIM105 - catching KeyError is faster than calling dict.pop or contextlib.suppress
            del new_vars[k]
        except KeyError:
            pass
    _CONTEXT.set((new_vars, tail))


def clear_scope() -> None:
    """Clear the current context scope, leaving enclosing scopes unaffected."""
    top_cell = _CONTEXT.get()
    if top_cell is None:
        return

    _, tail = top_cell
    _CONTEXT.set(({}, tail))


def get_context() -> dict[str, Any]:
    """Get current context as dict, topmost keys win over later keys."""
    context: dict[str, object] = {}
    cell = _CONTEXT.get()
    # This could be optimised by caching the materialised context dictionary in the cell.
    while cell is not None:
        kv, tail = cell
        context.update((k, v) for k, v in kv.items() if k not in context)
        cell = tail
    return context
