import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .widgets import TreeView
from pathlib import Path
from PIL import Image
from assets.img import QR_LOGO
from db.database import register_user, add_subject, get_subjects

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, devices):
        super().__init__(parent, corner_radius=0, border_width=1, fg_color="#3a3a3a")
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

        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="#3a3a3a")
        self.scrollable_frame.pack(expand=True, fill="both", padx=0, pady=0)

        # Main title
        ctk.CTkLabel(
            self.scrollable_frame, 
            text="Main Dashboard", 
            font=("Segoe UI", 32, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 20))

        # Stats frame
        stat_frame = ctk.CTkFrame(
            self.scrollable_frame, 
            fg_color="#2d2d2d", 
            height=150, 
            corner_radius=20
        )
        stat_frame.pack(fill="x", padx=20, pady=10)
        stat_frame.pack_propagate(False)

        total_students = ctk.StringVar(value=f"{0}")
        ctk.CTkLabel(
            stat_frame,
            text=f"TOTAL REGISTERED STUDENTS \n{total_students.get()}",
            font=("Segoe UI Bold", 16),
            text_color="#6cffa9",
        ).pack(pady=(35, 0))

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#2d2d2d",
            foreground="#ffffff",
            fieldbackground="#2d2d2d",
            rowheight=30,
        )
        
        # Tables container
        self.tables_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.tables_container.pack(fill="x", padx=20, pady=10)

        # Subjects table
        subjects = get_subjects()
        self.subjects_table = TreeView(self.tables_container, height=300, width=400)
        self.subjects_table.pack(side="left", expand=True, fill="both", padx=(0, 10))
        self.subjects_table.display_subjects(subjects)

        # Students table
        self.table_frame_2 = ctk.CTkFrame(self.tables_container, height=300, width=600)
        self.table_frame_2.pack(side="left", expand=True, fill="both", padx=(10, 0))
        ctk.CTkLabel(
            self.table_frame_2,
            text="Recently Scanned Students",
            font=("Segoe UI", 24, "bold"),
        ).pack(pady=(0, 10))

        columns = ("Student No.", "Last Name", "First Name", "Section", "Timestamp")
        self.recents = ttk.Treeview(
            self.table_frame_2, 
            columns=columns, 
            show="headings"
        )
        for col in columns:
            self.recents.heading(col, text=col)
            self.recents.column(col, anchor="w", width=150)
        self.recents.pack(expand=True, fill="both")

        # Button frame inside scrollable_frame
        self.button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=20)

        # Inner frame to center buttons
        self.inner_btn_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.inner_btn_frame.pack()  # centers inner frame inside button_frame

        # Buttons inside inner frame, packed horizontally
        self.open_btn = ctk.CTkButton(
            self.inner_btn_frame,
            text="Open Excel",
            font=parent.custom_font,
            command=self.open_excel_file
        )
        self.open_btn.pack(side="left", padx=10)

        self.scan_btn = ctk.CTkButton(
            self.inner_btn_frame,
            text="Scan ID",
            font=parent.custom_font,
            command=self.start_scan
        )
        self.scan_btn.pack(side="left", padx=10)

        self.device_options = ctk.CTkOptionMenu(
            self.inner_btn_frame,
            values=self.display_devices
        )
        self.device_options.pack(side="left", padx=10)
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

        # Center the form frame inside this view
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.form_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.form_frame.grid(row=0, column=0)

        self.form_frame.columnconfigure((0, 1), weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.form_frame, text="Register Student ID:", font=parent.custom_font
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 25))

        # Student Number
        self.student_num = ctk.CTkEntry(
            self.form_frame,
            font=parent.custom_font,
            placeholder_text="Student No.",
            width=425,
        )
        self.student_num.grid(row=1, column=0, columnspan=2, pady=(0, 15))

        # Last / First Name
        self.last_name = ctk.CTkEntry(
            self.form_frame,
            font=parent.custom_font,
            placeholder_text="Last Name",
            width=200,
        )
        self.last_name.grid(row=2, column=0, padx=(0, 10), pady=10)

        self.first_name = ctk.CTkEntry(
            self.form_frame,
            font=parent.custom_font,
            placeholder_text="First Name",
            width=200,
        )
        self.first_name.grid(row=2, column=1, padx=(10, 0), pady=10)

        # Section / Subject
        self.section = ctk.CTkEntry(
            self.form_frame,
            font=parent.custom_font,
            placeholder_text="Section",
            width=200,
        )
        self.section.grid(row=3, column=0, padx=(0, 10), pady=10)

        self.subject = ctk.CTkEntry(
            self.form_frame,
            font=parent.custom_font,
            placeholder_text="Subject",
            width=200,
        )
        self.subject.grid(row=3, column=1, padx=(10, 0), pady=10)

        # Button
        self.submit_btn = ctk.CTkButton(
            self.form_frame,
            text="Scan QR",
            font=parent.custom_font,
            state="disabled",
            command=self.start_qr_scan,
            width=220,
        )
        self.submit_btn.grid(row=4, column=0, columnspan=2, pady=(25, 10))

        self.student_num.bind("<KeyRelease>", lambda e: self.validate_input())

    def validate_input(self):
        if len(self.student_num.get()) >= 9:
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
        student_number = self.student_num.get()
        last_name = self.last_name.get()
        first_name = self.first_name.get()
        section = self.section.get()
        subject = self.subject.get()

        success = register_user(student_number, qr_hash, last_name, first_name, section, subject)

        if success:
            messagebox.showinfo("Success", f"Student registered: {student_number} - {first_name} {last_name}")
        else:
            messagebox.showerror("Error", f"Student already exists: {student_number} - {first_name} {last_name}")

        self.student_num.delete(0, "end")
        self.submit_btn.configure(state="disabled")


