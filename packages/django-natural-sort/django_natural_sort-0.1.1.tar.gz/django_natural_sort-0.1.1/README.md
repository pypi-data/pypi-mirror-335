# Django Natural Sort

![PyPI](https://img.shields.io/pypi/v/django-natural-sort)
![PyPI - License](https://img.shields.io/pypi/l/django-natural-sort)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-natural-sort)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-natural-sort)

A  lightweight, efficient package for natural sorting in Django and Django REST Framework.

## The Problem

By default, when you order strings containing numbers in Django or DRF, they're sorted lexicographically:

```
['1', '10', '11', '12', '2', '3', '4', '5', '6', '7', '8', '9']
```

This is not the expected order for humans, who would expect:

```
['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
```

This package solves this issue by implementing natural sorting, where numbers within strings are treated as actual numbers rather than individual characters.

## Installation

```bash
pip install django-natural-sort
```

## Usage

### In Django REST Framework Views

```python
from django_natural_sort.filters import NaturalOrderingFilter

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    filter_backends = [NaturalOrderingFilter]
    ordering_fields = ['id', 'name', 'version']
```

This automatically applies natural sorting to any `CharField`, `EmailField`, or `TextField` in your model when used in ordering. Just use the standard ordering parameter:

```
GET /api/mymodel/?ordering=version
```

## Features

- **Efficient**: Uses database ordering for non-string fields, only falls back to Python sorting when necessary
- **Compatible**: Works with Django 3.2+ and Django REST Framework 3.11.1+
- **Lightweight**: No external dependencies
- **Flexible**: Works with various string field types (CharField, TextField, EmailField)
- **Robust**: Handles edge cases like mixed types, None values, and more

## How It Works

The package detects which fields in your model are string fields. When ordering by these fields, it uses a natural sorting algorithm that correctly handles numbers embedded in strings.

For non-string fields, it uses the database's built-in ordering mechanism for optimal performance.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
