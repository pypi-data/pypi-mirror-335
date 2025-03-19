"""Python type shortcuts and helpers."""

from typing import Any, Callable, TypeAlias

ComparisonFunction: TypeAlias = Callable[[Any, Any], bool]
