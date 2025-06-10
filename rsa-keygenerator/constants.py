import os

## @file constants.py
#  @brief Stałe konfiguracyjne dla aplikacji podpisu cyfrowego PDF.

## @brief Ścieżka do katalogu z pendrivem zawierającym zaszyfrowany klucz prywatny.
#  Zakłada się, że pendrive jest zamontowany w dysku E ale moze sie to roznic.
PENDRIVE_PATH = "E:\\"

## @brief Pełna ścieżka do zaszyfrowanego pliku z kluczem prywatnym RSA.
PRIVATE_KEY_PATH = os.path.join(PENDRIVE_PATH, "private_encrypted.key")

## @brief Długość klucza RSA w bitach (zgodnie z wymaganiami projektu PAdES).
RSA_KEY_SIZE = 4096

## @brief Długość klucza AES w bajtach (256-bit = 32 bajty).
AES_KEY_SIZE = 32

## @brief Rozmiar wektora inicjalizującego (IV) używanego w trybie AES CBC (w bajtach).
IV_SIZE = 16

## @brief Rozmiar soli używanej w funkcji PBKDF2 do generowania klucza AES (w bajtach).
SALT_SIZE = 16
