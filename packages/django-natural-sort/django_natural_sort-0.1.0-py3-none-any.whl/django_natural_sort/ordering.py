"""
Django Natural Sort - A package for natural sorting in Django and Django REST Framework
"""

import re
from functools import cmp_to_key
from typing import Any, List


# Core natural sorting logic (standalone for reusability)
def parse_int_key(text: str) -> List[Any]:
    """
    Convert string with embedded numbers to list of string and number chunks.

    Args:
        text: The input string to parse.

    Returns:
        List of mixed types (int for numbers, str for non-numbers).

    Example:
        >>> parse_int_key("z23a")
        ['z', 23, 'a']
    """
    if not isinstance(text, str):
        return text
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.findall(r"[a-zA-Z]+|\d+", text)
    ]


def compare_values(x: Any, y: Any) -> int:
    """
    Compare two values with special handling for strings and booleans.
    Numbers are prioritized over strings in mixed-type comparisons.

    Args:
        x: First value to compare.
        y: Second value to compare.

    Returns:
        -1 if x < y, 0 if x == y, 1 if x > y.
    """
    # Handle None values
    if x is None and y is None:
        return 0
    if x is None:
        return -1
    if y is None:
        return 1

    # Natural string comparison
    if isinstance(x, str) and isinstance(y, str):
        x_key = parse_int_key(x)
        y_key = parse_int_key(y)

        # Compare chunk by chunk
        for x_part, y_part in zip(x_key, y_key):
            if type(x_part) is type(y_part):
                if x_part != y_part:
                    return -1 if x_part < y_part else 1
            elif isinstance(x_part, int):
                return -1  # Number comes before string
            else:
                return 1  # String comes after number

        # If one key is a prefix of the other, shorter comes first
        return -1 if len(x_key) < len(y_key) else (1 if len(x_key) > len(y_key) else 0)

    # Boolean comparison (False before True)
    if isinstance(x, bool) and isinstance(y, bool):
        return -1 if x < y else (1 if x > y else 0)

    # Default comparison
    try:
        return -1 if x < y else (1 if x > y else 0)
    except TypeError:
        # Fall back to string comparison if types can't be compared directly
        return compare_values(str(x), str(y))


def multikey_sort(
    items: List[Any], fields: List[str], strict: bool = False
) -> List[Any]:
    """
    Sort items by multiple fields with natural sort order.

    Args:
        items: List of objects to sort.
        fields: List of field names to sort by, prefixed with '-' for descending.
        strict: If True, raise exceptions for missing fields; otherwise, skip silently.

    Returns:
        Sorted list.

    Example:
        >>> multikey_sort([obj1, obj2], ['name', '-version'])
        [obj2, obj1]  # Assuming obj2.name < obj1.name or obj2.version > obj1.version
    """
    if not items or not fields:
        return items

    # Parse field specifications
    parsed_fields = []
    for field in fields:
        descending = field.startswith("-")
        field_name = field[1:] if descending else field
        parsed_fields.append((field_name, -1 if descending else 1))

    # Create comparison function
    def compare_items(a, b):
        for field_name, direction in parsed_fields:
            try:
                a_val = getattr(a, field_name)
                b_val = getattr(b, field_name)
                result = compare_values(a_val, b_val) * direction
                if result != 0:
                    return result
            except AttributeError:
                if strict:
                    raise ValueError(f"Field '{field_name}' not found")
                continue  # Skip silently in lenient mode
        return 0

    return sorted(items, key=cmp_to_key(compare_items))
