import customtkinter as ctk
from tkinter import messagebox
import ctypes
from .components.frames import HomeView, RegisterView, Menubar, Sidebar
from .components.widgets import ScanWindow
from assets.img import WINDOW_ICON
from devices.qr_scanner import cv2, USBQRScanner, WebcamScanner
from db.database import get_registered_user_by_qr, log_attendance_db, get_logs

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

SCALING_125 = ctk.set_widget_scaling(1)
DEFAULT_THEME = ctk.set_appearance_mode("light")
EXCEL_COLORS = ctk.set_default_color_theme("green")

class AttendanceApp(ctk.CTk):
    def __init__(self, file):
        super().__init__()

        self.excel = file

        self.title("Attendance System")
        self.iconbitmap(WINDOW_ICON)
        self.geometry("1920x1080")
        self.minsize(640, 480)
        self.after(1, self.maximize_on_start)

        self.custom_font = ctk.CTkFont(
            family="Segoe UI, Tahoma, sans",
            size=16,
            weight="normal"
        )

        self.menubar = Menubar(self)
        self.sidebar = Sidebar(self)

        self.init_device = self.detect_devices()
        self.home = HomeView(self, self.init_device)
        self.home.pack(expand=True, fill="both")

    def maximize_on_start(self):
        self.update_idletasks()
        self.state("zoomed")

    def detect_devices(self):
        return {
            "USB QR Scanner": USBQRScanner.is_connected("COM3"),
            "Webcam": self.check_webcam_available(0)
        }

    def check_webcam_available(self, index=0):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        available = cap.isOpened()
        cap.release()
        return available

    def open_scanner(self, device, callback=None):
        try:
            if device == "Webcam":
                scanner = WebcamScanner(cam_index=0)
            elif device == "USB QR Scanner":
                scanner = USBQRScanner(port="COM3")
            else:
                return

            if callback is None:
                callback = self.show_qr_hash

            ScanWindow(self, scanner, callback=callback)

        except Exception as e:
            messagebox.showerror("Device Error", str(e))

    def show_qr_hash(self, qr_hash):
        messagebox.showinfo("Scan Successful", f"QR Hash scanned: {qr_hash}")

    def verify_registered_qr(self, qr_hash):
        student_number = get_registered_user_by_qr(qr_hash)
        if student_number:
            if not self.excel or not self.excel.file_path:
                messagebox.showerror("No File Loaded", "Please open an Excel file first.")
                return
            session_tag = "default_session"
            log_attendance_db(student_number, session_tag)
            self.excel.sync_db_to_excel(session_tag)
            file_name = self.excel.file_path.name
            messagebox.showinfo(
                "Scan Successful",
                f"Student Number: {student_number}\n\nSaved to: {file_name}"
            )
        else:
            messagebox.showerror("Scan Denied", "QR not registered.")

    def show_home_view(self):
        if hasattr(self, "register_view"):
            self.register_view.pack_forget()
        self.home.pack(expand=True, fill="both")

    def show_register_view(self):
        if hasattr(self, "home"):
            self.home.pack_forget()
        if not hasattr(self, "register_view"):
            self.register_view = RegisterView(self)
        self.register_view.pack(expand=True, fill="both")