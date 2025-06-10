## @file ui_handlers.py
#  @brief Funkcje obsługujące logikę GUI aplikacji podpisu i weryfikacji PDF.
#  Zawiera funkcje związane z wyborem plików, podpisywaniem oraz weryfikacją podpisów elektronicznych.

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pdf_signer import sign_pdf
from pdf_verifier import verify_signature
from constants import PRIVATE_KEY_PATH

## @var app_state
#  @brief Słownik przechowujący stan aplikacji (ścieżki plików i dane GUI).
app_state = {
    "pdf_path": None,
    "verify_pdf_path": None,
    "verify_pub_key_path": None,
    "pin_entry": None,
}

## @brief Sprawdza, czy pendrive z zaszyfrowanym kluczem prywatnym jest podłączony.
#  @return True jeśli plik klucza prywatnego istnieje, False w przeciwnym wypadku.
def check_pendrive():
    return os.path.exists(PRIVATE_KEY_PATH)

## @brief Umożliwia użytkownikowi wybór pliku PDF do podpisania.
#  @param parent Element GUI (ramka), do którego zostanie dodany label z nazwą pliku.
def select_pdf(parent):
    file_path = filedialog.askopenfilename(
        title="Wybierz plik PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        app_state["pdf_path"] = file_path
        label = getattr(parent, "selected_file_label", None)
        if label:
            label.config(text=f"Wybrany plik: {os.path.basename(file_path)}")
        else:
            label = tk.Label(parent, text=f"Wybrany plik: {os.path.basename(file_path)}", font=("Arial", 10))
            label.pack(pady=2)
            setattr(parent, "selected_file_label", label)

## @brief Pokazuje status pendrive’a (czy wykryty).
#  @param parent Element GUI, do którego zostanie dodana etykieta statusu.
def check_and_show_status(parent):
    label = getattr(parent, "status_label", None)
    if not label:
        label = tk.Label(parent, font=("Arial", 10))
        label.pack(pady=2)
        setattr(parent, "status_label", label)

    if check_pendrive():
        label.config(text="✅ Pendrive wykryty", fg="green")
    else:
        label.config(text="❌ Pendrive nie znaleziony", fg="red")

## @brief Obsługuje logikę podpisywania dokumentu po kliknięciu przycisku.
#  Używa PIN-u z GUI do odszyfrowania klucza i podpisania pliku PDF.
def on_submit():
    pin = app_state["pin_entry"].get()
    if not pin:
        messagebox.showerror("Błąd", "PIN nie może być pusty.")
        return

    if not app_state.get("pdf_path"):
        messagebox.showerror("Błąd", "Nie wybrano pliku PDF.")
        return

    if not check_pendrive():
        messagebox.showerror("Błąd", "Pendrive nie został wykryty.")
        return

    try:
        sign_pdf(app_state["pdf_path"], pin)
        messagebox.showinfo("Sukces", "PDF został podpisany pomyślnie.")
    except Exception as e:
        messagebox.showerror("Błąd podczas podpisywania", str(e))

## @brief Umożliwia użytkownikowi wybór podpisanego pliku PDF do weryfikacji.
#  @param parent Ramka GUI do której zostanie dodany label z nazwą pliku.
def select_verify_pdf(parent):
    file_path = filedialog.askopenfilename(
        title="Wybierz podpisany plik PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        app_state["verify_pdf_path"] = file_path
        label = getattr(parent, "verify_pdf_label", None)
        if label:
            label.config(text=f"PDF: {os.path.basename(file_path)}")
        else:
            label = tk.Label(parent, text=f"PDF: {os.path.basename(file_path)}", font=("Arial", 10))
            label.pack(pady=2)
            setattr(parent, "verify_pdf_label", label)

## @brief Umożliwia użytkownikowi wybór pliku z kluczem publicznym.
#  @param parent Ramka GUI do której zostanie dodany label z nazwą klucza.
def select_pub_key(parent):
    key_path = filedialog.askopenfilename(
        title="Wybierz klucz publiczny",
        filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
    )
    if key_path:
        app_state["verify_pub_key_path"] = key_path
        label = getattr(parent, "verify_key_label", None)
        if label:
            label.config(text=f"Klucz: {os.path.basename(key_path)}")
        else:
            label = tk.Label(parent, text=f"Klucz: {os.path.basename(key_path)}", font=("Arial", 10))
            label.pack(pady=2)
            setattr(parent, "verify_key_label", label)

## @brief Przeprowadza proces weryfikacji podpisu na podstawie wybranego PDF i klucza publicznego.
#  Informuje użytkownika o wyniku (poprawny/niepoprawny podpis).
def verify_pdf_signature():
    pdf_path = app_state.get("verify_pdf_path")
    pub_key_path = app_state.get("verify_pub_key_path")

    if not pdf_path or not pub_key_path:
        messagebox.showerror("Błąd", "Wybierz plik PDF i klucz publiczny.")
        return

    try:
        valid = verify_signature(pdf_path, pub_key_path)
        if valid:
            messagebox.showinfo("Weryfikacja", "✅ Podpis jest poprawny.")
        else:
            messagebox.showerror("Weryfikacja", "❌ Podpis jest niepoprawny lub plik został zmodyfikowany.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się zweryfikować: {e}")
