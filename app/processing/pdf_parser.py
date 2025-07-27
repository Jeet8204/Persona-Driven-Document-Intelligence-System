
import os
import re
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from app.config import MIN_WORDS_FOR_SUBSECTION, MIN_HEADING_FONT_SIZE, HEADING_MAX_WORDS, OCR_RESOLUTION_DPI

def clean_text(text):
    """Cleans whitespace and removes non-printable characters from a string."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text

def extract_text_with_ocr_fallback(doc, page_num):
    """Extracts text from a page, falling back to OCR if the text layer is empty."""
    page = doc.load_page(page_num)
    text = page.get_text().strip()
    if not text:
        print(f"  -> No text layer on page {page_num + 1}. Attempting OCR...")
        try:
            pix = page.get_pixmap(dpi=OCR_RESOLUTION_DPI)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            print(f"     OCR failed for page {page_num + 1}: {e}")
            text = ""
    return clean_text(text)

def is_heading(span):
    """Determines if a text span is likely a heading based on font properties."""
    text = span.get("text", "").strip()
    if not text:
        return False
    
    font_size = span.get("size", 0)
    is_bold = "bold" in span.get("font", "").lower()
    word_count = len(text.split())

    return font_size >= MIN_HEADING_FONT_SIZE and is_bold and word_count <= HEADING_MAX_WORDS

def extract_sections_from_file(pdf_path):
    """
    Extracts sections from a PDF using a stateful approach that tracks sections across pages.
    """
    all_sections = []
    current_section = None

    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict").get("blocks", [])
            for b in blocks:
                if b['type'] == 0:
                    block_text = "".join([clean_text(s['text']) for l in b['lines'] for s in l['spans']])
                    if not block_text:
                        continue

                    first_span = b["lines"][0]["spans"][0]
                    if is_heading(first_span):
                        if current_section:
                            full_text = "\n\n".join(current_section["content_blocks"])
                            subsections = [{"text": p, "page_number": current_section["page_number"], "filename": current_section["filename"]} for p in current_section["content_blocks"] if len(p.split()) >= MIN_WORDS_FOR_SUBSECTION]
                            
                            current_section["text"] = full_text
                            current_section["subsections"] = subsections
                            del current_section["content_blocks"]
                            all_sections.append(current_section)

                        current_section = {
                            "filename": os.path.basename(pdf_path),
                            "page_number": page_num + 1,
                            "section_title": clean_text(first_span['text']),
                            "content_blocks": [],
                        }
                    elif current_section:
                        current_section["content_blocks"].append(block_text)

        if current_section:
            full_text = "\n\n".join(current_section["content_blocks"])
            subsections = [{"text": p, "page_number": current_section["page_number"], "filename": current_section["filename"]} for p in current_section["content_blocks"] if len(p.split()) >= MIN_WORDS_FOR_SUBSECTION]
            current_section["text"] = full_text
            current_section["subsections"] = subsections
            del current_section["content_blocks"]
            all_sections.append(current_section)

        if not all_sections:
            print(f"  -> No structured sections found in {os.path.basename(pdf_path)}. Falling back to page-based extraction.")
            for i in range(doc.page_count):
                page_text = extract_text_with_ocr_fallback(doc, i)
                if page_text:
                    subsections = [{"text": page_text, "page_number": i + 1, "filename": os.path.basename(pdf_path)}]
                    all_sections.append({
                        "filename": os.path.basename(pdf_path),
                        "page_number": i + 1,
                        "section_title": f"Page {i + 1} Content",
                        "text": page_text,
                        "subsections": subsections
                    })
        doc.close()
    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {e}")
    
    return all_sections

def extract_all_documents(pdf_paths: list):
    """
    Loops through a given list of PDF paths and extracts their content.
    """
    all_extracted_data = []

    # --- CHANGED: The function now iterates over the provided list of file paths ---
    if not pdf_paths:
        print("Warning: No PDF document paths were provided for processing.")
        return []

    for doc_path in pdf_paths:
        if not os.path.exists(doc_path):
            print(f"Warning: File not found at {doc_path}. Skipping.")
            continue
        
        filename = os.path.basename(doc_path)
        print(f" -> Processing: {filename}")
        file_data = extract_sections_from_file(doc_path)
        all_extracted_data.extend(file_data)
        
    # --- CHANGED: The function now returns only the extracted data ---
    return all_extracted_data