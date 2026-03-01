import customtkinter as ctk
from tkinter import messagebox, ttk
from src.devices.qr_scanner import WebcamScanner
from PIL import Image, ImageTk
from src.assets.img import STUDENT_ID
import cv2

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
        content.grid_columnconfigure(2, weight=1)
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
            scan_frame.grid(row=0, column=1, pady=10)
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

class TreeView(ctk.CTkFrame):
    def __init__(self, parent, height, width):
        super().__init__(parent, height=height, width=width)
        ctk.CTkLabel(
            self,
            text="Subjects", 
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(0, 10))

        # Subjects table
        self.subjects_tree = ttk.Treeview(
            self,
            columns=("Subject"),
            show="headings"
        )
        self.subjects_tree.heading("Subject", anchor="w")
        self.subjects_tree.column("Subject", anchor="w", width=200)
        self.subjects_tree.insert("", "end", values=("INPROT1",))
        self.subjects_tree.pack(expand=True, fill="both")

    def display_subjects(self, subjects):
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        for subject in subjects:
            self.subjects_tree.insert("", "end", values=(subject,))