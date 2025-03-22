"""
DRF Auto Filters - Automatic filter generation for Django Rest Framework.
"""

__version__ = "0.1.0"


def _lazy_import():
    from .filters import (
        AutoFilterBackend,
        AutoFilterSet,
        FilterConfig,
        ModelFieldMapping,
    )
    from .schema import swagger_auto_schema_with_filters
    
    return {
        "AutoFilterBackend": AutoFilterBackend,
        "AutoFilterSet": AutoFilterSet,
        "FilterConfig": FilterConfig,
        "ModelFieldMapping": ModelFieldMapping,
        "swagger_auto_schema_with_filters": swagger_auto_schema_with_filters,
    }


__all__ = [
    "AutoFilterBackend",
    "AutoFilterSet",
    "FilterConfig",
    "ModelFieldMapping",
    "swagger_auto_schema_with_filters",
]