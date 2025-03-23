import os
import pytest
from pdf_image_retrieval.extractor import PDFImageExtractor  # Corrected import

@pytest.fixture
def sample_pdf():
    return "tests/sample.pdf"  # Ensure this file exists for testing

def test_extract_images(sample_pdf):
    extractor = PDFImageExtractor(sample_pdf)  # Use PDFImageExtractor instead of PDFKeywordExtractor
    images = extractor.extract_images()  # extract_images() exists in PDFImageExtractor
    assert isinstance(images, list)  # Ensure it returns a list
    assert len(images) > 0  # Ensure at least one image is extracted
