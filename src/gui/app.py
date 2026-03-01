import sys
from pathlib import Path

# Add the 'src' directory to the Python module search path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as CTk
from tkinter import messagebox
import ctypes
from src.gui.components.frames import Dashboard, RegisterView, SubjectView, Menubar, Sidebar
from src.gui.components.widgets import ScanWindow
from src.assets.img import WINDOW_ICON
from src.devices.qr_scanner import cv2, USBQRScanner, WebcamScanner
from src.db.database import get_registered_user_by_qr, log_attendance_db

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

SCALING_125 = CTk.set_widget_scaling(1)
DEFAULT_THEME = CTk.set_appearance_mode("dark")
EXCEL_COLORS = CTk.set_default_color_theme("green")

class AttendanceApp(CTk.CTk):
    def __init__(self, file):
        super().__init__()

        self.excel = file

        self.title("Attendance System")
        self.iconbitmap(WINDOW_ICON)
        self.wm_iconbitmap
        self.geometry("1920x1080")
        self.minsize(640, 480)
        self.after(1, self.maximize_on_start)

        self.custom_font = CTk.CTkFont(
            family="Segoe UI, Tahoma, sans",
            size=16,
            weight="normal"
        )

        self.menubar = Menubar(self)
        self.sidebar = Sidebar(self, self.custom_font)

        self.init_device = self.detect_devices()
        self.home = Dashboard(self, self.init_device)
        self.home.pack(expand=True, fill="both")

    def maximize_on_start(self):
        self.update_idletasks()
        self.state("zoomed")
        self.after_cancel("all")  # Ensure no lingering callbacks

    def detect_devices(self):
        usb_ports = [num for num in range(1, 20)]
        usb_connected = any(USBQRScanner.is_connected(f"COM{port}") for port in usb_ports)
        
        return {
            "USB QR Scanner": usb_connected,
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
        student = get_registered_user_by_qr(qr_hash)

        if student:
            # Unpack returned student data
            student_number, last_name, first_name, section, subject = student

            if not self.excel or not self.excel.file_path:
                proceed = messagebox.askyesno(
                    "No File Loaded",
                    "No Excel file is loaded.\n\nDo you want to continue and log attendance to the database only?"
                )
                if not proceed:
                    return

                scanned = log_attendance_db(
                    student_number,
                    last_name,
                    first_name,
                    section,
                    subject
                )

                messagebox.showinfo(
                    "Scan Successful",
                    f"Student Number: {first_name} {last_name}\n\n{scanned}\n\nSaved to database only."
                )
                return

            # Log to database
            scanned = log_attendance_db(
                student_number,
                last_name,
                first_name,
                section,
                subject
            )

            file_name = self.excel.file_path.name
            messagebox.showinfo(
                "Scan Successful",
                f"Student Number: {student_number}\n\n{scanned}\n\nSaved to: {file_name}"
            )

            self.home.refresh_analytics()

        else:
            messagebox.showerror("Scan Denied", "QR not registered.")
        
        # Refresh the analytics graph (Added to dynamically update the graph after registration)
        self.home.refresh_analytics()

    def show_home_view(self):
        if hasattr(self, "register_view"):
            self.register_view.pack_forget()
        if hasattr(self, "subject_view"):
            self.subject_view.pack_forget()
        self.home.pack(expand=True, fill="both")

    def show_register_view(self):
        if hasattr(self, "home"):
            self.home.pack_forget()
        if hasattr(self, "subject_view"):
            self.subject_view.pack_forget()
        if not hasattr(self, "register_view"):
            self.register_view = RegisterView(self)
        self.register_view.pack(expand=True, fill="both")

    def show_subject_view(self):
        if hasattr(self, "home"):
            self.home.pack_forget()
        if hasattr(self, "register_view"):
            self.register_view.pack_forget()
        if not hasattr(self, "subject_view"):
            self.subject_view = SubjectView(self)
        self.subject_view.pack(expand=True, fill="both")

    def on_close(self):
        # Cancel any pending callbacks to avoid invalid command errors
        self.after_cancel("all")
        self.destroy()

if __name__ == "__main__":
    app = AttendanceApp(file=None)
    app.mainloop()