import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image
from assets.img import QR_LOGO
from db.database import register_user


class HomeView(ctk.CTkFrame):
    def __init__(self, parent, devices):
        super().__init__(
            parent, corner_radius=0, border_width=1, border_color="#A9A9A9"
        )
        self.parent = parent
        self.pack(expand=True, fill="both")

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

        # Treeview | Attendance Table Frame
        self.table_frame = ctk.CTkFrame(self, height=300, width=400)
        self.table_frame.place(relx=0.5, rely=0, anchor="n", y=50)

        columns = ("Student Number", "Timestamp")
        self.tree = ttk.Treeview(
            self.table_frame, columns=columns, show="headings", height=20
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=400)
        self.tree.pack(expand=True, fill="both")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.place(relx=0.5, rely=0.5, anchor="center", y=20)

        self.open_btn = ctk.CTkButton(
            self.button_frame,
            text="Open Excel",
            font=self.parent.custom_font,
            command=self.open_excel_file,
        )
        self.open_btn.grid(row=0, column=0, padx=10)

        self.scan_btn = ctk.CTkButton(
            self.button_frame,
            text="Scan ID",
            font=parent.custom_font,
            command=self.start_scan,
        )
        self.scan_btn.grid(row=0, column=1, padx=10)

        self.device_options = ctk.CTkOptionMenu(
            self.button_frame, values=self.display_devices
        )
        self.device_options.grid(row=0, column=2, padx=10)
        for name, available in devices.items():
            if available:
                self.device_options.set(name)
                break
        else:
            self.device_options.set(self.display_devices[0])

    def open_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Excel file",
            filetypes=(("Excel Files", "*.xlsx"), ("All Files", "*.*")),
        )
        if file_path:
            self.parent.excel.load_file(Path(file_path))
            messagebox.showinfo("File Loaded", f"Excel file loaded:\n{file_path}")

    def refresh_table(self, session_tag="default_session"):
        from db.database import get_logs

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        logs = get_logs(session_tag)

        for log in logs:
            student_number = log[0]
            timestamp = log[1]
            self.tree.insert("", "end", values=(student_number, timestamp))

    def start_scan(self):
        selected = self.device_options.get()
        actual_device = self.device_map.get(selected)
        if not actual_device:
            messagebox.showerror("Device Error", "Selected device is not connected.")
            return
        self.parent.open_scanner(
            actual_device, callback=self.parent.verify_registered_qr
        )


class RegisterView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent
        self.pack(expand=True, fill="both")

        ctk.CTkLabel(self, text="Enter Student Number:", font=parent.custom_font).pack(
            pady=(50, 10)
        )
        self.id_entry = ctk.CTkEntry(master=self, font=parent.custom_font)
        self.id_entry.pack(pady=(0, 10))

        self.submit_btn = ctk.CTkButton(
            self,
            text="Scan QR",
            font=parent.custom_font,
            state="disabled",
            command=self.start_qr_scan,
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
        success = register_user(student_number, qr_hash)

        if success:
            messagebox.showinfo("Success", f"Student registered: {student_number}")
        else:
            messagebox.showerror("Error", f"Student already exists: {student_number}")

        self.id_entry.delete(0, "end")
        self.submit_btn.configure(state="disabled")


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent, width=300, corner_radius=0, border_width=1, border_color="#A9A9A9"
        )
        self.pack(side="left", fill="y", ipady=10)

        qr_logo = ctk.CTkImage(Image.open(QR_LOGO), size=(100, 100))
        ctk.CTkLabel(self, text="", image=qr_logo).pack(pady=(50, 10))

        ctk.CTkButton(
            self, text="Home", font=parent.custom_font, command=parent.show_home_view
        ).pack(padx=10, pady=(20, 5))

        ctk.CTkButton(
            self,
            text="Register ID",
            font=parent.custom_font,
            command=parent.show_register_view,
        ).pack(padx=10, pady=(5, 5))


class Menubar(tk.Menu):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open Excel File", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.parent_app.destroy)
        self.add_cascade(label="File", menu=file_menu)
        self.parent_app.config(menu=self)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Excel file",
            filetypes=(("Excel Files", "*.xlsx"), ("All Files", "*.*")),
        )
        if file_path:
            self.parent_app.local_excel.load_file(Path(file_path))
            messagebox.showinfo("File Loaded", f"Excel file loaded:\n{file_path}")
