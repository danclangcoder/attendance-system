from pathlib import Path
from datetime import datetime
import ctypes

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk

from devices.qr_scanner import cv2, USBQRScanner, WebcamScanner
from assets.img import QR_LOGO, STUDENT_ID

from db.database import register_user, get_registered_user_by_qr

# High DPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

SCALING_125 = ctk.set_widget_scaling(1)
DEFAULT_THEME = ctk.set_appearance_mode("light")


class AttendanceApp(ctk.CTk):
    def __init__(self, local_excel, workbook):
        super().__init__()

        self.local_excel = local_excel
        self.workbook = workbook

        self.title("Attendance System")
        self.geometry("1920x1080")
        self.minsize(640, 480)
        self.after(1, self.maximize_on_start)

        self.custom_font = ctk.CTkFont(family="Segoe UI, Tahoma, sans", size=16, weight="normal")

        self.menubar = Menubar(self)
        self.sidebar = Sidebar(self)

        self.init_device = self.detect_devices()
        self.home = HomeView(self, self.init_device)
        self.home.pack(expand=True, fill="both")

    def maximize_on_start(self):
        self.update_idletasks()
        self.state("zoomed")

    def detect_devices(self):
        devices = {
            "USB QR Scanner": USBQRScanner.is_connected("COM3"),
            "Webcam": self.check_webcam_available(0)
        }
        return devices

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
            # Make sure a file is loaded
            if not self.local_excel or not self.local_excel.file_path:
                messagebox.showerror("No File Loaded", "Please open an Excel file first.")
                return

            # Save locally
            self.local_excel.log_attendance(student_number, "")

            # Save to Google sheet (if enabled)
            if self.workbook:
                self.workbook.log_attendance(
                    student_number,
                    "",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )

            # Get file name only (clean display)
            file_name = self.local_excel.file_path.name

            messagebox.showinfo(
                "Scan Successful",
                f"Student Number: {student_number}\n\nSaved to: {file_name}"
            )

        else:
            messagebox.showerror("Scan Denied", "QR not registered.")





    # View switching
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

