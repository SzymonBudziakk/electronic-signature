## @file key_generator.py
#  @brief Moduł GUI do generowania pary kluczy RSA oraz szyfrowania klucza prywatnego za pomocą AES.
#  Wygenerowany klucz prywatny jest zapisywany na pendrive w postaci zaszyfrowanej, a klucz publiczny jako PEM.

import tkinter as tk
from tkinter import messagebox
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from constants import PENDRIVE_PATH, RSA_KEY_SIZE, AES_KEY_SIZE, IV_SIZE

## @brief Funkcja generująca parę kluczy RSA i zapisująca je w odpowiednich lokalizacjach.
#  @param pin PIN podany przez użytkownika, wykorzystywany jako hasło do szyfrowania klucza prywatnego.
#  @throws ValueError jeśli PIN jest pusty.
#  @throws FileNotFoundError jeśli pendrive nie został wykryty.
def generate_keys(pin: str):
    if not pin:
        raise ValueError("PIN nie może być pusty.")

    if not os.path.exists(PENDRIVE_PATH):
        raise FileNotFoundError(f"Pendrive nie został znaleziony w {PENDRIVE_PATH}")

    # Generowanie klucza RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=RSA_KEY_SIZE,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Zapis klucza publicznego
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("public_key.pem", "wb") as f:
        f.write(pub_bytes)

    # KDF (z PIN-u -> klucz AES)
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(pin.encode())

    # Szyfrowanie klucza prywatnego
    iv = os.urandom(IV_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Dodanie paddingu do danych binarnych (zgodnie z blokiem AES)
    pad_len = 16 - (len(private_bytes) % 16)
    padded_data = private_bytes + bytes([pad_len] * pad_len)
    encrypted_private = encryptor.update(padded_data) + encryptor.finalize()

    # Zapis zaszyfrowanego klucza prywatnego na pendrive
    private_key_path = os.path.join(PENDRIVE_PATH, "private_encrypted.key")
    with open(private_key_path, "wb") as f:
        f.write(salt + iv + encrypted_private)

## @brief Funkcja uruchamiająca graficzny interfejs do generowania kluczy.
#  Umożliwia użytkownikowi wpisanie PIN-u oraz wygenerowanie pary kluczy RSA.
def run_gui():
    def on_generate():
        pin = pin_entry.get()
        try:
            generate_keys(pin)
            messagebox.showinfo("Sukces", "Klucze zostały wygenerowane i zapisane.")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    root = tk.Tk()
    root.title("Generator kluczy RSA")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True)

    tk.Label(frame, text="Wprowadź PIN:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")

    pin_entry = tk.Entry(
        frame,
        show="",  # Wpis widoczny (do testów; opcjonalnie można ustawić na "*")
        font=("Arial", 14),
        width=30,
        highlightbackground="gray",
        highlightcolor="blue",
        highlightthickness=1,
        relief="solid"
    )
    pin_entry.grid(row=1, column=0, pady=10)
    pin_entry.focus_set()

    generate_button = tk.Button(
        frame,
        text="Generuj klucze",
        command=on_generate,
        font=("Arial", 12),
        padx=10,
        pady=5
    )
    generate_button.grid(row=2, column=0, pady=10)

    root.geometry("400x200")
    root.resizable(False, False)
    root.mainloop()

## @brief Punkt wejścia do programu - uruchomienie GUI do generowania kluczy.
if __name__ == "__main__":
    run_gui()
