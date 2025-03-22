# Installation Guide

## Requirements

DRF Auto Filters requires:

- Python (3.8, 3.9, 3.10, 3.11)
- Django (3.2, 4.0, 4.1, 4.2)
- Django REST Framework (3.12+)
- django-filter (22.1+)

For Swagger documentation integration:
- drf-yasg (1.20+)

## Installation Steps

### 1. Install the Package

```bash
pip install drf-auto-filters
```

### 2. Add Required Apps to INSTALLED_APPS

In your Django settings (`settings.py`):

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
    'drf_auto_filters',
    # ...
]
```

### 3. Optional: Install and Configure drf-yasg for Swagger Documentation

If you want to use the Swagger documentation integration:

```bash
pip install drf-yasg
```

And add it to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'drf_yasg',
    # ...
]
```

### 4. Optional: Configure Default Filter Backends

If you want to use Django Filter Backend as the default for all your API views:

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    # ... other settings
}
```

Note that this isn't required to use DRF Auto Filters, as you can also apply the filter backend selectively to specific views.

## Verification

To verify that DRF Auto Filters is correctly installed, you can create a simple view and check that it generates the appropriate filters:

```python
from rest_framework import viewsets
from drf_auto_filters import AutoFilterBackend
from .models import YourModel
from .serializers import YourModelSerializer

class TestViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    filter_backends = [AutoFilterBackend]
```

After setting up URL routing for this viewset, you should be able to use filter parameters in your API requests based on the fields in your model.