class Menubar(tk.Menu):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open Excel File", command=self.open_file)
        file_menu.add_command(label="Set Google Sheet URL", command=self.set_google_sheet_url)
        file_menu.add_command(label="Create Google Sheet", command=self.create_google_sheet)  # new
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent_app.destroy)
        self.add_cascade(label="File", menu=file_menu)

        self.parent_app.config(menu=self)

    # ... existing open_file and set_google_sheet_url ...

    def create_google_sheet(self):
        if not hasattr(self.parent, "google_api") or not self.parent.google_api:
            messagebox.showerror("Error", "Google API not initialized")
            return

        popup = ctk.CTkToplevel(self.parent)
        popup.title("Create Google Sheet")
        popup.geometry("450x350")
        popup.transient(self.parent)
        popup.lift()
        popup.grab_set()

        font = self.parent.custom_font

        # Sheet Name
        ctk.CTkLabel(popup, text="Sheet Name:", font=font).pack(pady=(20, 5))
        sheet_entry = ctk.CTkEntry(popup, width=400, font=font)
        sheet_entry.pack(pady=(0, 10))

        # Worksheet Name
        ctk.CTkLabel(popup, text="Worksheet Name:", font=font).pack(pady=(10, 5))
        ws_entry = ctk.CTkEntry(popup, width=400, font=font)
        ws_entry.insert(0, "Sheet1")
        ws_entry.pack(pady=(0, 10))

        # Headers
        ctk.CTkLabel(popup, text="Headers (comma-separated):", font=font).pack(pady=(10, 5))
        headers_entry = ctk.CTkEntry(popup, width=400, font=font)
        headers_entry.insert(0, "Student Number,Complete Name,Timestamp")
        headers_entry.pack(pady=(0, 10))

        # Email
        ctk.CTkLabel(popup, text="Share with Email (optional):", font=font).pack(pady=(10, 5))
        email_entry = ctk.CTkEntry(popup, width=400, font=font)
        email_entry.pack(pady=(0, 10))

        def create_sheet_action():
            sheet_name = sheet_entry.get().strip()
            ws_name = ws_entry.get().strip() or "Sheet1"
            headers = [h.strip() for h in headers_entry.get().split(",")]
            email = email_entry.get().strip()

            if not sheet_name:
                messagebox.showerror("Error", "Sheet name cannot be empty.")
                return

            try:
                # Create the Google Sheet
                new_sheet = self.parent.google_api.client.create(sheet_name)
                ws = new_sheet.sheet1

                # Rename worksheet if needed
                if ws.title != ws_name:
                    ws.update_title(ws_name)

                # Update headers
                ws.update('A1:' + chr(64 + len(headers)) + '1', [headers])

                # Share with email if provided
                if email:
                    file_id = new_sheet.id  # the correct ID for the Drive API
                    self.parent.google_api.drive_service.permissions().create(
                        fileId=file_id,
                        body={'type': 'user', 'role': 'writer', 'emailAddress': email},
                        fields='id'
                    ).execute()

                messagebox.showinfo("Success", f"Google Sheet '{sheet_name}' created successfully!")
                popup.destroy()

                # Set as current workbook
                from api.google_sheets import Workbook
                self.parent.workbook = Workbook(
                    new_sheet.url, self.parent.google_api, worksheet_name=ws_name
                )

                # Refresh tree view
                self.refresh_tree()

            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to create sheet: {e}")

        ctk.CTkButton(popup, text="Create Sheet", font=font, command=create_sheet_action).pack(pady=(15, 20))

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Excel file",
            filetypes=(("Excel Files", "*.xlsx"), ("All Files", "*.*"))
        )
        if file_path:
            self.parent_app.local_excel.load_file(Path(file_path))
            messagebox.showinfo("File Loaded", f"Excel file loaded:\n{file_path}")

            
    def set_google_sheet_url(self):
        popup = ctk.CTkToplevel(self.parent_app)
        popup.title("Set Google Sheet URL")
        popup.geometry("450x220")  # taller for sheet name entry
        popup.transient(self.parent_app)
        popup.lift()
        popup.grab_set()

        ctk.CTkLabel(popup, text="Paste Google Sheet URL:", font=self.parent_app.custom_font).pack(pady=(20, 5))
        url_entry = ctk.CTkEntry(popup, width=400, font=self.parent_app.custom_font)
        url_entry.pack(pady=(0, 10))

        ctk.CTkLabel(popup, text="Worksheet Name:", font=self.parent_app.custom_font).pack(pady=(10, 5))
        sheet_entry = ctk.CTkEntry(popup, width=400, font=self.parent_app.custom_font)
        sheet_entry.insert(0, "Sheet1")  # default
        sheet_entry.pack(pady=(0, 10))

        def save_url():
            url = url_entry.get().strip()
            sheet_name = sheet_entry.get().strip() or "Sheet1"
            if not url:
                messagebox.showerror("Error", "Please enter a valid URL.")
                return
            try:
                from api.google_sheets import Workbook
                self.parent_app.workbook = Workbook(url, self.parent_app.google_api, worksheet_name=sheet_name)
                messagebox.showinfo("Success", "Google Sheet URL updated!")
                popup.destroy()
            except Exception as e:
                import traceback
                traceback.print_exc()  # shows full error in console
                messagebox.showerror("Error", f"Failed to set sheet: {e}")

        ctk.CTkButton(popup, text="Save", font=self.parent_app.custom_font, command=save_url).pack(pady=(10, 20))


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, width=300, corner_radius=0, border_width=0.2)
        self.pack(side="left", fill="y", ipady=10)

        qr_logo = ctk.CTkImage(Image.open(QR_LOGO), size=(100, 100))
        ctk.CTkLabel(master=self, text="", image=qr_logo).pack(pady=(50, 10))

        home_btn = ctk.CTkButton(
            master=self,
            text="Home",
            font=parent.custom_font,
            command=parent.show_home_view
        )
        home_btn.pack(padx=10, pady=(20, 5))

        register_btn = ctk.CTkButton(
            master=self,
            text="Register ID",
            font=parent.custom_font,
            command=parent.show_register_view
        )
        register_btn.pack(padx=10, pady=(5, 5))


