from zipfile import ZipFile
import mimetypes
import io

mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".docx",
)
mimetypes.add_type("application/msword", ".doc")
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".pptx",
)
mimetypes.add_type("application/vnd.ms-powerpoint", ".ppt")


def guess_content_type(filename: str) -> str:
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None:
        return "application/octet-stream"
    return content_type


def is_valid_docx(bytes: io.BytesIO) -> bool:
    try:
        with ZipFile(bytes) as file:
            if (
                "[Content_Types].xml" not in file.namelist()
                or "word/document.xml" not in file.namelist()
            ):
                return False
        return True
    except Exception:
        return False


def is_valid_pptx(bytes: io.BytesIO) -> bool:
    try:
        with ZipFile(bytes) as file:
            if (
                "[Content_Types].xml" not in file.namelist()
                or "ppt/presentation.xml" not in file.namelist()
            ):
                return False
        return True
    except Exception:
        return False


def _get_mime_type_from_content(file_bytes: io.BytesIO) -> str:
    file_bytes.seek(0)

    try:
        if is_valid_docx(file_bytes):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if is_valid_pptx(file_bytes):
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    except Exception:
        pass

    return "unknown"


def is_allowed_file(filename: str, file_bytes: io.BytesIO) -> bool:
    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type is None:
        mime_type = _get_mime_type_from_content(file_bytes)

    allowed_mime_types = [
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-powerpoint",  # .ppt
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
        "text/plain",  # .txt
        "image/jpeg",  # jpg/jpeg
        "image/png",  # png
    ]

    return mime_type in allowed_mime_types
