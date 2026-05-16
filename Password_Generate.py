import customtkinter as ctk
import secrets
import string
import os
import pyperclip
import sqlite3
import hashlib
import threading
import time
import csv
from cryptography.fernet import Fernet

#Appearance 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

#Main Window
app = ctk.CTk()
app.withdraw()
app.title("Secure Generator")
app.geometry("700x500")

conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               website TEXT,
               username TEXT,
               password BLOB,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
               """)
conn.commit()

key_file = "secret.key"
try:
    with open(key_file, "rb") as file:
        key = file.read()
except FileNotFoundError:
    key = Fernet.generate_key()

    with open(key_file,"wb") as file:
        file.write(key)
cipher = Fernet(key)

master_password_file = "master.key"

#password generator function
def master_login():
    login_window = ctk.CTkToplevel(app)
    login_window.title("Master Login")
    login_window.geometry("400x250")
    first_run = not os.path.exists(master_password_file)

    login_title = ctk.CTkLabel(
        login_window,
        text="Create the Master Password"
        if first_run
        else "Enter the Master Password",
        font=("Arial", 22, "bold")
    )
    login_title.pack(pady=20)

    master_entry = ctk.CTkEntry(
        login_window,
        placeholder_text="Master Password",
        show="*",
        width=250
    )
    master_entry.pack(pady=20)
    
    confirm_entry = ctk.CTkEntry(
        login_window,
        placeholder_text="Confirm Password",
        show = "*",
        width = 250
    )
    confirm_entry.pack(pady=10)

    if not first_run:
        confirm_entry.pack_forget()

    login_status = ctk.CTkLabel(
        login_window,
        text=""
    )
    login_status.pack(pady=10)

    def verify_master():

        entered_password = master_entry.get()

        hashed_password = hash_password(
            entered_password
        )


        if first_run:

            confirm_password = confirm_entry.get()

            if entered_password != confirm_password:

                login_status.configure(
                    text="Passwords do not match"
                )

                return

            with open(
                master_password_file,
                "w"
            ) as file:

                file.write(hashed_password)

            login_status.configure(
                text="Master Password Created"
            )

            app.deiconify()

            login_window.destroy()

            return

        with open(
            master_password_file,
            "r"
        ) as file:

            saved_password = file.read()

        if hashed_password == saved_password:

            login_status.configure(
                text="Access Granted"
            )

            app.deiconify()

            login_window.destroy()

        else:

            login_status.configure(
                text="Wrong Password"
            )
    login_button = ctk.CTkButton(
        login_window,
        text="Unlock Vault",
        command=verify_master
    )

    login_button.pack(pady=20)

def generate_password():
    length = int(length_slider.get())
    
    character = ""

    if uppercase_var.get():
        character += string.ascii_uppercase

    if lowercase_var.get():
        character += string.ascii_lowercase

    if numbers_var.get():
        character += string.digits

    if symbol_var.get():
        character += string.punctuation

    if not character:
        result_label.configure(text = "Select atleast one option!")
        return
    
    password = ''.join(secrets.choice(character) for _ in range(length))

    result_label.configure(text = password)

    check_password_strength(password)

def clear_clipboard_after_delay():
    time.sleep(30)
    pyperclip.copy("")

def copy_password():

    password = result_label.cget("text")

    if password != "Your password will appear here!":

        pyperclip.copy(password)

        copy_status.configure(
            text="Password Copied"
        )

        # Start clipboard auto-clear thread
        threading.Thread(
            target=clear_clipboard_after_delay,
            daemon=True
        ).start()

def check_password_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1

    if len(password) >= 10:
        score += 1

    if any(char.isupper() for char in password):
        score += 1

    if any(char.islower() for char in password):
        score += 1

    if any(char.isdigit() for char in password):
        score += 1

    if any(char in string.punctuation for char in password):
        score += 1

    strength_progress.set(score/6)

    print("Password Strength: ")

    if score <= 2:
        strength_label.configure(
        text="Strength: Weak "
)

    elif score <= 4:
        strength_label.configure(
        text="Strength: Medium"
)

    else:
        strength_label.configure(
        text="Strength: High"
)

def save_password(password):
    website = website_entry.get()
    username = username_entry.get()

    if not website or not username or not password:
        save_status.configure(
            text = "Fill all the fields!"
        )
        return

    encrypted_password = cipher.encrypt(password.encode())

    cursor.execute(
        "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
        (website, username,encrypted_password)
    )
    conn.commit()

    save_status.configure(text = "Encrypted and Saved!")

def delete_password(password_id, vault_window):
    cursor.execute(
        "DELETE FROM passwords WHERE id = ?",
        (password_id,)
    )
    conn.commit()
    vault_window.destroy()
    open_vault()

def toggle_password(password_label,actual_password,button):
    current_text = password_label.cget("text")

    if "********" in current_text:
        password_label.configure(
            text = actual_password
        )
        button.configure(text = "Hide")

    else:
        password_label.configure(text="********")
        button.configure(text="Show")

def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def copy_vault_password(password):

    pyperclip.copy(password)

    threading.Thread(
        target=clear_clipboard_after_delay,
        daemon=True
    ).start()

def export_passwords():
    cursor.execute(
        "SELECT website, username,password FROM passwords"
    )
    rows = cursor.fetchall()

    if not rows:
        save_status.configure(
            text = "No passwords to export!"
        )
        return
    with open(
        "passwords_backup.csv",
        'w',
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "Website",
            "Username",
            "Password"
        ])

        for row in rows:

            website = row[0]

            username = row[1]

            encrypted_password = row[2]

            decrypted_password = cipher.decrypt(
                encrypted_password
            ).decode()

            writer.writerow([
                website,
                username,
                decrypted_password
            ])

    save_status.configure(
        text="Passwords Exported"
    )

def open_vault():
    vault_window = ctk.CTkToplevel(app)

    vault_window.title("Password Vault")
    vault_window.geometry("600x500")

    vault_title = ctk.CTkLabel(
        vault_window,
        text="Saved Passwords",
        font=("Arial",22,"bold")
    )
    vault_title.pack(pady=20)

    search_entry = ctk.CTkEntry(
        vault_window,
        placeholder_text="Search Website"
    )
    search_entry.pack(pady=10)

    search_button = ctk.CTkButton(
        vault_window,
        text = "Search",
        command=lambda:[
            vault_window.destroy(),
            open_vault()
        ]
    )
    search_button.pack(pady=5) 

    scrollable_frame = ctk.CTkScrollableFrame(
        vault_window,
        width=450,
        height=250
    )
    scrollable_frame.pack(
        pady=10,
        padx=10,
        fill="both",
        expand=True
    )
    cursor.execute("SELECT * FROM passwords")
    rows = cursor.fetchall()

    if not rows:

        empty_label = ctk.CTkLabel(
            vault_window,
            text="No passwords saved yet!"
        )

        empty_label.pack(pady=20)

        return
    for row in rows:

        password_id = row[0]

        website = row[1]

        username = row[2]

        encrypted_password = row[3]

        decrypted_password = cipher.decrypt(
            encrypted_password
        ).decode()

        # Search filter
        search_text = search_entry.get().lower()

        if search_text and search_text not in website.lower():
            continue

        # Frame for each password
        password_frame = ctk.CTkFrame(scrollable_frame)

        password_frame.pack(
            pady=10,
            padx=10,
            fill="x"
        )

        # Password details
        details_label = ctk.CTkLabel(

        password_frame,

        text=f"""
    Website: {website}

    Username: {username}
    """,

        font=("Arial", 14),

        justify="left"
    )

        details_label.pack(
            side="left",
            padx=10,
            pady=10
        )

        # Hidden password label
        password_label = ctk.CTkLabel(

            password_frame,

            text="********",

            font=("Arial", 14)
        )

        password_label.pack(
            side="left",
            padx=10,
            pady=10
                )
        
        toggle_button = ctk.CTkButton(
            password_frame,
            text="Show",
            width=70
        )

        toggle_button.configure(
            command=lambda pl=password_label,
            dp=decrypted_password,
            btn=toggle_button:
            toggle_password(pl, dp, btn)
        )

        toggle_button.pack(
            side="right",
            padx=5
        )

        copy_button = ctk.CTkButton(

            password_frame,

            text="Copy",

            width=70,

            command=lambda pwd=decrypted_password:
            copy_vault_password(pwd)
    )

        copy_button.pack(
            side="right",
            padx=5
        )

            # Delete button
        delete_button = ctk.CTkButton(

                password_frame,

                text="Delete",

                width=80,

                command=lambda id=password_id:
                delete_password(id, vault_window)
            )

        delete_button.pack(
                side="right",
                padx=10
            )


#Title
title_label = ctk.CTkLabel(
    app,
    text = "SecurePass Generator" ,
    font = ("Arial", 24, "bold")
)
title_label.pack(pady = 20)

website_entry = ctk.CTkEntry(
    app,
    placeholder_text="Enter Website"
)
website_entry.pack(pady=10)

username_entry = ctk.CTkEntry(
    app,
    placeholder_text="Enter Username/Email"
)
username_entry.pack(pady = 10)

#length slider
length_label = ctk.CTkLabel(app,text = "Password Length")
length_label.pack()

length_slider = ctk.CTkSlider(
    app,
    from_= 4,
    to=32,
    number_of_steps=28
)

length_slider.set(12)
length_slider.pack(pady=10)

#Checkboxes
uppercase_var = ctk.BooleanVar(value=True)
lowercase_var = ctk.BooleanVar(value=True)
numbers_var = ctk.BooleanVar(value=True)
symbol_var = ctk.BooleanVar(value=True)

uppercase_checkbox = ctk.CTkCheckBox(
    app,
    text = "Uppercase Letters",
    variable = uppercase_var
)
uppercase_checkbox.pack()

lowercase_checkbox = ctk.CTkCheckBox(
    app,
    text = "Lowercase Letters",
    variable = lowercase_var
)
lowercase_checkbox.pack()

numbercase_checkbox = ctk.CTkCheckBox(
    app,
    text = "Numbercase Letters",
    variable = numbers_var
)
numbercase_checkbox.pack()

symbol_checkbox = ctk.CTkCheckBox(
    app,
    text = "Symbol Letters",
    variable = symbol_var
)
symbol_checkbox.pack()

#Generate Button
generate_button = ctk.CTkButton(
    app,
    text="Generate Password",
    command=generate_password
)

generate_button.pack(pady=20)

copy_button = ctk.CTkButton(
    app,
    text = "Copy Password",
    command=copy_password
)
copy_button.pack(pady=10)

save_button = ctk.CTkButton(
    app,
    text="Save Password",
    command=lambda: save_password(result_label.cget("text"))
)

save_button.pack(pady=10)

vault_button = ctk.CTkButton(
    app,
    text="View Vault",
    command=open_vault
)
vault_button.pack(pady=10)

export_button = ctk.CTkButton(
    app,
    text="Export Passwords",
    command=export_passwords
)
export_button.pack(pady=10)

#Result Label
result_label = ctk.CTkLabel(
    app,
    text = "Your password will appear here!",
    font=("Arial", 16)
)

result_label.pack(pady=20)

copy_status = ctk.CTkLabel(
    app,
    text="",
    font=("Arial", 14)
)
copy_status.pack()

strength_label = ctk.CTkLabel(
    app,
    text="Strength: ",
    font=("Arial",16)
)

strength_label.pack(pady=10)

strength_progress = ctk.CTkProgressBar(
    app,
    width=300
)
strength_progress.set(0)

strength_progress.pack(pady=10)

save_status = ctk.CTkLabel(
    app,
    text = "",
    font=("Arial", 14)
)

save_status.pack(pady = 5)

cursor.execute("SELECT * FROM passwords")

rows = cursor.fetchall()

# for row in rows:

#     encrypted_password = row[1]

#     decrypted_password = cipher.decrypt(encrypted_password).decode()

#     print(decrypted_password)
master_login()

app.mainloop()