class HomeView(ctk.CTkFrame):
    def __init__(self, parent, devices):
        super().__init__(parent, corner_radius=0, border_width=0.2)
        self.parent = parent
        self.pack(expand=True, fill="both", padx=20, pady=20)

        self.devices = devices
        self.display_devices = []
        self.device_map = {}

        for name, available in devices.items():
            if available:
                self.display_devices.append(name)
                self.device_map[name] = name
            else:
                label = f"{name} (Not Connected)"
                self.display_devices.append(label)
                self.device_map[label] = None

        # --- Top File Management Panel ---
        self.file_panel = ctk.CTkFrame(self, corner_radius=0)
        self.file_panel.pack(fill="x", pady=(0, 20))

        open_excel_btn = ctk.CTkButton(
            self.file_panel,
            text="Open Excel File",
            font=self.parent.custom_font,
            command=self.open_excel_file
        )
        open_excel_btn.pack(side="left", padx=5)

        create_sheet_btn = ctk.CTkButton(
            self.file_panel,
            text="Create Google Sheet",
            font=self.parent.custom_font,
            command=self.create_google_sheet
        )
        create_sheet_btn.pack(side="left", padx=5)

        load_sheet_btn = ctk.CTkButton(
            self.file_panel,
            text="Load Sheet URL",
            font=self.parent.custom_font,
            command=self.load_google_sheet
        )
        load_sheet_btn.pack(side="left", padx=5)

        refresh_btn = ctk.CTkButton(
            self.file_panel,
            text="Refresh",
            font=self.parent.custom_font,
            command=self.refresh_tree
        )
        refresh_btn.pack(side="left", padx=5)

        # --- TreeView for files ---
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(expand=True, fill="both")

        from tkinter import ttk
        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Last Scan"), show="headings")
        self.tree.heading("Type", text="File Type")
        self.tree.heading("Last Scan", text="Last Scan")
        self.tree.column("Type", width=120)
        self.tree.column("Last Scan", width=150)
        self.tree.pack(expand=True, fill="both", side="left")

        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.tree_scroll.set)
        self.tree_scroll.pack(side="right", fill="y")

        self.refresh_tree()

        # --- Existing Device Dropdown + Scan Button ---
        self.device_options = ctk.CTkOptionMenu(master=self, values=self.display_devices)
        self.device_options.place(relx=0.5, rely=1.0, anchor="s", y=-70)

        self.scan_btn = ctk.CTkButton(
            master=self,
            text="Scan ID",
            font=parent.custom_font,
            command=self.start_scan
        )
        self.scan_btn.place(relx=0.5, rely=1.0, anchor="s", y=-100)

        # Auto select first available device
        for name, available in devices.items():
            if available:
                self.device_options.set(name)
                break
        else:
            self.device_options.set(self.display_devices[0])

    # --- File Management Functions ---
    def open_excel_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select an Excel file",
            filetypes=(("Excel Files", "*.xlsx"), ("All Files", "*.*"))
        )
        if file_path:
            self.parent.local_excel.load_file(Path(file_path))
            messagebox.showinfo("File Loaded", f"Excel file loaded:\n{file_path}")
            self.refresh_tree()

    def create_google_sheet(self):
        if not hasattr(self.parent, "google_api") or not self.parent.google_api:
            messagebox.showerror("Error", "Google API not initialized")
            return

        
        sheet_name = simpledialog.askstring("New Google Sheet", "Enter Google Sheet name:")
        if not sheet_name:
            return

        try:
            # Create a new Google Sheet
            sh = self.parent.google_api.client.create(sheet_name)
            # Share with service account automatically
            self.parent.google_api.share_sheet_with_service_account(sh.id)
            messagebox.showinfo("Success", f"Google Sheet '{sheet_name}' created and shared.")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sheet: {e}")

    def load_google_sheet(self):
        url = simpledialog.askstring("Load Google Sheet", "Paste Google Sheet URL:")
        if not url:
            return
        try:
            from api.google_sheets import Workbook
            self.parent.workbook = Workbook(url, self.parent.google_api)
            messagebox.showinfo("Loaded", "Google Sheet loaded successfully.")
            self.refresh_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Google Sheet: {e}")

    def refresh_tree(self):
        # Clear existing
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Local Excel
        if hasattr(self.parent, "local_excel") and self.parent.local_excel and self.parent.local_excel.file_path:
            last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Could use actual last scan time
            self.tree.insert("", "end", values=("Local Excel", last_scan))

        # Google Sheet
        if hasattr(self.parent, "workbook") and self.parent.workbook:
            last_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Could store last scan dynamically
            self.tree.insert("", "end", values=("Google Sheet", last_scan))

    # --- Device + Scan ---
    def start_scan(self):
        selected = self.device_options.get()
        actual_device = self.device_map.get(selected)
        if not actual_device:
            messagebox.showerror("Device Error", "Selected device is not connected.")
            return
        self.parent.open_scanner(actual_device, callback=self.parent.verify_registered_qr)

