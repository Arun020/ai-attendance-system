import customtkinter as ctk
import subprocess
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import simpledialog, messagebox

import requests
import certifi
import urllib3

# 🔥 FIX: suppress SSL warnings (safe for demo)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from session_store import set_session, get_token


# -----------------------------
# THEME
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -----------------------------
# MAIN WINDOW
# -----------------------------
app = ctk.CTk()
app.title("AI Attendance System")
app.state("zoomed")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


# -----------------------------
# GLOBAL ROLE
# -----------------------------
CURRENT_ROLE = None


# -----------------------------
# POPUP INPUT
# -----------------------------
def ask_topmost(title, prompt):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    value = simpledialog.askstring(title, prompt, parent=root)

    root.destroy()
    return value


# -----------------------------
# LOGIN (FIXED SSL ISSUE HERE)
# -----------------------------
def login_user():

    global CURRENT_ROLE

    email = ask_topmost("Login", "Enter Email")
    password = ask_topmost("Login", "Enter Password")

    if not email or not password:
        return

    try:
        response = requests.post(
            "https://ai-attendance-system-edyg.onrender.com/login",
            json={"email": email, "password": password},
            verify=False,   # 🔥 FINAL FIX (prevents SSL crash)
            timeout=10
        )

        data = response.json()

        token = data.get("access_token")
        role = data.get("role")

        if not token:
            messagebox.showerror("Login Failed", str(data))
            return

        set_session(token, role)
        CURRENT_ROLE = role

        messagebox.showinfo("Login Success", f"Role: {role}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -----------------------------
# CHECK LOGIN
# -----------------------------
def ensure_login():
    if not get_token():
        messagebox.showwarning("Warning", "Please login first!")
        return False
    return True


# -----------------------------
# START ATTENDANCE
# -----------------------------
def start_attendance():

    if not ensure_login():
        return

    window = tk.Toplevel(app)
    window.title("Select Mode")
    window.geometry("300x180")
    window.attributes("-topmost", True)

    tk.Label(window, text="Select Attendance Mode",
             font=("Arial", 14, "bold")).pack(pady=10)

    def college_mode():

        if CURRENT_ROLE not in ["admin", "teacher", "student"]:
            messagebox.showerror("Access Denied", "Not allowed for this role")
            return

        window.destroy()

        subject = ask_topmost("College Mode", "Enter Subject Name")
        teacher = ask_topmost("College Mode", "Enter Teacher Name")

        token = get_token()

        subprocess.Popen([
            sys.executable,
            os.path.join(SCRIPTS_DIR, "attendance_system.py"),
            "college",
            subject or "",
            teacher or "",
            token or ""
        ])

    def corporate_mode():

        if CURRENT_ROLE not in ["admin", "hr"]:
            messagebox.showerror("Access Denied", "Not allowed for this role")
            return

        window.destroy()

        token = get_token()

        subprocess.Popen([
            sys.executable,
            os.path.join(SCRIPTS_DIR, "attendance_system.py"),
            "corporate",
            "",
            "",
            token or ""
        ])

    tk.Button(window, text="College", width=20, command=college_mode).pack(pady=10)
    tk.Button(window, text="Corporate", width=20, command=corporate_mode).pack(pady=5)


# -----------------------------
# CAPTURE FACES
# -----------------------------
def capture_faces():

    name = ask_topmost("Input", "Enter Student Name")

    if not name:
        return

    subprocess.Popen([
        sys.executable,
        os.path.join(SCRIPTS_DIR, "capture_faces.py"),
        str(name)
    ])


# -----------------------------
# TRAIN MODEL
# -----------------------------
def train_model():

    subprocess.Popen([
        sys.executable,
        os.path.join(SCRIPTS_DIR, "train_model.py")
    ])


# -----------------------------
# VIEW ATTENDANCE
# -----------------------------
def view_attendance():

    role = CURRENT_ROLE

    if not role:
        messagebox.showwarning("Warning", "Please login first!")
        return

    if role == "admin":

        popup = tk.Toplevel(app)
        popup.title("Dashboard")
        popup.geometry("300x200")
        popup.attributes("-topmost", True)

        tk.Label(popup, text="Select Dashboard",
                 font=("Arial", 14, "bold")).pack(pady=10)

        def open_college():
            webbrowser.open("https://ai-attendance-system-edyg.onrender.com/college-ui")
            popup.destroy()

        def open_corporate():
            webbrowser.open("https://ai-attendance-system-edyg.onrender.com/corporate-ui")
            popup.destroy()

        tk.Button(popup, text="College Dashboard",
                  width=25, command=open_college).pack(pady=10)

        tk.Button(popup, text="Corporate Dashboard",
                  width=25, command=open_corporate).pack(pady=5)

        return

    if role == "teacher":
        webbrowser.open("https://ai-attendance-system-edyg.onrender.com/college-ui")
        return

    if role == "hr":
        webbrowser.open("https://ai-attendance-system-edyg.onrender.com/corporate-ui")
        return

    messagebox.showerror("Access Denied", "No dashboard access")


# -----------------------------
# VIEW DEFAULTERS
# -----------------------------
def view_defaulters():

    role = CURRENT_ROLE

    if not role:
        messagebox.showwarning("Warning", "Please login first!")
        return

    if role == "admin":

        popup = tk.Toplevel(app)
        popup.title("Defaulters")
        popup.geometry("300x200")
        popup.attributes("-topmost", True)

        tk.Label(popup, text="Select Defaulter List",
                 font=("Arial", 14, "bold")).pack(pady=10)

        def open_college():
            webbrowser.open("https://ai-attendance-system-edyg.onrender.com/college-defaulters")
            popup.destroy()

        def open_corporate():
            webbrowser.open("https://ai-attendance-system-edyg.onrender.com/corporate-defaulters")
            popup.destroy()

        tk.Button(popup, text="College Defaulters",
                  width=25, command=open_college).pack(pady=10)

        tk.Button(popup, text="Corporate Defaulters",
                  width=25, command=open_corporate).pack(pady=5)

        return


# -----------------------------
# EXIT
# -----------------------------
def exit_application():
    app.destroy()
    os._exit(0)


# -----------------------------
# UI DESIGN (UNCHANGED)
# -----------------------------
main_frame = ctk.CTkFrame(app, corner_radius=20)
main_frame.pack(pady=30, padx=30, fill="both", expand=True)

title = ctk.CTkLabel(main_frame, text="AI Attendance Dashboard",
                     font=("Arial", 34, "bold"))
title.pack(pady=25)

button_frame = ctk.CTkFrame(main_frame)
button_frame.pack(pady=20)

ctk.CTkButton(button_frame, text="Login (JWT)",
              width=250, height=50, command=login_user).grid(row=0, column=0, padx=20, pady=15)

ctk.CTkButton(button_frame, text="Start Attendance",
              width=250, height=50, command=start_attendance).grid(row=0, column=1, padx=20, pady=15)

ctk.CTkButton(button_frame, text="Capture Faces",
              width=250, height=50, command=capture_faces).grid(row=1, column=0, padx=20, pady=15)

ctk.CTkButton(button_frame, text="Train Model",
              width=250, height=50, command=train_model).grid(row=1, column=1, padx=20, pady=15)

ctk.CTkButton(button_frame, text="View Attendance",
              width=520, height=50, command=view_attendance,
              fg_color="#2e8b57").grid(row=2, column=0, columnspan=2, pady=20)

ctk.CTkButton(button_frame, text="View Defaulters",
              width=520, height=50, command=view_defaulters,
              fg_color="#b22222").grid(row=3, column=0, columnspan=2, pady=10)

ctk.CTkButton(main_frame, text="Exit",
              width=300, height=50, fg_color="red",
              hover_color="darkred", command=exit_application).pack(pady=20)

app.mainloop()