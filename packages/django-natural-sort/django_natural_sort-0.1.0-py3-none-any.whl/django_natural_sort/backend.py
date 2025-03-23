import re
from functools import cmp_to_key
from typing import Any, Callable, List, Optional


class NaturalOrderingBackend:
    """
    Core implementation of natural string sorting logic.
    """

    @staticmethod
    def parse_int_key(text: str) -> List[Any]:
        """
        Convert a string with embedded numbers into a list of
        string and number chunks.

        Args:
            text: The input string to parse.

        Returns:
            A list of mixed types (int for numbers, str for non-numbers).

        Example:
            >>> NaturalOrderingBackend.parse_int_key("z23a")
            ['z', 23, 'a']
        """
        if not isinstance(text, str):
            return text
        return [
            int(c) if c.isdigit()
            else c.lower() for c in re.split(r"(\d+)", text)
        ]

    @staticmethod
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
            x_key = NaturalOrderingBackend.parse_int_key(x)
            y_key = NaturalOrderingBackend.parse_int_key(y)

            # Compare chunk by chunk
            for x_part, y_part in zip(x_key, y_key):
                if type(x_part) is type(y_part):
                    if x_part != y_part:
                        return -1 if x_part < y_part else 1
                elif isinstance(x_part, int):
                    return -1  # Numbers come before strings
                else:
                    return 1  # Strings come after numbers

            # If one key is a prefix of the other, shorter comes first
            return (
                -1 if len(x_key) < len(y_key)
                else (1 if len(x_key) > len(y_key) else 0)
            )

        # Boolean comparison (False before True)
        if isinstance(x, bool) and isinstance(y, bool):
            return -1 if x < y else (1 if x > y else 0)

        # Default comparison
        try:
            return -1 if x < y else (1 if x > y else 0)
        except TypeError:
            # Fall back to string comparison
            # if types can't be compared directly
            return NaturalOrderingBackend.compare_values(str(x), str(y))

    @staticmethod
    def natural_sort(
        items: List[Any],
        key: Optional[Callable[[Any], str]] = None,
        reverse: bool = False,
    ) -> List[Any]:
        """
        Sort a list using natural ordering (e.g., 'file2' before 'file10').

        Args:
            items: List of items to sort.
            key: Optional function to extract a string from each item.
            reverse: If True, sort in descending order.

        Returns:
            Sorted list.

        Example:
            >>> NaturalOrderingBackend.natural_sort(['file10', 'file2', 'file1'])
            ['file1', 'file2', 'file10']
        """

        def key_func(item):
            return NaturalOrderingBackend.parse_int_key(key(item) if key else item)

        return sorted(items, key=key_func, reverse=reverse)

    @staticmethod
    def multikey_sort(items: List[Any], fields: List[str]) -> List[Any]:
        """
        Sort items by multiple fields with natural sort order.

        Args:
            items: List of objects to sort.
            fields: List of field names to sort by, 
                    prefixed with '-' for descending.

        Returns:
            Sorted list.
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
                    result = (
                        NaturalOrderingBackend.compare_values(a_val, b_val)
                        * direction
                    )
                    if result != 0:
                        return result
                except AttributeError:
                    pass  # Skip fields that don’t exist
            return 0

        return sorted(items, key=cmp_to_key(compare_items))
