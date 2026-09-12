"""Parameter sanitization and input validation handlers for Fibonacci operations."""

from typing import Any, Tuple
from .exceptions import InvalidInputError, NegativeBoundError, RangeBoundError


def sanitize_integer(
    value: Any,
    param_name: str = "bound",
    allow_negative: bool = False,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Sanitizes and converts an input value to a valid strict integer.

    Parameters
    ----------
    value : Any
        The raw input value (int, string containing integer, etc.).
    param_name : str
        The variable name used for descriptive error messages.
    allow_negative : bool
        Whether negative values are permitted. Defaults to False.
    min_value : int, optional
        Minimum allowable value (inclusive).
    max_value : int, optional
        Maximum allowable value (inclusive).

    Returns
    -------
    int
        Sanitized integer value.

    Raises
    ------
    InvalidInputError
        If value is boolean, None, float, or cannot be parsed as a base-10 integer.
    NegativeBoundError
        If value is negative and allow_negative is False.
    RangeBoundError
        If value violates min_value or max_value constraints.
    """
    # Reject booleans explicitly (since bool is a subclass of int in Python)
    if isinstance(value, bool):
        raise InvalidInputError(
            f"Parameter '{param_name}' must be an integer, got boolean ({value}).",
            details={"param": param_name, "value": value, "type": type(value).__name__},
        )

    # Reject floats or None directly to prevent silent truncation/loss of precision
    if isinstance(value, float):
        raise InvalidInputError(
            f"Parameter '{param_name}' must be an exact integer, got float ({value}).",
            details={"param": param_name, "value": value, "type": "float"},
        )

    if value is None:
        raise InvalidInputError(
            f"Parameter '{param_name}' cannot be None.",
            details={"param": param_name, "value": None},
        )

    # Handle string or integer conversion
    try:
        if isinstance(value, str):
            clean_str = value.strip().replace("_", "").replace(",", "")
            sanitized = int(clean_str)
        elif isinstance(value, int):
            sanitized = int(value)
        else:
            raise TypeError
    except (ValueError, TypeError) as exc:
        raise InvalidInputError(
            f"Parameter '{param_name}' could not be converted to an integer. Received: {value!r}",
            details={"param": param_name, "raw_value": value, "type": type(value).__name__},
        ) from exc

    # Check negative bound condition
    if not allow_negative and sanitized < 0:
        raise NegativeBoundError(
            f"Parameter '{param_name}' cannot be negative. Received: {sanitized}.",
            details={"param": param_name, "value": sanitized},
        )

    # Check min/max bounds if specified
    if min_value is not None and sanitized < min_value:
        raise RangeBoundError(
            f"Parameter '{param_name}' ({sanitized}) is below minimum allowed value ({min_value}).",
            details={"param": param_name, "value": sanitized, "min_value": min_value},
        )

    if max_value is not None and sanitized > max_value:
        raise RangeBoundError(
            f"Parameter '{param_name}' ({sanitized}) exceeds maximum allowed value ({max_value}).",
            details={"param": param_name, "value": sanitized, "max_value": max_value},
        )

    return sanitized


def validate_range_bounds(start: Any, end: Any) -> Tuple[int, int]:
    """Sanitizes and validates start and end bounds for a sequence range.

    Parameters
    ----------
    start : Any
        Starting sequence index (0-indexed).
    end : Any
        Ending sequence index (inclusive).

    Returns
    -------
    tuple of (int, int)
        Sanitized (start, end) integer bounds.

    Raises
    ------
    InvalidInputError
        If start or end are not valid integers.
    NegativeBoundError
        If start or end are negative.
    RangeBoundError
        If start > end.
    """
    clean_start = sanitize_integer(start, param_name="start_bound", allow_negative=False)
    clean_end = sanitize_integer(end, param_name="end_bound", allow_negative=False)

    if clean_start > clean_end:
        raise RangeBoundError(
            f"Start bound ({clean_start}) cannot be greater than end bound ({clean_end}).",
            details={"start": clean_start, "end": clean_end},
        )

    return clean_start, clean_end
