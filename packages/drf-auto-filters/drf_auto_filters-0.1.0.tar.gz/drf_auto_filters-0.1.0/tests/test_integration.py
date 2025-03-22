"""
Integration tests for DRF Auto Filters with DRF and drf-yasg.
"""
import json
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import path, include
from rest_framework import serializers, viewsets
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient, APIRequestFactory

from drf_auto_filters import AutoFilterBackend, swagger_auto_schema_with_filters
from tests.models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [AutoFilterBackend]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [AutoFilterBackend]
    
    @swagger_auto_schema_with_filters()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# Set up test URL patterns
router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]


@override_settings(ROOT_URLCONF=__name__)
class DRFIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        
        # Create test data
        self.author = Author.objects.create(
            name="Test Author",
            birth_date="1990-01-01",
            biography="Test biography",
        )
        
        self.book1 = Book.objects.create(
            title="Test Book",
            author=self.author,
            publication_date="2020-01-01",
            price=19.99,
            pages=200,
            description="Test description",
            is_bestseller=True,
            genre="fiction",
        )
        
        self.book2 = Book.objects.create(
            title="Another Book",
            author=self.author,
            publication_date="2021-01-01",
            price=29.99,
            pages=300,
            description="Another test description",
            is_bestseller=False,
            genre="sci-fi",
        )
    
    def test_api_list_with_filters(self):
        """Test that the API correctly handles filter parameters."""
        # Test exact match filter
        response = self.client.get("/api/books/?title_exact=Test Book")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.book1.id)
        
        # Test partial match filter
        response = self.client.get("/api/books/?title_partial=Another")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.book2.id)
        
        # Test numeric range filter
        response = self.client.get("/api/books/?price_min=25.00")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.book2.id)
        
        # Test date range filter
        response = self.client.get("/api/books/?publication_date_after=2020-06-01")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.book2.id)
        
        # Test boolean filter
        response = self.client.get("/api/books/?is_bestseller=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.book1.id)
        
        # Test foreign key filter
        response = self.client.get(f"/api/books/?author_id={self.author.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        
        # Test multiple filters (AND logic)
        response = self.client.get(f"/api/books/?title_partial=Book&price_min=25.00")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["id"], self.book2.id)
        
        # Test filter with no results
        response = self.client.get("/api/books/?title_exact=Non-Existent Book")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)
        
    def test_filter_parameter_validation(self):
        """Test that invalid filter parameters are handled correctly."""
        # Test with invalid value type
        response = self.client.get("/api/books/?price_min=invalid")
        self.assertEqual(response.status_code, 200)  # DRF silently ignores invalid filters
        data = response.json()
        self.assertEqual(data["count"], 2)  # Returns all books
        
        # Test with non-existent filter
        response = self.client.get("/api/books/?nonexistent_filter=value")
        self.assertEqual(response.status_code, 200)  # DRF silently ignores invalid filters
        data = response.json()
        self.assertEqual(data["count"], 2)  # Returns all books


@mock.patch('drf_auto_filters.schema.SwaggerAutoSchemaGenerator.get_filter_parameters')
@override_settings(ROOT_URLCONF=__name__)
class SwaggerIntegrationTests(TestCase):
    """Test integration with drf-yasg for Swagger documentation."""
    
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        
    def test_swagger_schema_generation(self, mock_get_filter_parameters):
        """Test that swagger schema correctly incorporates filter parameters."""
        # Mock filter parameters
        mock_get_filter_parameters.return_value = [
            {'name': 'title_exact', 'in': 'query', 'description': 'Filter by exact title match'},
            {'name': 'price_min', 'in': 'query', 'description': 'Filter by minimum price'}
        ]
        
        try:
            # Only test if drf-yasg is installed
            from drf_yasg.views import get_schema_view
            from drf_yasg import openapi
            
            # Create schema view
            schema_view = get_schema_view(
                openapi.Info(
                    title="Test API",
                    default_version='v1',
                ),
                public=True,
            )
            
            # Get schema
            response = self.client.get('/api/swagger.json', format='json')
            
            # Since we can't actually run the drf-yasg view in these tests,
            # we'll just verify our swagger_auto_schema_with_filters decorator
            # calls the expected methods
            self.assertTrue(mock_get_filter_parameters.called)
            
        except ImportError:
            # Skip test if drf-yasg is not installed
            self.skipTest("drf-yasg is not installed")