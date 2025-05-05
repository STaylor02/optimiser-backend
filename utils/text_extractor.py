import fitz  # PyMuPDF
import docx
import re

def fix_spaced_out_words(text):
    """
    Detects and fixes words where characters are spaced out like 'C u s t o m e r'.
    """
    return re.sub(r'(?<=\b)([A-Z])(?:\s[A-Z]){2,}(?=\b)', lambda m: m.group(0).replace(" ", ""), text)

def clean_text(text):
    """
    Clean text while preserving structure:
    - Remove extra internal spaces
    - Keep line breaks to separate sections
    - Fix character spacing issues
    """
    # Fix spaced-out uppercase words
    text = fix_spaced_out_words(text)

    # Normalize whitespace: replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Reduce multiple newlines to max two (preserve paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove trailing spaces on each line
    text = "\n".join(line.strip() for line in text.splitlines())

    return text.strip()

def extract_text_from_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        return clean_text(text)
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None

def extract_text_from_docx(filepath):
    try:
        doc = docx.Document(filepath)
        text_parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())

        for table in doc.tables:
            for row in table.rows:
                row_text = ' | '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)

        return clean_text("\n".join(text_parts))
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return None

def extract_text(filepath):
    if filepath.lower().endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    elif filepath.lower().endswith('.docx'):
        return extract_text_from_docx(filepath)
    else:
        return None
