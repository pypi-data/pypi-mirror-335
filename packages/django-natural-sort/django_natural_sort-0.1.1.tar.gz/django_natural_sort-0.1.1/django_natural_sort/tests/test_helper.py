from django.test import TransactionTestCase

from django_natural_sort.helper import DjangoModelHelper
from sampleapp.models import TestModel


class DjangoModelHelperTests(TransactionTestCase):
    def test_get_string_field_names(self):
        """Test identification of string fields in querysets."""
        # Basic queryset
        queryset = TestModel.objects.all()
        string_fields = DjangoModelHelper.get_string_field_names(queryset)
        self.assertEqual(string_fields, {"name"})

        # With annotated string field
        from django.db.models import CharField, Value

        queryset = TestModel.objects.annotate(
            text_field=Value("text", output_field=CharField())
        )
        string_fields = DjangoModelHelper.get_string_field_names(queryset)
        self.assertEqual(string_fields, {"name", "text_field"})

        # Edge case: empty queryset
        self.assertEqual(
            DjangoModelHelper.get_string_field_names(TestModel.objects.none()),
            {"name"}
        )
