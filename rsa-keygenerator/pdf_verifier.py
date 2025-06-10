## @file pdf_verifier.py
#  @brief Moduł do weryfikacji podpisu cyfrowego w dokumencie PDF.
#  Sprawdza, czy podpis znajdujący się w metadanych PDF jest zgodny z jego zawartością oraz z kluczem publicznym użytkownika A.

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from PyPDF2 import PdfReader, PdfWriter
import hashlib

## @brief Weryfikuje podpis cyfrowy znajdujący się w metadanych pliku PDF.
#  @param pdf_path Ścieżka do podpisanego pliku PDF.
#  @param public_key_path Ścieżka do pliku PEM z kluczem publicznym użytkownika A.
#  @return True jeśli podpis jest poprawny, False w przeciwnym wypadku.
#  @throws ValueError jeśli podpis nie znajduje się w metadanych PDF.
def verify_signature(pdf_path: str, public_key_path: str) -> bool:
    # Wczytanie klucza publicznego
    with open(public_key_path, "rb") as f:
        public_key_data = f.read()
    public_key = serialization.load_pem_public_key(public_key_data)

    # Odczyt metadanych PDF i pobranie podpisu
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    signature_hex = metadata.get("/Signature")
    if not signature_hex:
        raise ValueError("Brak podpisu w metadanych PDF.")

    signature = bytes.fromhex(signature_hex)

    # Przygotowanie czystej kopii PDF bez metadanych do obliczenia skrótu
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    import io
    buffer = io.BytesIO()
    writer.write(buffer)
    pdf_bytes = buffer.getvalue()

    # Obliczenie skrótu SHA-256 z zawartości PDF
    hash_val = hashlib.sha256(pdf_bytes).digest()

    # Weryfikacja podpisu
    try:
        public_key.verify(
            signature,
            hash_val,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
