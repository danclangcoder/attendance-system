from devices.qr_scanner import USBQRScanner, WebcamScanner, cv2
import customtkinter as ctk
from CTkMenuBar import *
from tkinter import messagebox
from PIL import Image, ImageTk
import ctypes

# =========================
# DPI AWARENESS (WINDOWS)
# =========================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

"""
--------------DARK THEME----------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
-----------------COLORS-----------------
    BG = "#0F1115"
    SIDEBAR = "#16181D"
    CARD = "#1A1D23"
    TEXT = "#E6EAF2"
    TEXT_MUTED = "#9AA0AA"
    ACCENT = "#3B82F6"
    SUCCESS = "#22C55E"
    DANGER = "#EF4444"
----------------------------------------
"""

DARK_MODE = ctk.set_appearance_mode("dark")
SCALING_125 = ctk.set_widget_scaling(1.25)

class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Attendance System")
        self.geometry("1920x1080")
        self.minsize(640, 480)
        self.after(1, self.maximize_on_start)

        self.custom_font = ctk.CTkFont(
            family="Segoe UI, Tahoma, sans",
            size=10,
            weight="normal"
        )

        # ---------Topbar----------
        self.menubar = Menubar(self)

        # ---------Sidebar----------
        self.sidebar = Sidebar(self)

        # ---------Main Content-----
        self.main_frame = Main(self)
        
    def maximize_on_start(self):
        self.update_idletasks()
        self.state("zoomed")

    def open_scanner(self, device):

        if device == "Webcam":
            scanner = WebcamScanner()
        else:
            scanner = USBQRScanner(port="COM3")

        ScanWindow(self, scanner, callback=self.on_scan_complete)


    def on_scan_complete(self, qr):
        messagebox.showinfo("Scan Successful", qr)

    def clear_content(self, frame):
        for w in frame.winfo_children():
            w.destroy()
    
    def validate_input(self):
        minimum_chars = 9 
        if len(self.id_entry.get()) >= minimum_chars:
            self.submit_btn.configure(state="normal")
        else:
            self.submit_btn.configure(state="disabled")

    def submit(self):
        print("Submitted:", self.id_entry.get())

class Menubar(CTkMenuBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(bg_color="#313131")

        # Menus
        self.file_menu = self.add_cascade("File")
        self.help_menu = self.add_cascade("Help")
        
class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(
            width=300, 
            corner_radius=0, 
            border_color="#444444", 
            border_width=0.5
        )
        self.pack(side="left", fill="y", ipady=10)

        qr_logo = ctk.CTkImage(Image.open("src/images/qr-code.png"), size=(100, 100))
        ctk.CTkLabel(master=self, text="", image=qr_logo).pack(pady=(50, 10))

        home_btn = ctk.CTkButton(
            master=self,
            text="Home",
            font=parent.custom_font,
            fg_color="transparent",
            hover_color="#444444"
        )
        home_btn.pack(padx=10, pady=(20, 5))

        register_btn = ctk.CTkButton(
            master=self,
            text="Register ID",
            font=parent.custom_font,
            fg_color="transparent",
            hover_color="#444444"
        )
        register_btn.pack(padx=10, pady=(5, 5))

class Main(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.pack(expand=True, fill="both")

        self.device_options = ctk.CTkOptionMenu(
            master=self,
            values=["USB QR Scanner", "Webcam"]
        )
        self.device_options.set("USB QR Scanner")
        self.device_options.place(relx=0.5, rely=1.0, anchor="s", y=-70)

        scan_btn = ctk.CTkButton(
            master=self,
            text="Scan ID",
            command=self.start_scan
        )
        scan_btn.place(relx=0.5, rely=1.0, anchor="s", y=-100)

    def start_scan(self):
        device = self.device_options.get()
        self.parent.open_scanner(device)

class ScanWindow(ctk.CTkToplevel):
    def __init__(self, parent, scanner, callback):
        super().__init__(parent)

        self.scanner = scanner
        self.callback = callback

        # Window Properties
        self.title("QR Scanner")
        self.center_on_screen()
        self.geometry("1280x720")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Layout
        content = ctk.CTkFrame(self)
        content.pack(expand=True, fill="both", padx=20, pady=20)

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        # Widgets
        id_img = Image.open("src/images/Student-ID-Sample.png")
        self.img = ctk.CTkImage(id_img, id_img, size=(180, 300))

        ctk.CTkLabel(
            content,
            image=self.img,
            text=""
        ).grid(row=0, column=0, padx=20, pady=10, sticky="n")

        self.video_label = ctk.CTkLabel(content, text="")
        self.video_label.grid(row=0, column=1, padx=20, pady=10, sticky="n")

        self.status = ctk.CTkLabel(
            self, 
            text="Place and align your ID QR on the scanner."
        )
        self.status.pack(pady=(0, 10))

        try:
            self.scanner.open()
        except Exception as e:
            messagebox.showerror("Device is not connected.", str(e))
            self.destroy()
            return

        self.running = True
        self.after(100, self.poll)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def poll(self):
        if not self.running:
            return

        result = self.scanner.read()
        
        if isinstance(result, tuple):
            frame, qr = result
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            if qr:
                self.on_qr_detected(qr)
                return
            
        elif result:
            self.on_qr_detected(result)
            return

        self.after(15, self.poll)

    def on_qr_detected(self, qr):
        self.running = False
        self.scanner.close()
        self.callback(qr)
        self.destroy()

    def on_close(self):
        self.running = False
        self.scanner.close()
        self.destroy()
                
    def center_on_screen(self):
        self.update_idletasks()

        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        x = (sw - w) // 2
        y = (sh - h) // 2

        self.geometry(f"+{x - 800}+{y - 400}")