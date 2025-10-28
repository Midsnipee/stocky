"""Compatibility shim in front of the real FastAPI package.

FastAPI 0.103 still depends on Pydantic 1.x which, prior to 1.10.14,
uses the legacy signature of :func:`typing.ForwardRef._evaluate`. Python
3.12 makes ``recursive_guard`` keyword-only, which triggers a ``TypeError``
when FastAPI imports its OpenAPI models. The shim patches Pydantic before
delegating to the genuine FastAPI package located in site-packages.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from importlib.machinery import PathFinder
from typing import Any, ForwardRef, cast


def _patch_pydantic_forward_ref() -> None:
    try:  # pragma: no cover - depends on optional dependency
        from pydantic import typing as pydantic_typing
    except Exception:  # pragma: no cover - pydantic missing or broken
        return

    original = pydantic_typing.evaluate_forwardref

    def _compat_forwardref(type_: Any, globalns: Any, localns: Any) -> Any:
        if isinstance(type_, ForwardRef):
            try:
                return cast(Any, type_)._evaluate(globalns, localns, set())
            except TypeError:
                return cast(Any, type_)._evaluate(
                    globalns, localns, recursive_guard=set()
                )
        return original(type_, globalns, localns)

    pydantic_typing.evaluate_forwardref = _compat_forwardref


_patch_pydantic_forward_ref()

_current_dir = os.path.dirname(__file__)
_search_path = [
    entry
    for entry in sys.path
    if entry not in {"", os.getcwd(), _current_dir}
]

_original_spec = PathFinder.find_spec(__name__, _search_path)
if _original_spec is None or _original_spec.loader is None:  # pragma: no cover
    raise ImportError("Unable to locate the real fastapi package")

_original_module = importlib.util.module_from_spec(_original_spec)
# Register early to satisfy imports triggered during exec_module
sys.modules[__name__] = _original_module
_original_spec.loader.exec_module(_original_module)

globals().update(_original_module.__dict__)

