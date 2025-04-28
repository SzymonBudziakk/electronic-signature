import tkinter as tk
from tkinter import filedialog, messagebox
import os

PENDRIVE_PATH = "D:\\private_encrypted.key"

def check_pendrive():
    return os.path.exists(PENDRIVE_PATH)

def run_main_app():
    def select_pdf():
        file_path = filedialog.askopenfilename(
            title="Wybierz plik PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            selected_file_label.config(text=f"Wybrany plik: {os.path.basename(file_path)}")
            app_state["pdf_path"] = file_path

    def check_and_show_status():
        if check_pendrive():
            status_label.config(text="✅ Pendrive wykryty", fg="green")
        else:
            status_label.config(text="❌ Pendrive nie znaleziony", fg="red")

    def on_submit():
        pin = pin_entry.get()
        if not pin:
            messagebox.showerror("Błąd", "PIN nie może być pusty.")
            return

        if not app_state["pdf_path"]:
            messagebox.showerror("Błąd", "Nie wybrano pliku PDF.")
            return

        if not check_pendrive():
            messagebox.showerror("Błąd", "Pendrive nie został wykryty.")
            return

        # logika podpisywania pdf tutaj
        messagebox.showinfo("Informacja", "Wszystko gotowe do podpisu!")

    app_state = {"pdf_path": None}

    root = tk.Tk()
    root.title("Aplikacja podpisu PDF")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True)

    select_pdf_button = tk.Button(
        frame,
        text="Wybierz plik PDF",
        command=select_pdf,
        font=("Arial", 12)
    )
    select_pdf_button.grid(row=0, column=0, pady=10)

    selected_file_label = tk.Label(
        frame,
        text="Nie wybrano pliku.",
        font=("Arial", 10)
    )
    selected_file_label.grid(row=1, column=0, pady=5)

    tk.Label(frame, text="Wprowadź PIN:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=(10, 0))
    pin_entry = tk.Entry(
        frame,
        show="*",
        font=("Arial", 14),
        width=30
    )
    pin_entry.grid(row=3, column=0, pady=5)

    check_pendrive_button = tk.Button(
        frame,
        text="Sprawdź pendrive",
        command=check_and_show_status,
        font=("Arial", 12)
    )
    check_pendrive_button.grid(row=4, column=0, pady=10)

    status_label = tk.Label(
        frame,
        text="Status pendrive: Nie sprawdzono",
        font=("Arial", 10)
    )
    status_label.grid(row=5, column=0, pady=5)

    submit_button = tk.Button(
        frame,
        text="Kontynuuj",
        command=on_submit,
        font=("Arial", 12),
        padx=10,
        pady=5
    )
    submit_button.grid(row=6, column=0, pady=20)

    root.geometry("450x400")
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    run_main_app()
