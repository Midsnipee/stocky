"""Compatibility hooks executed on Python startup.

This module patches Pydantic 1.x so that it remains compatible with
Python 3.12. The typing module changed the signature of
``ForwardRef._evaluate`` to require the ``recursive_guard`` argument to be
passed by keyword only. Pydantic 1.10.x still uses the positional call,
which raises ``TypeError`` on import. The shim below retries the call with
the new signature when needed while preserving the original behaviour for
other cases.
"""

from __future__ import annotations

from typing import Any, ForwardRef, cast


try:  # pragma: no cover - defensive import
    from pydantic import typing as pydantic_typing
except Exception:  # pragma: no cover - pydantic not installed
    pydantic_typing = None


if pydantic_typing is not None:  # pragma: no branch - simple guard
    original_evaluate_forwardref = pydantic_typing.evaluate_forwardref

    def _evaluate_forwardref_compat(type_: Any, globalns: Any, localns: Any) -> Any:
        if isinstance(type_, ForwardRef):
            try:
                return cast(Any, type_)._evaluate(globalns, localns, set())
            except TypeError:
                return cast(Any, type_)._evaluate(
                    globalns, localns, recursive_guard=set()
                )
        return original_evaluate_forwardref(type_, globalns, localns)

    pydantic_typing.evaluate_forwardref = _evaluate_forwardref_compat

