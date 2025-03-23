import os

from setuptools import find_packages, setup

# Read the contents of README.md
with open(
    os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8"
) as f:
    long_description = f.read()

setup(
    name="django-natural-sort",
    version="0.1.1",
    author="Lekan Akindele",
    author_email="lekan.akindele12@gmail.com",
    description="Natural sorting for Django and Django REST Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akindele214/django-natural-sort",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.9.0",
    ],
    keywords="django, drf, natural sort, sorting, ordering",
    project_urls={
        "Bug Tracker": "https://github.com/akindele214/django-natural-sort/issues",
        "Documentation": "https://github.com/akindele214/django-natural-sort",
        "Source Code": "https://github.com/akindele214/django-natural-sort",
    },
)
