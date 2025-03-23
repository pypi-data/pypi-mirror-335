import os
import pytest
from pdf_image_retrieval.retriever import ImageRetriever

@pytest.fixture
def retriever():
    """Creates a temporary retriever instance using an in-memory database."""
    return ImageRetriever(":memory:")  # Use SQLite in-memory DB for testing

def test_add_and_search_image(retriever):
    """Test adding and retrieving images by keyword."""
    retriever.add_image("https://your-s3-bucket/image1.png", ["finance", "report"])
    
    results = retriever.search_images("finance")
    
    assert len(results) > 0  # Ensure at least one result is found
    assert "https://your-s3-bucket/image1.png" in results
