
from pathlib import Path

import pymupdf
from docx import Document


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF resume.

    Returns:
        str: Extracted text from all PDF pages.
    """
    text_parts = []

    with pymupdf.open(file_path) as document:
        for page in document:
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX resume.

    Returns:
        str: Extracted paragraph text.
    """
    document = Document(file_path)
    text_parts = []

    for paragraph in document.paragraphs:
        paragraph_text = paragraph.text.strip()
        if paragraph_text:
            text_parts.append(paragraph_text)

    return "\n".join(text_parts).strip()


def extract_resume_text(file_path):
    """
    Detect the resume file type and extract its text.

    Supports PDF and DOCX files.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Resume file not found: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(path)

    elif extension == ".docx":
        return extract_text_from_docx(path)

    else:
        raise ValueError(
            "Unsupported file type. Please upload a PDF or DOCX file."
        )


if __name__ == "__main__":
    print("Resume Parser module loaded successfully.")
    print("Supported formats: PDF and DOCX")

