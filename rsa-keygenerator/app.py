## @file app.py
#  @brief Główna aplikacja GUI do podpisywania i weryfikacji plików PDF.

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from ui_handlers import (
    select_pdf,
    check_and_show_status,
    on_submit,
    select_verify_pdf,
    select_pub_key,
    verify_pdf_signature,
    app_state
)

## @brief Funkcja uruchamiająca główne GUI aplikacji.
#  Tworzy dwie sekcje: podpisywanie i weryfikację plików PDF.
def run_main_app():
    root = tk.Tk()
    root.title("Aplikacja podpisu PDF")

    frame = tk.Frame(root, padx=10, pady=20)
    frame.pack(expand=True)

    ## @brief Funkcja tworząca interfejs GUI dla podpisywania PDF.
    def handle_sign():
        sign_frame = tk.LabelFrame(frame, text="Podpisywanie", font=("Arial", 12, "bold"), padx=10, pady=10)
        sign_frame.grid(row=0, column=0, padx=(0, 40), pady=10, sticky="n")

        select_pdf_button = tk.Button(
            sign_frame,
            text="Wybierz plik PDF",
            command=lambda: select_pdf(sign_frame),
            font=("Arial", 12)
        )
        select_pdf_button.pack(pady=5)

        tk.Label(sign_frame, text="Wprowadź PIN:", font=("Arial", 12)).pack(anchor="w", pady=(10, 0))
        pin_entry = tk.Entry(
            sign_frame,
            show="*",
            font=("Arial", 14),
            width=30
        )
        pin_entry.pack(pady=5)
        app_state["pin_entry"] = pin_entry

        check_pendrive_button = tk.Button(
            sign_frame,
            text="Sprawdź pendrive",
            command=lambda: check_and_show_status(sign_frame),
            font=("Arial", 12)
        )
        check_pendrive_button.pack(pady=5)

        submit_button = tk.Button(
            sign_frame,
            text="Podpisz PDF",
            command=on_submit,
            font=("Arial", 12),
            padx=10,
            pady=5
        )
        submit_button.pack(pady=10)

    ## @brief Funkcja tworząca interfejs GUI dla weryfikacji podpisu PDF.
    def handle_verify():
        verify_frame = tk.LabelFrame(frame, text="Weryfikacja", font=("Arial", 12, "bold"), padx=10, pady=10)
        verify_frame.grid(row=0, column=1, pady=10, sticky="n")

        select_pdf_btn = tk.Button(
            verify_frame,
            text="Wybierz PDF",
            command=lambda: select_verify_pdf(verify_frame),
            font=("Arial", 12)
        )
        select_pdf_btn.pack(pady=5)

        select_key_btn = tk.Button(
            verify_frame,
            text="Wybierz klucz publiczny",
            command=lambda: select_pub_key(verify_frame),
            font=("Arial", 12)
        )
        select_key_btn.pack(pady=5)

        run_verify_button = tk.Button(
            verify_frame,
            text="Zweryfikuj",
            command=verify_pdf_signature,
            font=("Arial", 12),
            padx=10,
            pady=5
        )
        run_verify_button.pack(pady=15)

    handle_sign()
    handle_verify()

    root.geometry("700x400")
    root.resizable(False, False)
    root.mainloop()

## @brief Punkt wejścia do aplikacji GUI.
if __name__ == "__main__":
    run_main_app()
