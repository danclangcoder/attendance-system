import tkinter as tk
from tkinter import ttk
# from devices.qr_camera import scan_qr

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Attendance System")
        self.state("zoomed")
        self.minsize(640, 480)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Group widgets into a Frame widget
        start_menu = ttk.Frame(self)        
        self.init_widgets(start_menu)

    def init_widgets(self, frame):
        # Scan
        scan_button = ttk.Button(
            frame, 
            text="Scan ID (QR)",
            takefocus=False,
            command=lambda: TopWindow(self, "ID – QR Scanner", 640, 480)
        )
        scan_button.pack(side="left", ipadx=50, padx=(20, 10))

        #Register
        register_button = ttk.Button(
            frame, text="Register Students",
            takefocus=False,
            command=lambda: TopWindow(self, "Register your ID QR", 1280, 720)
        )
        register_button.pack(side="left", ipadx=50, padx=(10, 20))

class TopBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

class 

class TopWindow(tk.Toplevel):
    def __init__(self, parent, title, width, height):
        super().__init__(parent)
        self.wm_title(title)
        # self.state("zoomed")
        self.center_toplevel(width, height)
        self.minsize(width, height)

        # Modal window
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def center_toplevel(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.wm_geometry(f'{width}x{height}+{x}+{(y) - (round(y * 0.20))}')

    def on_close(self):
        self.grab_release()
        self.destroy()