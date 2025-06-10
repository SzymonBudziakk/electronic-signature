## @file pdf_signer.py
#  @brief Moduł odpowiadający za podpisywanie dokumentów PDF z wykorzystaniem klucza RSA.
#  Klucz prywatny użytkownika A przechowywany na pendrive jest odszyfrowywany za pomocą PIN-u, a dokument PDF podpisywany kryptograficznie.

import os
import hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from PyPDF2 import PdfReader, PdfWriter
from constants import PRIVATE_KEY_PATH, SALT_SIZE, AES_KEY_SIZE, IV_SIZE

## @brief Odszyfrowuje klucz prywatny RSA przechowywany na pendrive za pomocą podanego PIN-u.
#  @param pin PIN użytkownika, służący do wygenerowania klucza AES do odszyfrowania klucza RSA.
#  @return Obiekt RSAPrivateKey gotowy do użycia przy podpisywaniu.
#  @throws FileNotFoundError jeśli plik z kluczem nie został znaleziony.
def decrypt_private_key(pin: str) -> rsa.RSAPrivateKey:
    if not os.path.exists(PRIVATE_KEY_PATH):
        raise FileNotFoundError("Pendrive not found or private key missing.")

    with open(PRIVATE_KEY_PATH, "rb") as f:
        data = f.read()
        salt = data[:SALT_SIZE]
        iv = data[SALT_SIZE:SALT_SIZE+IV_SIZE]
        encrypted_data = data[SALT_SIZE+IV_SIZE:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(pin.encode())

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    pad_len = padded_data[-1]
    private_bytes = padded_data[:-pad_len]

    private_key = serialization.load_der_private_key(private_bytes, password=None, backend=default_backend())
    return private_key

## @brief Podpisuje wskazany plik PDF cyfrowo za pomocą klucza prywatnego RSA użytkownika A.
#  @param pdf_path Ścieżka do pliku PDF, który ma zostać podpisany.
#  @param pin PIN użytkownika używany do odszyfrowania klucza prywatnego.
#  @details Podpisywanie odbywa się poprzez wyliczenie skrótu SHA-256 na bazie zawartości PDF, a następnie podpisanie go za pomocą klucza RSA. Podpis oraz dane o podpisującym zapisywane są w metadanych PDF.
def sign_pdf(pdf_path: str, pin: str):
    private_key = decrypt_private_key(pin)

    # Wczytanie dokumentu PDF i zapisanie jego "czystej" wersji do bufora
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    import io
    unsigned_buffer = io.BytesIO()
    writer.write(unsigned_buffer)
    unsigned_pdf_bytes = unsigned_buffer.getvalue()

    # Obliczenie skrótu (hash) całego dokumentu PDF
    hash_val = hashlib.sha256(unsigned_pdf_bytes).digest()

    # Podpisanie skrótu kluczem prywatnym RSA
    signature = private_key.sign(
        hash_val,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Ścieżka wyjściowa do podpisanego dokumentu
    out_path = os.path.splitext(pdf_path)[0] + "_signed.pdf"

    # Wczytanie PDF ponownie i dodanie podpisu jako metadanych
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_metadata({
        "/SignedBy": "User A",
        "/Signature": signature.hex()
    })

    with open(out_path, "wb") as f:
        writer.write(f)
