# -*- coding: utf-8 -*-
import os
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    _logger.warning("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")

try:
    from pdfminer.high_level import extract_text
    from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
    from pdfminer.pdfparser import PDFSyntaxError
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False
    _logger.warning("pdfminer.six not installed. Install with: pip install pdfminer.six")

try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    _logger.warning("pdf2image not installed. Install with: pip install pdf2image")

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    _logger.warning("pytesseract or PIL not installed. Install with: pip install pytesseract Pillow")

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    _logger.warning("python-docx not installed. Install with: pip install python-docx")


class PDFExtractor:
    """
    Ekstrak teks dari PDF (baik teks maupun hasil scan),
    lalu bisa disimpan ke DOCX atau TXT.
    """

    def __init__(self, file_bytes):
        """
        Args:
            file_bytes: bytes data dari file PDF
        """
        self.file_bytes = file_bytes

    def is_text_based_pdf(self):
        """
        Cek cepat apakah PDF mengandung teks yang bisa diekstrak tanpa OCR.
        """
        if not HAS_PDFMINER:
            _logger.warning("pdfminer.six not available, cannot check if PDF is text-based")
            return False
            
        try:
            text = extract_text(io.BytesIO(self.file_bytes), maxpages=1)
            has_text = bool(text.strip())
            _logger.info(f"PDF text-based check: {has_text}")
            return has_text
        except (PDFSyntaxError, PDFTextExtractionNotAllowed) as e:
            _logger.debug(f"PDF is protected or has syntax error: {e}")
            return False
        except Exception as e:
            _logger.debug(f"Error checking PDF type: {e}")
            return False

    def extract_text_from_pdfminer(self):
        """Gunakan pdfminer untuk ekstraksi teks (PDF berbasis teks)"""
        if not HAS_PDFMINER:
            _logger.error("pdfminer.six not installed")
            return ""
            
        try:
            _logger.info("Extracting text using pdfminer.six...")
            text = extract_text(io.BytesIO(self.file_bytes))
            _logger.info(f"pdfminer extracted {len(text)} characters")
            return text
        except Exception as e:
            _logger.error(f"[pdfminer] Gagal ekstrak teks: {e}")
            return ""

    def extract_text_from_pymupdf(self):
        """Gunakan PyMuPDF (fitz) sebagai alternatif pdfminer"""
        if not HAS_FITZ:
            _logger.error("PyMuPDF (fitz) not installed")
            return ""
            
        text_all = []
        try:
            _logger.info("Extracting text using PyMuPDF (fitz)...")
            with fitz.open(stream=self.file_bytes, filetype="pdf") as doc:
                for page_num, page in enumerate(doc):
                    page_text = page.get_text("text")
                    text_all.append(page_text)
                    _logger.debug(f"Page {page_num + 1}: {len(page_text)} chars")
            
            result = "\n".join(text_all)
            _logger.info(f"PyMuPDF extracted {len(result)} characters from {len(text_all)} pages")
            return result
        except Exception as e:
            _logger.error(f"[fitz] Gagal ekstrak teks: {e}")
            return ""

    def extract_text_with_layout(self):
        """
        Extract text from PDF while preserving layout using PyMuPDF blocks.
        Uses horizontal positioning (x0) to detect indentation and alignment.
        """
        if not HAS_FITZ:
            _logger.error("PyMuPDF (fitz) not installed")
            return ""
        
        result = []
        try:
            _logger.info("Extracting text with layout preservation using PyMuPDF blocks...")
            with fitz.open(stream=self.file_bytes, filetype="pdf") as doc:
                for page_num, page in enumerate(doc):
                    blocks = page.get_text("blocks")
                    _logger.debug(f"Page {page_num + 1}: Found {len(blocks)} text blocks")
                    
                    for block in blocks:
                        # block format: (x0, y0, x1, y1, "text", block_no, block_type)
                        x0, y0, x1, y1, text, block_no, block_type = block
                        
                        # Skip empty blocks
                        if not text.strip():
                            continue
                        
                        # Detect indentation based on horizontal position
                        if x0 < 100:
                            # Left-aligned text (main content)
                            result.append(text)
                        elif x0 < 200:
                            # First level indentation (e.g., list items)
                            result.append(f"    {text}")
                        elif x0 > 200:
                            # Deeper indentation
                            if abs(x0 - 210) < 10:
                                # Centered text (e.g., titles)
                                result.append(f"\n{text.center(80)}\n")
                            else:
                                result.append(f"        {text}")
                        else:
                            result.append(text)
            
            final_text = "\n".join(result)
            _logger.info(f"Layout extraction complete: {len(final_text)} characters extracted")
            return final_text
        except Exception as e:
            _logger.error(f"[fitz layout] Failed to extract text with layout: {e}")
            return ""

    def extract_text_with_ocr(self, lang="ind"):
        """
        Gunakan OCR (Tesseract) untuk PDF hasil scan.
        Pastikan Tesseract dan pdf2image sudah terpasang.
        
        Args:
            lang: Language code for Tesseract (default: 'ind' for Indonesian)
        """
        if not HAS_PDF2IMAGE:
            _logger.error("pdf2image not installed, cannot perform OCR")
            return ""
        
        if not HAS_OCR:
            _logger.error("pytesseract or PIL not installed, cannot perform OCR")
            return ""
            
        text_all = []
        try:
            _logger.info("Converting PDF to images for OCR...")
            images = convert_from_bytes(self.file_bytes, dpi=300)
            _logger.info(f"Converted to {len(images)} images, performing OCR...")
            
            for i, img in enumerate(images):
                _logger.debug(f"OCR processing page {i + 1}/{len(images)}...")
                text = pytesseract.image_to_string(img, lang=lang)
                text_all.append(text)
            
            result = "\n".join(text_all)
            _logger.info(f"OCR extracted {len(result)} characters from {len(images)} pages")
            return result
        except Exception as e:
            _logger.error(f"[OCR] Gagal melakukan OCR: {e}")
            return ""

    def extract_text_auto(self):
        """Pilih metode otomatis berdasarkan isi PDF"""
        _logger.info("Starting automatic PDF text extraction...")
        
        # Try text-based extraction first (faster)
        if self.is_text_based_pdf():
            _logger.info("PDF is text-based, trying pdfminer first...")
            text = self.extract_text_from_pdfminer()
            
            if not text.strip():
                _logger.info("pdfminer returned empty, trying PyMuPDF...")
                text = self.extract_text_from_pymupdf()
        else:
            # PDF is image-based, need OCR
            _logger.info("PDF is image-based or protected, attempting OCR...")
            text = self.extract_text_with_ocr()
        
        result = text.strip()
        _logger.info(f"Auto extraction complete: {len(result)} characters extracted")
        return result

    def save_as_docx(self, output_path=None):
        """
        Simpan hasil ekstraksi ke file DOCX.
        
        Returns:
            str: Path to saved file, or None if failed
        """
        if not HAS_DOCX:
            _logger.error("python-docx not installed, cannot save as DOCX")
            return None
            
        text = self.extract_text_auto()
        if not text:
            _logger.warning("No text extracted, cannot save DOCX")
            return None

        try:
            doc = Document()
            for line in text.splitlines():
                if line.strip():  # Skip empty lines
                    doc.add_paragraph(line)
            
            output_path = output_path or "output_extracted.docx"
            doc.save(output_path)
            _logger.info(f"Saved extracted text to {output_path}")
            return output_path
        except Exception as e:
            _logger.error(f"Failed to save DOCX: {e}")
            return None

    def save_as_txt(self, output_path=None):
        """
        Simpan hasil ekstraksi ke file TXT.
        
        Returns:
            str: Path to saved file, or None if failed
        """
        text = self.extract_text_auto()
        if not text:
            _logger.warning("No text extracted, cannot save TXT")
            return None
        
        try:
            output_path = output_path or "output_extracted.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            _logger.info(f"Saved extracted text to {output_path}")
            return output_path
        except Exception as e:
            _logger.error(f"Failed to save TXT: {e}")
            return None
