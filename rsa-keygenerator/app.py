import tkinter as tk
from tkinter import messagebox
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Ścieżka do pendrive'a (dla macOS)
PENDRIVE_PATH = "/Volumes/NO NAME"

# Parametry szyfrowania
RSA_KEY_SIZE = 4096
AES_KEY_SIZE = 32  # 256-bit
IV_SIZE = 16       # For AES CBC

def generate_keys(pin: str):
    if not pin:
        raise ValueError("PIN nie może być pusty.")

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

    # Padding
    pad_len = 16 - (len(private_bytes) % 16)
    padded_data = private_bytes + bytes([pad_len] * pad_len)
    encrypted_private = encryptor.update(padded_data) + encryptor.finalize()

    # Zapis zaszyfrowanego klucza prywatnego
    os.makedirs(PENDRIVE_PATH, exist_ok=True)
    with open(f"{PENDRIVE_PATH}/private_encrypted.key", "wb") as f:
        f.write(salt + iv + encrypted_private)

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
        show="", # Changed from "*" to "" to make the input visible
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

if __name__ == "__main__":
    run_gui()