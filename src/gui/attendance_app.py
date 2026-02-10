import customtkinter as ctk
from datetime import datetime
import json
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import sys
import os

# =====================================================
# PATH IMPORT
# =====================================================
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.sha.sha_256 import create_key as hash_key  # Your hash function

# =====================================================
# CONFIG
# =====================================================
USERS_FILE = "registered_users.JSON"

BG_COLOR = "#202020"
CARD_COLOR = "#383838"
HEADER_COLOR = "#575656"
GREY_COLOR = "#464545"
WHITE_TEXT = "#F6F9FC"
SUCCESS_COLOR = "#2E7D32"
DANGER_COLOR = "#E53935"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# =====================================================
# MAIN APP
# =====================================================
class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Attendance System")
        self.geometry("1100x600")
        self.resizable(False, False)

        self.status_text = ctk.StringVar(value="IDLE")
        self.student_id_var = ctk.StringVar()
        self.info_name = ctk.StringVar(value="---")
        self.info_time = ctk.StringVar(value="---")
        self.info_status = ctk.StringVar(value="---")

        self.build_ui()
        self.home_screen()

    # =====================================================
    # UI
    # =====================================================
    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, height=90, fg_color=HEADER_COLOR)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="MENU",
                     font=("Segoe UI", 24, "bold"),
                     text_color=WHITE_TEXT).pack(pady=25)

        # Main frame
        main = ctk.CTkFrame(self, fg_color=BG_COLOR)
        main.pack(fill="both", expand=True, padx=20, pady=15)

        # Left panel
        self.left_panel = ctk.CTkFrame(main, width=260, fg_color=CARD_COLOR)
        self.left_panel.pack(side="left", fill="y", padx=(0, 15))
        self.left_panel.pack_propagate(False)

        # Right container
        self.right_container = ctk.CTkFrame(main, fg_color=BG_COLOR)
        self.right_container.pack(side="right", fill="both", expand=True)

        self.right_panel = ctk.CTkFrame(self.right_container, fg_color=GREY_COLOR)
        self.right_panel.place(relwidth=1)

        # Status box
        self.status_box = ctk.CTkFrame(self.right_container, height=80, fg_color=CARD_COLOR)
        self.status_box.pack(side="bottom", fill="x")
        ctk.CTkLabel(self.status_box, textvariable=self.status_text,
                     font=("Segoe UI", 14, "bold")).pack(expand=True)

        # Left buttons
        self.make_btn("HOME", self.home_screen)
        self.make_btn("ID REGISTRATION", self.register_screen)
        self.make_btn("ATTENDANCE SCANNING", self.attendance_screen)
        self.make_btn("STOP SCANNING", self.stop_loading, DANGER_COLOR)

    def make_btn(self, text, cmd, color=CARD_COLOR):
        ctk.CTkButton(self.left_panel, text=text, fg_color=color, command=cmd)\
            .pack(fill="x", padx=20, pady=12)

    # =====================================================
    # JSON HANDLING
    # =====================================================
    def load_users(self):
        if not os.path.exists(USERS_FILE):
            return {}
        with open(USERS_FILE, "r") as f:
            return json.load(f)

    def save_users(self, users):
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

    # =====================================================
    # REGISTER
    # =====================================================
    def register_student_after_scan(self, qr_data, entry, btn):
        sid = self.student_id_var.get().upper()
        if not sid:
            self.status_text.set("Please enter Student ID")
            return

        users = self.load_users()
        qr_hash = hash_key(qr_data)
        users[sid] = qr_hash
        self.save_users(users)

        self.info_name.set(sid)
        self.info_status.set("REGISTERED")
        self.info_time.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_text.set("Registration success")
        self.flash_success()

        # Remove entry and button
        entry.destroy()
        btn.destroy()
        self.student_id_var.set("")

        # Ready for next scan after 1 sec
        self.after(1000, self.auto_register_scan)

    def auto_register_scan(self):
        qr_data = self.scan_qr_code()
        if not qr_data:
            self.status_text.set("QR scan failed")
            return

        users = self.load_users()
        qr_hash = hash_key(qr_data)

        if qr_hash in users.values():  # Already registered
            self.status_text.set("YOUR QR IS ALREADY REGISTERED")
            for sid, stored_hash in users.items():
                if stored_hash == qr_hash:
                    self.info_name.set(sid)
                    self.info_status.set("ALREADY REGISTERED")
                    self.info_time.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.after(2000, self.auto_register_scan)
            return

        # Not registered → show entry + submit
        entry = ctk.CTkEntry(self.right_panel, textvariable=self.student_id_var)
        entry.pack(pady=20)
        entry.focus()
        submit_btn = ctk.CTkButton(self.right_panel, text="SUBMIT",
                                   command=lambda: self.register_student_after_scan(qr_data, entry, submit_btn))
        submit_btn.pack(pady=10)

    # =====================================================
    # ATTENDANCE
    # =====================================================
    def attendance_student(self, qr_data):
        users = self.load_users()
        qr_hash = hash_key(qr_data)

        for sid, stored_hash in users.items():
            if stored_hash == qr_hash:
                self.info_name.set(sid)
                self.info_status.set("PRESENT")
                self.info_time.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.status_text.set("Attendance logged")
                self.flash_success()
                return

        self.info_name.set("---")
        self.info_status.set("NOT REGISTERED")
        self.info_time.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_text.set("Unknown QR")

    # =====================================================
    # CAMERA
    # =====================================================
    def scan_qr_code(self):
        win = CameraWindow(self)
        self.wait_window(win)
        return win.qr_data

    # =====================================================
    # SCREENS
    # =====================================================
    def home_screen(self):
        self.clear_right_panel()
        ctk.CTkLabel(self.right_panel, text="HOME",
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE_TEXT).pack(pady=15)
        self.info_row("STUDENT ID :", self.info_name)
        self.info_row("TIME :", self.info_time)
        self.info_row("STATUS :", self.info_status)

    def register_screen(self):
        self.clear_right_panel()
        ctk.CTkLabel(self.right_panel, text="ID REGISTRATION",
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE_TEXT).pack(pady=15)
        self.info_row("STUDENT ID :", self.info_name)
        self.info_row("TIME :", self.info_time)
        self.info_row("STATUS :", self.info_status)

        # Auto start camera scan
        self.after(500, self.auto_register_scan)

    def attendance_screen(self):
        self.clear_right_panel()
        ctk.CTkLabel(self.right_panel, text="ATTENDANCE SCANNING",
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE_TEXT).pack(pady=15)
        self.info_row("STUDENT ID :", self.info_name)
        self.info_row("TIME :", self.info_time)
        self.info_row("STATUS :", self.info_status)

        ctk.CTkButton(self.right_panel, text="SCAN QR",
                      command=lambda: self.attendance_scan_process()).pack(pady=20)

    def attendance_scan_process(self):
        qr_data = self.scan_qr_code()
        if not qr_data:
            self.status_text.set("QR scan failed")
            return
        self.attendance_student(qr_data)

    # =====================================================
    # HELPERS
    # =====================================================
    def clear_right_panel(self):
        for w in self.right_panel.winfo_children():
            w.destroy()

    def info_row(self, label, var):
        row = ctk.CTkFrame(self.right_panel, fg_color=GREY_COLOR)
        row.pack(anchor="w", padx=40, pady=8)
        ctk.CTkLabel(row, text=label, width=15).pack(side="left")
        ctk.CTkLabel(row, textvariable=var).pack(side="left")

    # =====================================================
    # EFFECTS
    # =====================================================
    def flash_success(self):
        self.status_box.configure(fg_color=SUCCESS_COLOR)
        self.after(400, lambda: self.status_box.configure(fg_color=CARD_COLOR))

    def stop_loading(self):
        self.status_text.set("IDLE")


# =====================================================
# CAMERA WINDOW
# =====================================================
class CameraWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.qr_data = None
        self.cap = cv2.VideoCapture(0)
        self.label = ctk.CTkLabel(self)
        self.label.pack(expand=True, fill="both")
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            codes = decode(frame)
            for code in codes:
                self.qr_data = code.data.decode()
                self.cap.release()
                self.destroy()
                return

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.label.configure(image=img)
            self.label.image = img

        self.after(10, self.update_frame)


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()