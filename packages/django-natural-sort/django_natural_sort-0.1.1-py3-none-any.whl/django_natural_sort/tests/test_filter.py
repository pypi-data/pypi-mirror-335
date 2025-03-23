from django.db import models
from django.test import TransactionTestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from django_natural_sort.filters import NaturalOrderingFilter
from django_natural_sort.tests.factories import TestModelFactory
from sampleapp.models import TestModel


class NaturalOrderingFilterTests(TransactionTestCase):
    def setUpTestData(self, names):
        for index, name in enumerate(names):
            TestModelFactory(name=name, number=index + 1)

    def setUp(self):
        self.filter = NaturalOrderingFilter()
        self.factory = APIRequestFactory()
        # Create a mock view with ordering_fields
        self.mock_view = type("MockView", (), {"ordering_fields": ["name", "number"]})()

    def test_get_ordering(self):
        """Test extraction of ordering parameters."""
        # Test data
        self.setUpTestData(["item10", "item2", "item1"])
        # Ordering from request
        django_request = self.factory.get("/", {"ordering": "name,-number"})
        request = Request(django_request)  # Wrap with DRF Request
        queryset = TestModel.objects.all()
        ordering = self.filter.get_ordering(request, queryset, view=self.mock_view)
        self.assertEqual(ordering, ["name", "-number"])

        # Fallback to model ordering
        class TestModelWithOrdering(models.Model):
            name = models.CharField(max_length=50)

            class Meta:
                ordering = ["name"]
                app_label = "natural_sort"  # Explicitly set app_label

        request = Request(self.factory.get("/"))
        queryset = TestModelWithOrdering.objects.all()
        ordering = self.filter.get_ordering(request, queryset, view=self.mock_view)
        self.assertEqual(ordering, ["name"])

        # Edge case: no ordering specified, no model ordering
        request = Request(self.factory.get("/"))
        ordering = self.filter.get_ordering(
            request, TestModel.objects.all(), view=self.mock_view
        )
        self.assertEqual(ordering, [])

    def test_filter_queryset(self):
        """Test application of natural sorting to querysets."""
        # Test data
        self.setUpTestData(["item10", "item2", "item1"])

        queryset = TestModel.objects.all()
        # Natural sorting on string field
        request = Request(self.factory.get("/", {"ordering": "name"}))
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual([item.name for item in filtered], ["item1", "item2", "item10"])

        # Database ordering on non-string field
        request = Request(self.factory.get("/", {"ordering": "number"}))
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual([item.number for item in filtered], [1, 2, 3])

        # Mixed ordering
        request = Request(self.factory.get("/", {"ordering": "name,-number"}))
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual(
            [item.name for item in filtered], ["item1", "item2", "item10"]
        )  # Unique names

        # Reverse natural sorting
        request = Request(self.factory.get("/", {"ordering": "-name"}))
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual([item.name for item in filtered], ["item10", "item2", "item1"])

        # No ordering
        request = Request(self.factory.get("/"))
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual(list(filtered), list(queryset))

        # Edge case: empty queryset
        request = Request(self.factory.get("/", {"ordering": "name"}))
        filtered = self.filter.filter_queryset(
            request, TestModel.objects.none(), view=self.mock_view
        )
        self.assertEqual(list(filtered), [])

    def test_get_ordering_with_list_of_int(self):
        # Test data
        self.setUpTestData(
            ["1", "10", "11", "12", "2", "3", "4", "5", "6", "7", "8", "9"]
        )
        request = Request(
            self.factory.get("/", {"ordering": "name"})
        )  # Wrap with DRF Request
        queryset = TestModel.objects.all()
        ordering = self.filter.get_ordering(request, queryset, view=self.mock_view)
        self.assertEqual(
            ordering,
            [
                "name",
            ],
        )
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual(
            [item.name for item in filtered],
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        )
        request = Request(
            self.factory.get("/", {"ordering": "-name"})
        )
        ordering = self.filter.get_ordering(request, queryset, view=self.mock_view)
        self.assertEqual(
            ordering,
            [
                "-name",
            ],
        )
        filtered = self.filter.filter_queryset(request, queryset, view=self.mock_view)
        self.assertEqual(
            [item.name for item in filtered],
            ['12', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1'],
        )
