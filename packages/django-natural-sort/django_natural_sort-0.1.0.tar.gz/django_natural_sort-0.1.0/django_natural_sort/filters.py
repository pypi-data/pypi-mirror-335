
from rest_framework.filters import OrderingFilter

from .backend import NaturalOrderingBackend
from .helper import DjangoModelHelper


class NaturalOrderingFilter(OrderingFilter):
    """
    Django REST Framework filter that applies natural sorting to string fields.

    Usage:
        class MyViewSet(viewsets.ModelViewSet):
            filter_backends = [NaturalOrderingFilter]
            ordering_fields = ['id', 'name', 'version']
    """

    def get_ordering(self, request, queryset, view):
        """
        Get the ordering fields for the request.
        """
        ordering = super().get_ordering(request, queryset, view)

        # Default to the model's ordering attribute if ordering is not specified
        if ordering is None and hasattr(queryset.model._meta, "ordering"):
            return queryset.model._meta.ordering

        return ordering

    def filter_queryset(self, request, queryset, view):
        """
        Apply sorting to the queryset.
        """
        ordering = self.get_ordering(request, queryset, view)

        if not ordering:
            return queryset

        # Get field names without direction prefix
        clean_ordering = [field.lstrip("-") for field in ordering]

        # Get all string fields in the queryset that should use natural sort
        string_fields = DjangoModelHelper.get_string_field_names(queryset)

        # Check if any ordering fields are string fields
        needs_natural_sort = (
            any(field in string_fields for field in clean_ordering)
        )

        if needs_natural_sort:
            # For natural sort, convert to list and sort in Python
            queryset_list = list(queryset)
            return NaturalOrderingBackend.multikey_sort(queryset_list, ordering)
        else:
            # For non-string fields, use the database's built-in ordering
            return queryset.order_by(*ordering)
