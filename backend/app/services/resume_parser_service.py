from io import BytesIO
from pathlib import Path

import fitz
from docx import Document


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from a PDF file without saving it to disk."""
    document = fitz.open(stream=file_bytes, filetype="pdf")

    try:
        text_parts = []

        for page in document:
            text_parts.append(page.get_text())

        return "\n".join(text_parts).strip()

    finally:
        document.close()


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from a DOCX file without saving it to disk."""
    document = Document(BytesIO(file_bytes))

    text_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    return "\n".join(text_parts).strip()


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """Extract resume text based on the uploaded file extension."""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Please upload a PDF or DOCX resume."
        )

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if extension == ".pdf":
        text = extract_pdf_text(file_bytes)

    elif extension == ".docx":
        text = extract_docx_text(file_bytes)

    else:
        raise ValueError("Unsupported file type.")

    if not text:
        raise ValueError(
            "No readable text was found in the uploaded resume."
        )

    return text