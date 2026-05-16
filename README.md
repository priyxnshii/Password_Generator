# 🔐 SecurePass - Password Manager

SecurePass is a desktop password manager built with Python and CustomTkinter that securely generates, stores, encrypts, and manages passwords using a modern GUI.

---

## Features

- Secure password generation
- Password strength checker
- Master login authentication
- Encrypted password storage
- SQLite database integration
- Password vault
- Show/Hide password
- Copy password functionality
- Auto-clear clipboard security
- Search saved passwords
- Delete saved passwords
- Export passwords to CSV
- Scrollable vault UI
- Modern CustomTkinter interface

---

## Technologies Used

- Python
- CustomTkinter
- SQLite3
- Cryptography (Fernet)
- hashlib
- pyperclip
- PyInstaller

---

## Installation

Clone repository:

```bash
git clone <your-repo-link>
```

Move into folder:

```bash
cd SecurePass
```

Install dependencies:

```bash
pip install customtkinter
pip install pyperclip
pip install cryptography
```

Run application:

```bash
python Password_Generate.py
```

---

## Convert To EXE

```bash
pyinstaller --onefile --windowed Password_Generate.py
```

---

## Project Structure

```plaintext
SecurePass/
│
├── Password_Generate.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── passwords.db
├── master.key
├── secret.key
```

---

## Screenshots

Add screenshots here:

Main Application UI

Vault Window

Master Login Screen

---

## Future Improvements

- Breach checker API
- Cloud synchronization
- OTP verification
- Dark/Light theme switching
- Password categories
