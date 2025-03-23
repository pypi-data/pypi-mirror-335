import fitz
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download("punkt")
nltk.download("stopwords")

class PDFKeywordExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_keywords(self):
        doc = fitz.open(self.pdf_path)
        text = " ".join([page.get_text() for page in doc])
        words = word_tokenize(text)
        stop_words = set(stopwords.words("english"))
        keywords = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
        return list(set(keywords))  # Remove duplicates

if __name__ == "__main__":
    extractor = PDFKeywordExtractor("sample.pdf")
    keywords = extractor.extract_keywords()
    print("Extracted Keywords:", keywords)
