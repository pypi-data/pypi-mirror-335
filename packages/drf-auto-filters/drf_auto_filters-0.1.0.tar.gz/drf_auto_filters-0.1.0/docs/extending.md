# Extending DRF Auto Filters

DRF Auto Filters is designed to be highly extensible. Here are several ways to customize its behavior to meet your specific requirements.

## Creating Custom Filter Configurations

You can customize the filters generated for specific field types by subclassing `ModelFieldMapping`:

```python
from drf_auto_filters import ModelFieldMapping, FilterConfig
from django_filters import rest_framework as django_filters

class CustomModelFieldMapping(ModelFieldMapping):
    @staticmethod
    def get_text_filters():
        # Start with the default text filters
        filters = ModelFieldMapping.get_text_filters()
        
        # Add a custom regex filter
        filters['regex'] = FilterConfig(
            lookup_expr='regex',
            field_class=django_filters.CharFilter,
            label='Regex match',
            help_text='Filter by regex pattern'
        )
        
        # Remove a filter you don't want
        if 'endswith' in filters:
            del filters['endswith']
            
        return filters
```

## Creating a Custom Filter Set

Extend the `AutoFilterSet` class to add global filters or modify the filter generation process:

```python
from drf_auto_filters import AutoFilterSet
from django_filters import rest_framework as django_filters

class CustomAutoFilterSet(AutoFilterSet):
    @classmethod
    def generate_filters(cls, model_class, field_names=None):
        # Get the default filters
        filters = super().generate_filters(model_class, field_names)
        
        # Add a custom global search filter
        filters['search'] = django_filters.CharFilter(
            method='filter_search',
            label='Global search',
            help_text='Search across multiple text fields'
        )
        
        return filters
        
    def filter_search(self, queryset, name, value):
        # Implement custom search logic
        return queryset.filter(title__icontains=value) | queryset.filter(description__icontains=value)
```

## Creating a Custom Filter Backend

Create a custom filter backend by subclassing `AutoFilterBackend`:

```python
from drf_auto_filters import AutoFilterBackend

class CustomFilterBackend(AutoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        # Use custom logic to determine the filter set class
        if hasattr(view, 'custom_filterset_class'):
            return view.custom_filterset_class
            
        # Use a custom mapping for certain models
        model = queryset.model
        if model.__name__ == 'SpecialModel':
            return SpecialModelFilterSet
            
        # Fall back to the default behavior
        return super().get_filterset_class(view, queryset)
```

## Customizing Swagger Schema Generation

Customize the Swagger documentation generation by extending `SwaggerAutoSchemaGenerator`:

```python
from drf_auto_filters.schema import SwaggerAutoSchemaGenerator
from drf_yasg import openapi

class CustomSwaggerAutoSchemaGenerator(SwaggerAutoSchemaGenerator):
    @staticmethod
    def get_filter_parameters(filter_class):
        # Get the default parameters
        parameters = SwaggerAutoSchemaGenerator.get_filter_parameters(filter_class)
        
        # Enhance documentation for specific parameters
        for param in parameters:
            # Add examples for date filters
            if param.name.endswith('_after') or param.name.endswith('_before'):
                param.example = '2023-01-01'
                
            # Add more descriptive help text
            if 'partial' in param.name:
                param.description = f"{param.description} - Use this for flexible text searching"
            
        return parameters
```

## Example: Model-Specific Custom Filters

Here's a complete example of creating custom filters for a specific model:

```python
from drf_auto_filters import AutoFilterSet, AutoFilterBackend
from django_filters import rest_framework as django_filters
from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer

# Create a custom filter set for the Book model
class BookFilterSet(AutoFilterSet):
    # Add a custom filter for filtering by publication year
    publication_year = django_filters.NumberFilter(
        field_name='publication_date',
        lookup_expr='year',
        label='Publication Year',
        help_text='Filter by the year of publication'
    )
    
    # Add a custom price range filter
    price_range = django_filters.RangeFilter(
        field_name='price',
        label='Price Range',
        help_text='Filter by price range (min-max)'
    )
    
    # Add a custom method filter
    is_recent = django_filters.BooleanFilter(
        method='filter_recent',
        label='Recent Books',
        help_text='Filter for books published in the last year'
    )
    
    def filter_recent(self, queryset, name, value):
        from django.utils import timezone
        import datetime
        
        if value:
            one_year_ago = timezone.now().date() - datetime.timedelta(days=365)
            return queryset.filter(publication_date__gte=one_year_ago)
        return queryset
    
    class Meta:
        model = Book
        # Include both auto-generated filters and our custom filters
        fields = list(AutoFilterSet.generate_filters(Book).keys()) + [
            'publication_year',
            'price_range',
            'is_recent'
        ]

# Use the custom filter set in a viewset
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [AutoFilterBackend]
    filterset_class = BookFilterSet
```

With this setup, your API will have both the automatically generated filters for all fields in the Book model, plus the custom filters you've defined.

## Advanced: Completely Replace the Filter Generation Logic

If you need to completely customize how filters are generated, you can override the core methods:

```python
from drf_auto_filters import AutoFilterSet, ModelFieldMapping
from django.db import models

class CompletelyCustomFilterSet(AutoFilterSet):
    @classmethod
    def generate_filters(cls, model_class, field_names=None):
        # Start with an empty dict instead of using the parent method
        filters = {}
        
        # Get model fields (with your own logic)
        model_fields = [f for f in model_class._meta.get_fields() 
                       if not f.auto_created and hasattr(f, 'name')]
        
        # Apply your custom filter generation logic
        for field in model_fields:
            if field_names is not None and field.name not in field_names:
                continue
                
            # Your custom filter generation logic here...
            if isinstance(field, models.CharField):
                # Create only the filters you want for text fields
                # ...
            
        return filters
```

By extending DRF Auto Filters in these ways, you can tailor its behavior to perfectly match your project's requirements while still benefiting from the automatic filter generation infrastructure.