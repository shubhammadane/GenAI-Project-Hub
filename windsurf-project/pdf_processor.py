"""
PDF text extraction with page metadata preservation.
"""
import fitz
from typing import List, Dict, Tuple


class PDFProcessor:
    """Extracts text from PDF files while preserving page numbers."""
    
    def __init__(self):
        self.pages: List[Dict] = []
    
    def extract_pdf_text(self, pdf_path: str) -> Tuple[List[Dict], str]:
        """
        Extract text from PDF page by page with page metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (list of page dicts with text and page number, error message)
        """
        self.pages = []
        total_text = ""
        
        try:
            doc = fitz.open(pdf_path)
            
            # Check if PDF is password protected
            if doc.is_encrypted:
                doc.close()
                return [], "This PDF is password-protected. Please provide an unprotected PDF."
            
            # Check if PDF has any pages
            if len(doc) == 0:
                doc.close()
                return [], "This PDF contains no pages."
            
            # Extract text page by page
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    self.pages.append({
                        "page_number": page_num + 1,  # 1-indexed for display
                        "text": text
                    })
                    total_text += text + "\n"
            
            doc.close()
            
            # Check if any text was extracted
            if not self.pages:
                return [], "No extractable text found in this PDF. This may be a scanned document. OCR is not supported in this version."
            
            return self.pages, ""
            
        except fitz.FileDataError:
            return [], "The PDF file appears to be corrupted or invalid."
        except Exception as e:
            return [], f"Error reading PDF: {str(e)}"
    
    def get_page_count(self) -> int:
        """Return the number of pages extracted."""
        return len(self.pages)
    
    def get_full_text(self) -> str:
        """Return the concatenated text from all pages."""
        return "\n".join([page["text"] for page in self.pages])
    
    def get_text_preview(self, max_chars: int = 500) -> str:
        """Return a preview of the extracted text."""
        full_text = self.get_full_text()
        if len(full_text) <= max_chars:
            return full_text
        return full_text[:max_chars] + "..."
