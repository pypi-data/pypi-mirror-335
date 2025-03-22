"""
Core filter implementation for auto-generating filters based on model field types.
"""
from dataclasses import dataclass
from typing import Dict, List, Type, Set, Optional

from django.db import models
from django.db.models.fields import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    FloatField,
    IntegerField,
    TextField,
)
from django.db.models.fields.related import (
    ForeignKey,
    ManyToManyField,
    OneToOneField,
)
from django_filters import rest_framework as django_filters
from rest_framework.exceptions import ValidationError


@dataclass
class FilterConfig:
    """Configuration for a filter field."""
    lookup_expr: str
    field_class: Type[django_filters.Filter]
    label: str
    help_text: str


class ModelFieldMapping:
    """Maps model field types to their corresponding filter configurations."""
    
    @staticmethod
    def get_text_filters() -> Dict[str, FilterConfig]:
        return {
            'exact': FilterConfig(
                lookup_expr='exact',
                field_class=django_filters.CharFilter,
                label='Exact match',
                help_text='Filter by exact text match'
            ),
            'iexact': FilterConfig(
                lookup_expr='iexact',
                field_class=django_filters.CharFilter,
                label='Exact match (case insensitive)',
                help_text='Filter by exact text match (case insensitive)'
            ),
            'contains': FilterConfig(
                lookup_expr='contains',
                field_class=django_filters.CharFilter,
                label='Contains',
                help_text='Filter by partial text match'
            ),
            'partial': FilterConfig(
                lookup_expr='icontains',
                field_class=django_filters.CharFilter,
                label='Contains (case insensitive)',
                help_text='Filter by partial text match (case insensitive)'
            ),
            'startswith': FilterConfig(
                lookup_expr='istartswith',
                field_class=django_filters.CharFilter,
                label='Starts with',
                help_text='Filter by text starting with (case insensitive)'
            ),
            'endswith': FilterConfig(
                lookup_expr='iendswith',
                field_class=django_filters.CharFilter,
                label='Ends with',
                help_text='Filter by text ending with (case insensitive)'
            ),
        }
    
    @staticmethod
    def get_numeric_filters() -> Dict[str, FilterConfig]:
        return {
            'exact': FilterConfig(
                lookup_expr='exact',
                field_class=django_filters.NumberFilter,
                label='Exact match',
                help_text='Filter by exact numeric value'
            ),
            'min': FilterConfig(
                lookup_expr='gte',
                field_class=django_filters.NumberFilter,
                label='Minimum',
                help_text='Filter by minimum value (inclusive)'
            ),
            'max': FilterConfig(
                lookup_expr='lte',
                field_class=django_filters.NumberFilter,
                label='Maximum',
                help_text='Filter by maximum value (inclusive)'
            ),
        }
    
    @staticmethod
    def get_date_filters() -> Dict[str, FilterConfig]:
        return {
            'exact': FilterConfig(
                lookup_expr='exact',
                field_class=django_filters.DateFilter,
                label='Exact date',
                help_text='Filter by exact date'
            ),
            'after': FilterConfig(
                lookup_expr='gte',
                field_class=django_filters.DateFilter,
                label='After date',
                help_text='Filter by date after (inclusive)'
            ),
            'before': FilterConfig(
                lookup_expr='lte',
                field_class=django_filters.DateFilter,
                label='Before date',
                help_text='Filter by date before (inclusive)'
            ),
        }
    
    @staticmethod
    def get_datetime_filters() -> Dict[str, FilterConfig]:
        return {
            'exact': FilterConfig(
                lookup_expr='exact',
                field_class=django_filters.DateTimeFilter,
                label='Exact datetime',
                help_text='Filter by exact datetime'
            ),
            'after': FilterConfig(
                lookup_expr='gte',
                field_class=django_filters.DateTimeFilter,
                label='After datetime',
                help_text='Filter by datetime after (inclusive)'
            ),
            'before': FilterConfig(
                lookup_expr='lte',
                field_class=django_filters.DateTimeFilter,
                label='Before datetime',
                help_text='Filter by datetime before (inclusive)'
            ),
        }
    
    @staticmethod
    def get_boolean_filters() -> Dict[str, FilterConfig]:
        return {
            '': FilterConfig(
                lookup_expr='exact',
                field_class=django_filters.BooleanFilter,
                label='Boolean value',
                help_text='Filter by boolean value (true/false)'
            ),
        }
    
    @staticmethod
    def get_foreignkey_filters() -> Dict[str, FilterConfig]:
        return {
            'id': FilterConfig(
                lookup_expr='exact',
                field_class=django_filters.NumberFilter,
                label='Foreign key ID',
                help_text='Filter by foreign key ID'
            ),
        }
    
    @staticmethod
    def get_manytomany_filters() -> Dict[str, FilterConfig]:
        return {
            'contains': FilterConfig(
                lookup_expr='',  # Special handling in filter set creation
                field_class=django_filters.ModelMultipleChoiceFilter,
                label='Contains',
                help_text='Filter by related object'
            ),
        }
    
    @classmethod
    def get_field_filters(cls, field: models.Field) -> Dict[str, FilterConfig]:
        """Get appropriate filters for a given model field."""
        if isinstance(field, (CharField, TextField)):
            return cls.get_text_filters()
        elif isinstance(field, (IntegerField, FloatField, DecimalField)):
            return cls.get_numeric_filters()
        elif isinstance(field, DateField):
            return cls.get_date_filters()
        elif isinstance(field, DateTimeField):
            return cls.get_datetime_filters()
        elif isinstance(field, BooleanField):
            return cls.get_boolean_filters()
        elif isinstance(field, (ForeignKey, OneToOneField)):
            return cls.get_foreignkey_filters()
        elif isinstance(field, ManyToManyField):
            return cls.get_manytomany_filters()
        else:
            # Default to exact match only for unrecognized fields
            return {
                'exact': FilterConfig(
                    lookup_expr='exact',
                    field_class=django_filters.CharFilter,
                    label=f'Exact match for {field.__class__.__name__}',
                    help_text=f'Filter by exact match for this {field.__class__.__name__} field'
                ),
            }


