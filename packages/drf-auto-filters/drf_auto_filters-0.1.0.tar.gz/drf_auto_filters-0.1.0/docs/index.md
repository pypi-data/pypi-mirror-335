# DRF Auto Filters Documentation

## Introduction

DRF Auto Filters simplifies filtering in Django REST Framework by automatically generating and integrating in Swagger UI appropriate filters based on your model field types. It eliminates the need to manually create filter classes while providing a rich set of filtering capabilities out of the box.

## Core Concepts

DRF Auto Filters works by:

1. Analyzing your model fields
2. Determining the appropriate filter types for each field
3. Generating a FilterSet class with all the necessary filters
4. Making these filters available through the Django REST Framework API

The library provides appropriate filters for each field type:

| Field Type | Available Filters |
|------------|-------------------|
| Text (CharField, TextField) | exact, case-insensitive exact, contains, case-insensitive contains, starts with, ends with |
| Numeric (IntegerField, FloatField, DecimalField) | exact, minimum, maximum |
| Date (DateField) | exact, after, before |
| DateTime (DateTimeField) | exact, after, before |
| Boolean (BooleanField) | true/false |
| ForeignKey | ID-based filtering |
| ManyToMany | contains related objects |

## Table of Contents

- [Installation](installation.md) - Getting started with DRF Auto Filters
- [Usage](usage.md) - Basic and advanced usage examples
- [Extending](extending.md) - Customizing and extending the functionality

## Example Application

Here's a complete example of using DRF Auto Filters in a Django project:

```python
# models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    
class Genre(models.Model):
    name = models.CharField(max_length=50)
    
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genre)
    publication_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_bestseller = models.BooleanField(default=False)

# serializers.py
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

# views.py
from rest_framework import viewsets
from drf_auto_filters import AutoFilterBackend, swagger_auto_schema_with_filters
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [AutoFilterBackend]
    
    @swagger_auto_schema_with_filters()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

With this setup, your API will automatically support a wide range of filters without any additional configuration.