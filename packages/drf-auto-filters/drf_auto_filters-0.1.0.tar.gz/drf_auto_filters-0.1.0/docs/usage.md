# Usage Guide

## Basic Usage

Using DRF Auto Filters is straightforward:

```python
from rest_framework import viewsets
from drf_auto_filters import AutoFilterBackend
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    filter_backends = [AutoFilterBackend]
```

With this minimal setup, DRF Auto Filters automatically generates appropriate filters for all fields in your model.

## Available Filter Types by Field Type

### Text Fields (CharField, TextField)

For text fields like `name = models.CharField(max_length=100)`:

| Filter Suffix | Lookup | Description | Example URL |
|---------------|--------|-------------|-------------|
| `_exact` | `exact` | Exact match (case-sensitive) | `/api/models/?name_exact=Test` |
| `_iexact` | `iexact` | Exact match (case-insensitive) | `/api/models/?name_iexact=test` |
| `_contains` | `contains` | Contains (case-sensitive) | `/api/models/?name_contains=es` |
| `_partial` | `icontains` | Contains (case-insensitive) | `/api/models/?name_partial=es` |
| `_startswith` | `istartswith` | Starts with (case-insensitive) | `/api/models/?name_startswith=te` |
| `_endswith` | `iendswith` | Ends with (case-insensitive) | `/api/models/?name_endswith=st` |

### Numeric Fields (IntegerField, FloatField, DecimalField)

For numeric fields like `price = models.DecimalField(max_digits=6, decimal_places=2)`:

| Filter Suffix | Lookup | Description | Example URL |
|---------------|--------|-------------|-------------|
| `_exact` | `exact` | Exact match | `/api/models/?price_exact=19.99` |
| `_min` | `gte` | Minimum value (inclusive) | `/api/models/?price_min=10.00` |
| `_max` | `lte` | Maximum value (inclusive) | `/api/models/?price_max=20.00` |

### Date Fields (DateField)

For date fields like `created_date = models.DateField()`:

| Filter Suffix | Lookup | Description | Example URL |
|---------------|--------|-------------|-------------|
| `_exact` | `exact` | Exact date | `/api/models/?created_date_exact=2023-01-01` |
| `_after` | `gte` | After date (inclusive) | `/api/models/?created_date_after=2023-01-01` |
| `_before` | `lte` | Before date (inclusive) | `/api/models/?created_date_before=2023-12-31` |

### DateTime Fields (DateTimeField)

For datetime fields like `created_at = models.DateTimeField()`:

| Filter Suffix | Lookup | Description | Example URL |
|---------------|--------|-------------|-------------|
| `_exact` | `exact` | Exact datetime | `/api/models/?created_at_exact=2023-01-01T12:00:00Z` |
| `_after` | `gte` | After datetime (inclusive) | `/api/models/?created_at_after=2023-01-01T00:00:00Z` |
| `_before` | `lte` | Before datetime (inclusive) | `/api/models/?created_at_before=2023-12-31T23:59:59Z` |

### Boolean Fields (BooleanField)

For boolean fields like `is_active = models.BooleanField(default=True)`:

| Filter Name | Lookup | Description | Example URL |
|-------------|--------|-------------|-------------|
| field name as-is | `exact` | Boolean value | `/api/models/?is_active=true` |

### Foreign Key Fields (ForeignKey, OneToOneField)

For foreign key fields like `author = models.ForeignKey(Author, on_delete=models.CASCADE)`:

| Filter Suffix | Lookup | Description | Example URL |
|---------------|--------|-------------|-------------|
| `_id` | `exact` | Foreign key ID | `/api/models/?author_id=1` |

### Many-to-Many Fields (ManyToManyField)

For many-to-many fields like `tags = models.ManyToManyField(Tag)`:

| Filter Suffix | Description | Example URL |
|---------------|-------------|-------------|
| `_contains` | Contains related objects | `/api/models/?tags_contains=1,2,3` |

## Limiting Fields for Filtering

You can limit which fields get filters by adding a `filter_set_fields` attribute to your view:

```python
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [AutoFilterBackend]
    filter_set_fields = ['title', 'author', 'publication_date']  # Only these fields will have filters
```

This is useful for improving performance and reducing clutter in your API.

## Swagger Documentation Integration

To include auto-generated filters in your Swagger documentation, use the `swagger_auto_schema_with_filters` decorator:

```python
from drf_auto_filters import AutoFilterBackend, swagger_auto_schema_with_filters

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [AutoFilterBackend]
    
    @swagger_auto_schema_with_filters()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
```

This will document all available filters in your Swagger UI, making your API more discoverable and user-friendly.

## Combining with Other Filter Backends

DRF Auto Filters can be combined with other DRF filter backends:

```python
from rest_framework import viewsets, filters
from drf_auto_filters import AutoFilterBackend

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [
        AutoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_date', 'price']
```

This gives you the power of automatic field-specific filtering along with search and ordering capabilities.