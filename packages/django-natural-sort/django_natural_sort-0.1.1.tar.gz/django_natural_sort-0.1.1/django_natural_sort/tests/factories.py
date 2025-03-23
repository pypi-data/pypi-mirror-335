import factory
from factory.django import DjangoModelFactory

from sampleapp.models import TestModel


class TestModelFactory(DjangoModelFactory):
    class Meta:
        model = TestModel

    name = factory.Sequence(lambda n: f"Test Name {n}")
    number = factory.Faker(
        "pyfloat", left_digits=1, right_digits=2, positive=True, max_value=10
    )