class RegisterView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(expand=True, fill="both")

        ctk.CTkLabel(self, text="Enter Student Number:", font=parent.custom_font).pack(pady=(50, 10))
        self.id_entry = ctk.CTkEntry(master=self, font=parent.custom_font)
        self.id_entry.pack(pady=(0, 10))

        self.submit_btn = ctk.CTkButton(
            self,
            text="Scan QR",
            font=parent.custom_font,
            state="disabled",
            command=self.start_qr_scan
        )
        self.submit_btn.pack(pady=(0, 20))

        self.id_entry.bind("<KeyRelease>", lambda e: self.validate_input())

    def validate_input(self):
        if len(self.id_entry.get()) >= 9:
            self.submit_btn.configure(state="normal")
        else:
            self.submit_btn.configure(state="disabled")

    def start_qr_scan(self):
        selected_device = None
        devices = self.parent.init_device
        for name, available in devices.items():
            if available:
                selected_device = name
                break

        if not selected_device:
            messagebox.showerror("Device Error", "No scanning device is connected.")
            return

        self.parent.open_scanner(selected_device, callback=self.register_qr)

    def register_qr(self, qr_hash):
        student_number = self.id_entry.get()
        success = register_user(student_number, qr_hash)  # no name

        if success:
            messagebox.showinfo("Success", f"Student registered: {student_number}")
        else:
            messagebox.showerror("Error", f"Student already exists: {student_number}")

        self.id_entry.delete(0, "end")
        self.submit_btn.configure(state="disabled")


class ScanWindow(ctk.CTkToplevel):
    def __init__(self, parent, scanner, callback):
        super().__init__(parent)
        self.scanner = scanner
        self.callback = callback
        self.last_qr = None
        self.cooldown = False

        # Window properties
        self.title("QR Scanner")
        self.update_idletasks()
        self.center_on_screen(900, 700)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        content = ctk.CTkFrame(self)
        content.pack(expand=True, fill="both", padx=20, pady=20)

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        if isinstance(scanner, WebcamScanner):
            self.video_label = ctk.CTkLabel(content, text="")
            self.video_label.grid(row=0, column=1, sticky="nsew")
        else:
            scan_frame = ctk.CTkFrame(
                content,
                width=500,
                height=500,
                corner_radius=15,
                fg_color="transparent",
                border_width=3,
                border_color="#00C853"
            )
            scan_frame.grid(row=0, column=0, pady=10)
            scan_frame.grid_propagate(False)

            id_img = Image.open(STUDENT_ID)
            img = ctk.CTkImage(id_img, size=(360, 480))

            ctk.CTkLabel(scan_frame, image=img, text="").place(relx=0.5, rely=0.5, anchor="center")
            self.video_label = None

        try:
            self.scanner.open()
        except Exception as e:
            messagebox.showerror("Device Error", str(e))
            self.destroy()
            return

        self.running = True
        self.after(100, self.poll)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def poll(self):
        if not self.running:
            return

        result = self.scanner.read()

        if isinstance(self.scanner, WebcamScanner):
            frame, qr = result if result else (None, None)

            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (800, 600))
                mirrored_display = cv2.flip(frame, 1)

                img = Image.fromarray(mirrored_display)
                imgtk = ImageTk.PhotoImage(img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            if qr:
                self.on_qr_detected(qr)
        else:
            if result:
                self.on_qr_detected(result)

        self.after(15, self.poll)

    def on_qr_detected(self, qr):
        if self.cooldown or qr == self.last_qr:
            return
        self.last_qr = qr
        self.cooldown = True
        self.after(10, lambda: self.callback(qr))
        self.after(1000, self.reset)

    def reset(self):
        self.cooldown = False
        self.last_qr = None

    def on_close(self):
        self.running = False
        self.scanner.close()
        self.destroy()

    def center_on_screen(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x-100}+{y-100}")