"""
Tests for the auto filter functionality.
"""
import datetime
from unittest import mock

from django.test import TestCase
from django_filters import rest_framework as django_filters
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import ModelViewSet

from drf_auto_filters import AutoFilterBackend, AutoFilterSet
from tests.models import Author, Book


class BookSerializer:
    class Meta:
        model = Book
        fields = "__all__"


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [AutoFilterBackend]


class AutoFilterSetTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            name="Test Author",
            birth_date=datetime.date(1990, 1, 1),
            biography="Test biography",
        )
        
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            publication_date=datetime.date(2020, 1, 1),
            price=19.99,
            pages=200,
            description="Test description",
            is_bestseller=True,
            genre="fiction",
        )
        
        self.book2 = Book.objects.create(
            title="Another Book",
            author=self.author,
            publication_date=datetime.date(2021, 1, 1),
            price=29.99,
            pages=300,
            description="Another test description",
            is_bestseller=False,
            genre="sci-fi",
        )
        
        self.factory = APIRequestFactory()
        
    def test_auto_filter_set_creation(self):
        """Test that AutoFilterSet correctly creates filters for a model."""
        filter_class = AutoFilterSet.get_filter_class_for_model(Book)
        
        # Check that the filter class has been created correctly
        self.assertTrue(issubclass(filter_class, AutoFilterSet))
        self.assertEqual(filter_class.Meta.model, Book)
        
        # Check that filters were created for text fields
        self.assertIn("title_exact", filter_class.base_filters)
        self.assertIn("title_partial", filter_class.base_filters)
        
        # Check that filters were created for numeric fields
        self.assertIn("price_exact", filter_class.base_filters)
        self.assertIn("price_min", filter_class.base_filters)
        self.assertIn("price_max", filter_class.base_filters)
        
        # Check that filters were created for date fields
        self.assertIn("publication_date_exact", filter_class.base_filters)
        self.assertIn("publication_date_before", filter_class.base_filters)
        self.assertIn("publication_date_after", filter_class.base_filters)
        
        # Check that filters were created for boolean fields
        self.assertIn("is_bestseller", filter_class.base_filters)
        
        # Check that filters were created for foreign key fields
        self.assertIn("author_id", filter_class.base_filters)
        
        # Check that filters were created for choice fields
        self.assertIn("genre_exact", filter_class.base_filters)
        
    def test_filter_backend_integration(self):
        """Test that AutoFilterBackend integrates correctly with DRF views."""
        backend = AutoFilterBackend()
        view = BookViewSet()
        
        # Mock the view's get_queryset method
        view.get_queryset = mock.MagicMock(return_value=Book.objects.all())
        
        # Test that the backend returns the correct filter class
        filter_class = backend.get_filterset_class(view, Book.objects.all())
        self.assertTrue(issubclass(filter_class, AutoFilterSet))
        
    def test_filtering_functionality(self):
        """Test that the generated filters actually work."""
        filter_class = AutoFilterSet.get_filter_class_for_model(Book)
        
        # Test text exact filter
        filtered = filter_class({"title_exact": "Test Book"}, queryset=Book.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.book)
        
        # Test text partial filter
        filtered = filter_class({"title_partial": "Book"}, queryset=Book.objects.all())
        self.assertEqual(filtered.qs.count(), 2)
        
        # Test numeric min filter
        filtered = filter_class({"price_min": "25.00"}, queryset=Book.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.book2)
        
        # Test boolean filter
        filtered = filter_class({"is_bestseller": "true"}, queryset=Book.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.book)
        
        # Test foreign key filter
        filtered = filter_class({"author_id": str(self.author.id)}, queryset=Book.objects.all())
        self.assertEqual(filtered.qs.count(), 2)
        
        # Test choice field filter
        filtered = filter_class({"genre_exact": "sci-fi"}, queryset=Book.objects.all())
        self.assertEqual(filtered.qs.count(), 1)
        self.assertEqual(filtered.qs.first(), self.book2)