class AutoFilterSet(django_filters.FilterSet):
    """
    A FilterSet class that automatically generates filters based on model fields.
    """
    
    @classmethod
    def generate_filters(cls, model_class: Type[models.Model], field_names: Optional[List[str]] = None) -> Dict[str, django_filters.Filter]:
        """
        Generate filter fields for a model class.
        
        Args:
            model_class: The model class to generate filters for
            field_names: Optional list of field names to generate filters for.
                         If provided, only these fields will have filters.
        """
        filters = {}
        
        # Get all model fields
        model_fields = model_class._meta.get_fields()
        model_field_names = {field.name for field in model_fields if hasattr(field, 'name')}
        
        # If field_names is provided, validate that all fields exist on the model
        if field_names is not None:
            invalid_fields = set(field_names) - model_field_names
            if invalid_fields:
                raise ValidationError(
                    f"Invalid field(s) in filter_set_fields: {', '.join(invalid_fields)}. "
                    f"Valid fields are: {', '.join(sorted(model_field_names))}"
                )
        
        # Process each field
        for field in model_fields:
            # Skip auto-created fields like id
            if getattr(field, 'auto_created', False):
                continue
                
            # Skip many-to-one relationships (reverse ForeignKey)
            if getattr(field, 'one_to_many', False):
                continue
            
            # Skip fields not in field_names if field_names is provided
            if field_names is not None and field.name not in field_names:
                continue
                
            # Handle different field types
            if hasattr(field, 'get_internal_type'):
                # Standard model fields with get_internal_type
                field_name = field.name
                field_filters = ModelFieldMapping.get_field_filters(field)
                
                # Get a readable field name
                verbose_name = getattr(field, 'verbose_name', field_name)
                
                for suffix, filter_config in field_filters.items():
                    filter_name = f"{field_name}_{suffix}" if suffix else field_name
                    
                    # Create a label that includes the field name
                    if suffix:
                        label = f"{verbose_name.capitalize()} - {filter_config.label}"
                    else:
                        label = f"{verbose_name.capitalize()}"
                    
                    # Update help text to include field name
                    help_text = filter_config.help_text.replace('Filter by', f'Filter {verbose_name} by')
                    
                    if isinstance(field, ManyToManyField) and suffix == 'contains':
                        # Special handling for many-to-many relationships
                        filters[filter_name] = filter_config.field_class(
                            field_name=field_name,
                            queryset=field.related_model.objects.all(),
                            label=label,
                            help_text=help_text
                        )
                    else:
                        # Standard filter
                        if filter_config.lookup_expr:
                            filters[filter_name] = filter_config.field_class(
                                field_name=field_name,
                                lookup_expr=filter_config.lookup_expr,
                                label=label,
                                help_text=help_text
                            )
                        else:
                            filters[filter_name] = filter_config.field_class(
                                field_name=field_name,
                                label=label,
                                help_text=help_text
                            )
        
        return filters

    @classmethod
    def get_filter_class_for_model(cls, model_class: Type[models.Model], field_names: Optional[List[str]] = None) -> Type['AutoFilterSet']:
        """
        Create a FilterSet class for a specific model class with auto-generated filters.
        
        Args:
            model_class: The model class to create filters for
            field_names: Optional list of field names to generate filters for
        """
        
        # Generate filter fields
        filter_fields = cls.generate_filters(model_class, field_names)
        
        # Create a new FilterSet class for this model
        attrs = {
            'Meta': type('Meta', (), {
                'model': model_class,
                'fields': list(filter_fields.keys()),
            }),
            **filter_fields
        }
        
        return type(f'{model_class.__name__}AutoFilterSet', (cls,), attrs)


class AutoFilterBackend(django_filters.DjangoFilterBackend):
    """
    A filter backend that automatically creates filters based on model fields.
    
    To limit which fields get filters, add a filter_set_fields attribute to your view:
    
    class MyModelViewSet(viewsets.ModelViewSet):
        queryset = MyModel.objects.all()
        filter_backends = [AutoFilterBackend]
        filter_set_fields = ['name', 'status', 'created_at']  # Only these fields will have filters
    """
    
    def get_filterset_class(self, view, queryset=None):
        """
        Return the filterset class to use for the given view and queryset.
        """
        # Check if the view has a custom filterset_class defined
        if hasattr(view, 'filterset_class'):
            return view.filterset_class
        
        # Get the model class from the queryset
        model_class = queryset.model
        
        # Check if the view has specified which fields to filter on
        field_names = None
        if hasattr(view, 'filter_set_fields'):
            field_names = view.filter_set_fields
        
        # Generate an AutoFilterSet class for this model with the specified fields
        return AutoFilterSet.get_filter_class_for_model(model_class, field_names)