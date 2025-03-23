from typing import Set

from django.db.models import CharField, EmailField, TextField


class DjangoModelHelper:
    """
    Helper class for working with Django models and querysets.
    """

    @staticmethod
    def get_string_field_names(queryset) -> Set[str]:
        """
        Extract field names that should be naturally sorted from a queryset.

        Args:
            queryset: Django queryset to analyze.

        Returns:
            Set of field names that should use natural sort.
        """
        string_fields = set()

        # Check model fields
        for field in queryset.model._meta.get_fields():
            if isinstance(field, (CharField, EmailField, TextField)):
                string_fields.add(field.name)

        # Check annotated fields
        for name, expression in queryset.query.annotations.items():
            if hasattr(expression, "output_field") and isinstance(
                expression.output_field, (CharField, EmailField, TextField)
            ):
                string_fields.add(name)

        return string_fields
