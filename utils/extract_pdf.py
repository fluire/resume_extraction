import PyPDF2

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract_text(self) -> str:
        text = ""
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

# Usage example:
extractor = PDFExtractor("RISHI-JUL_2025.pdf")
pdf_text = extractor.extract_text()
print(pdf_text)