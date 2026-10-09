from pathlib import Path


ALLOWED_SIGNATURES = {
    "png": (b"\x89PNG\r\n\x1a\n",),
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "pdf": (b"%PDF-",),
    "doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
    # DOCX uses the Open XML ZIP container. Full document parsing belongs in a malware-scanning pipeline.
    "docx": (b"PK\x03\x04",),
}


def validate_upload(uploaded_file, allowed_extensions):
    """Validate extension and known file signatures without trusting the browser MIME type."""
    filename = uploaded_file.filename or ""
    if "." not in filename:
        return False, "File must have an allowed extension."
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in allowed_extensions or extension not in ALLOWED_SIGNATURES:
        return False, "Only PNG, JPG, JPEG, PDF, DOC and DOCX files are allowed."

    header = uploaded_file.stream.read(16)
    uploaded_file.stream.seek(0)
    if not any(header.startswith(signature) for signature in ALLOWED_SIGNATURES[extension]):
        return False, "File content does not match its extension."
    return True, None


def safe_upload_path(upload_folder, stored_filename):
    """Return a generated filename path guaranteed to stay inside the configured upload folder."""
    root = Path(upload_folder).resolve()
    target = (root / stored_filename).resolve()
    if root not in target.parents:
        raise ValueError("Invalid upload storage path.")
    return target