class SubjectView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0)
        self.parent = parent
        self.pack(expand=True, fill="both")

        ctk.CTkLabel(
            self,
            text="Subjects",
            font=parent.custom_font,
        ).pack(pady=20)
        self.subject_entry = ctk.CTkEntry(
            self,
            font=parent.custom_font,
            placeholder_text="Enter subject name or code...",
            width=400,
        )
        self.subject_entry.pack(pady=10)
        ctk.CTkButton(
            self,
            text="Add",
            font=parent.custom_font,
            command=self.add_subject,
        ).pack(pady=10)

    def add_subject(self):
        subject_name = self.subject_entry.get()
        if subject_name:
            add_subject(subject_name)
            self.subject_entry.delete(0, "end")
            messagebox.showinfo("Success", f"Subject added: {subject_name}")

            # Refresh tree view in Dashboard
            subjects = get_subjects()
            if hasattr(self.parent, "home") and hasattr(self.parent.home, "subjects_table"):
                self.parent.home.subjects_table.display_subjects(subjects)
        else:
            messagebox.showerror("Error", "Please enter a subject name.")

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            width=220,
            corner_radius=0,
            border_width=1,
            border_color="#A9A9A9",
            fg_color="#3a3a3a",
        )
        self.pack(side="left", fill="y", ipady=10)
        self.pack_propagate(False)

        ctk.CTkButton(
            self,
            text="x",
            fg_color="transparent",
            width=30,
            height=30,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=10, pady=20, anchor="ne")


        qr_logo = ctk.CTkImage(Image.open(QR_LOGO), size=(100, 100))
        ctk.CTkLabel(self, text="", image=qr_logo).pack(pady=(50, 10))

        ctk.CTkButton(
            self,
            text="Home",
            anchor="w",
            font=parent.custom_font,
            fg_color="transparent",
            command=parent.show_home_view,
        ).pack(padx=10, pady=(20, 5), fill="x")

        ctk.CTkButton(
            self,
            text="Register ID",
            anchor="w",
            font=parent.custom_font,
            fg_color="transparent",
            command=parent.show_register_view,
        ).pack(padx=10, pady=(5, 5), fill="x")

        ctk.CTkButton(
            self,
            text="Add Subject",
            anchor="w",
            font=parent.custom_font,
            fg_color="transparent",
            command=parent.show_subject_view,
        ).pack(padx=10, pady=(5, 5), fill="x")


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
