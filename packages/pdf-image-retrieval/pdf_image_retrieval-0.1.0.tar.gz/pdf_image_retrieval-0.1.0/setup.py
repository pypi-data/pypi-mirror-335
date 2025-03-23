from setuptools import setup, find_packages

setup(
    name="pdf-image-retrieval",
    version="0.1.0",
    author="Aryan Dhandhukiya",
    author_email="dhandhukiyaaryan05@gmail.com",
    description="Extracts images from PDFs, stores them in S3, and retrieves based on keyword search",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aryandhandhukiya/pdf-image-retrieval",
    packages=find_packages(),
    install_requires=["fitz", "pdf2image", "Pillow", "boto3", "nltk"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
