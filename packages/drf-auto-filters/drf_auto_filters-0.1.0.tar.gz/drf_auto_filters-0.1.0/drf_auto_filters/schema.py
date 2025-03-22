"""
Schema generation utilities for integrating with drf-yasg.
"""
from functools import wraps
from typing import Dict, List, Optional, Type

from django_filters import rest_framework as django_filters
from rest_framework.views import APIView

from .filters import AutoFilterBackend


class SwaggerAutoSchemaGenerator:
    """
    Enhances DRF YASG schema generation with auto-generated filter documentation.
    """
    
    @staticmethod
    def get_filter_parameters(filter_class) -> List:
        """
        Extract filter parameters from a filter class for Swagger documentation.
        """
        try:
            from drf_yasg import openapi
        except ImportError:
            return []
            
        parameters = []
        
        # Get all filter fields
        filter_fields = {name: field for name, field in filter_class.__dict__.items() 
                       if isinstance(field, django_filters.Filter)}
        
        for name, field in filter_fields.items():
            parameter = openapi.Parameter(
                name=name,
                in_=openapi.IN_QUERY,
                description=getattr(field, 'help_text', f'Filter by {name}'),
                type=openapi.TYPE_STRING,
                required=False
            )
            parameters.append(parameter)
            
        return parameters
    
    @classmethod
    def enhance_schema_with_filters(cls, view, original_schema: Dict) -> Dict:
        """
        Enhance a schema with filter parameters.
        """
        if not original_schema:
            return original_schema
            
        if hasattr(view, 'filter_backends') and AutoFilterBackend in view.filter_backends:
            # Get the filter class
            filter_class = AutoFilterBackend().get_filterset_class(view)
            
            if filter_class:
                # Get filter parameters
                filter_parameters = cls.get_filter_parameters(filter_class)
                
                # Add filter parameters to manual_parameters
                manual_parameters = original_schema.get('manual_parameters', [])
                manual_parameters.extend(filter_parameters)
                
                # Update schema
                original_schema['manual_parameters'] = manual_parameters
                
        return original_schema


def swagger_auto_schema_with_filters(**kwargs):
    """
    Decorator that enhances swagger_auto_schema with auto-generated filter documentation.
    """
    try:
        from drf_yasg.utils import swagger_auto_schema
    except ImportError:
        # If drf_yasg is not installed, return a no-op decorator
        def noop_decorator(func):
            return func
        return noop_decorator
    
    def decorator(view_method):
        # Apply the standard swagger_auto_schema decorator
        decorated_view = swagger_auto_schema(**kwargs)(view_method)
        
        # Get the view instance if this is a method
        view_instance = None
        if hasattr(view_method, '__self__'):
            view_instance = view_method.__self__
        
        # Get the original schema
        original_schema = getattr(decorated_view, '_swagger_auto_schema', {})
        
        # Enhance the schema with filter parameters
        enhanced_schema = SwaggerAutoSchemaGenerator.enhance_schema_with_filters(
            view_instance,
            original_schema
        )
        
        # Update the decorated view with the enhanced schema
        setattr(decorated_view, '_swagger_auto_schema', enhanced_schema)
        
        return decorated_view
    
    return decorator