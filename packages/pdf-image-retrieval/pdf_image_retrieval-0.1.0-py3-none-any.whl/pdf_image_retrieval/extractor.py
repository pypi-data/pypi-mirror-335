import fitz  # PyMuPDF
import os
from pdf2image import convert_from_path
from PIL import Image

class PDFImageExtractor:
    def __init__(self, pdf_path, output_folder="images"):
        self.pdf_path = pdf_path
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def extract_images(self):
        doc = fitz.open(self.pdf_path)
        images = []
        for page_number in range(len(doc)):
            for img_index, img in enumerate(doc[page_number].get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_format = base_image["ext"]
                img_path = os.path.join(self.output_folder, f"page_{page_number+1}_img_{img_index+1}.{img_format}")
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                images.append(img_path)
        return images

if __name__ == "__main__":
    extractor = PDFImageExtractor("sample.pdf")
    extracted_images = extractor.extract_images()
    print("Extracted images:", extracted_images)
