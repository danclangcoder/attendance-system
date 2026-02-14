import customtkinter as ctk
import json
import os
import wmi
from datetime import datetime
import sys
sys.path.append("../db")
sys.path.append("../devices")
sys.path.append("../attendance")

from database import Database
from qr_scanner import QRScanner
from attendance_log import AttendanceLog

# Initialize database, scanner, and attendance log
self.database = Database()
self.qr_scanner = QRScanner()
self.attendance_log = AttendanceLog()

# =====================================================
#THEME
# =====================================================
BG_COLOR = "#0A0A0B"        
CARD_COLOR = "#141417"      
HEADER_COLOR = "#141417"
ACCENT_COLOR = "#007AFF"    
SUCCESS_COLOR = "#2ED573"   
DANGER_COLOR = "#FF4757"    
TEXT_MAIN = "#FFFFFF"
TEXT_DIM = "#A0A0A5"


# FONTS
FONT_MAIN = "Segoe UI Variable Display"
FONT_BOLD = "Segoe UI Variable Display Semibold"

ctk.set_appearance_mode("Dark")

class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Attendance System v3.0 - Modern Pro")
        self.geometry("1100x700")
        self.resizable(False, False)

        self.load_database()

        # Variables
        self.status_text = ctk.StringVar(value="● SYSTEM READY")
        self.student_id_input = ctk.StringVar()
        self.qr_hash_input = ctk.StringVar() 
        
        self.info_name = ctk.StringVar(value="---")
        self.info_time = ctk.StringVar(value="---")
        self.info_status = ctk.StringVar(value="---")

        self.is_scanning_active = False
        self.build_ui()
        self.home_screen()

    # =====================================================
    # HARDWARE DETECTION
    # =====================================================
    def is_qr_scanner_connected(self):
        # Use the QRScanner class to check connection
        return self.qr_scanner.is_connected()

    # =====================================================
    # DATA LOGIC
    # =====================================================
    def load_database(self):
        # Use the Database class to load data
        self.students = self.database.load_students()

    def save_to_json(self):
        # Use the Database class to save data
        self.database.save_students(self.students)

    # =====================================================
    # UI BUILDER - MODERNIZE WITH ICONS
    # =====================================================
    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, height=80, fg_color=HEADER_COLOR, corner_radius=0)
        header.pack(fill="x")

        self.menu_btn = ctk.CTkButton(header, text="☰", width=50, height=45, 
                                     font=("Arial", 22), fg_color="transparent", 
                                     hover_color="#252529", command=self.toggle_left_panel)
        self.menu_btn.pack(side="left", padx=20)

        ctk.CTkLabel(header, text="QR ATTENDANCE", 
                     font=(FONT_BOLD, 22), text_color=TEXT_MAIN).pack(side="left", padx=5)

        self.main_container = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar with ICONS PRESERVED
        self.left_panel = ctk.CTkFrame(self.main_container, width=280, fg_color=HEADER_COLOR, corner_radius=0)
        self.left_panel.pack_propagate(False)

        self.make_nav_btn("DASHBOARD", "🏠", self.home_screen)
        self.make_nav_btn("REGISTRATION", "📝", self.register_screen)
        self.make_nav_btn("SCAN ATTENDANCE", "📡", self.check_device_and_start_attendance)
        self.make_nav_btn("STOP SYSTEM", "🛑", self.stop_loading, hover_color=DANGER_COLOR)

        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=40, pady=30)

        # Footer
        self.status_box = ctk.CTkFrame(self, height=45, fg_color=HEADER_COLOR, corner_radius=0)
        self.status_box.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(self.status_box, textvariable=self.status_text, 
                                        font=(FONT_BOLD, 12), text_color=TEXT_DIM)
        self.status_label.pack(expand=True)

        self.left_panel_visible = False

    def make_nav_btn(self, text, icon, cmd, hover_color=None):
        btn = ctk.CTkButton(self.left_panel, text=f"  {icon}   {text}", height=65, corner_radius=0,
                            fg_color="transparent", anchor="w", 
                            font=(FONT_BOLD, 14),
                            hover_color=hover_color if hover_color else "#1E1E22", command=cmd)
        btn.pack(fill="x", padx=10, pady=2)

    def toggle_left_panel(self):
        if self.left_panel_visible: self.left_panel.pack_forget()
        else: self.left_panel.pack(side="left", fill="y")
        self.left_panel_visible = not self.left_panel_visible

    def clear_right_panel(self):
        self.is_scanning_active = False
        for w in self.right_panel.winfo_children(): w.destroy()

    # =====================================================
    # DASHBOARD
    # =====================================================
    def home_screen(self):
        self.clear_right_panel()
        ctk.CTkLabel(self.right_panel, text="Overview", 
                     font=(FONT_BOLD, 36), text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 25))
        
        stat_frame = ctk.CTkFrame(self.right_panel, fg_color=CARD_COLOR, height=160, corner_radius=24)
        stat_frame.pack(fill="x", pady=10)
        stat_frame.pack_propagate(False)
        
        ctk.CTkLabel(stat_frame, text="TOTAL ENROLLED STUDENTS", 
                     font=(FONT_BOLD, 12), text_color=ACCENT_COLOR).pack(pady=(40,0))
        ctk.CTkLabel(stat_frame, text=str(len(self.students)), 
                     font=(FONT_BOLD, 64), text_color=TEXT_MAIN).pack()

        ctk.CTkLabel(self.right_panel, text="Recent Activity", 
                     font=(FONT_BOLD, 18)).pack(anchor="w", pady=(30, 15))
        
        scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        for s in reversed(self.students):
            f = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, height=65, corner_radius=16)
            f.pack(fill="x", pady=6, padx=2)
            ctk.CTkLabel(f, text=f"   ID: {s['id']}", font=(FONT_BOLD, 15)).pack(side="left", padx=15)
            ctk.CTkLabel(f, text=f"{s['date']}   ", font=(FONT_MAIN, 12), text_color=TEXT_DIM).pack(side="right", padx=15)

    # =====================================================
    # REGISTRATION
    # =====================================================
    def register_screen(self):
        self.clear_right_panel()
        self.student_id_input.set("")
        ctk.CTkLabel(self.right_panel, text="New Registration", 
                     font=(FONT_BOLD, 36)).pack(anchor="w", pady=(0, 35))
        
        form_card = ctk.CTkFrame(self.right_panel, fg_color=CARD_COLOR, corner_radius=24)
        form_card.pack(fill="x")

        inner = ctk.CTkFrame(form_card, fg_color="transparent")
        inner.pack(padx=60, pady=50, fill="both")

        ctk.CTkLabel(inner, text="ASSIGN STUDENT ID", 
                     font=(FONT_BOLD, 12), text_color=ACCENT_COLOR).pack(anchor="w")
        self.id_entry = ctk.CTkEntry(inner, textvariable=self.student_id_input, height=60, 
                                     placeholder_text="Enter Unique ID...", 
                                     font=(FONT_MAIN, 18), 
                                     fg_color=BG_COLOR, border_width=0, corner_radius=12)
        self.id_entry.pack(pady=(12, 30), fill="x")
        self.id_entry.focus_set()

        ctk.CTkButton(inner, text="NEXT: SCAN QR CODE", fg_color=ACCENT_COLOR, height=60, 
                      font=(FONT_BOLD, 16), corner_radius=12, 
                      command=self.lock_id_and_wait_qr).pack(fill="x")

    # =====================================================
    # ATTENDANCE (SCANNING MODE)
    # =====================================================
    def check_device_and_start_attendance(self):
        self.clear_right_panel()
        self.info_name.set("---")
        self.info_time.set("---")
        self.info_status.set("IDLE")

        ctk.CTkLabel(self.right_panel, text="Scan Mode", 
                     font=(FONT_BOLD, 36)).pack(anchor="w", pady=(0, 35))
        
        if self.is_qr_scanner_connected():
            self.is_scanning_active = True
            self.status_text.set("● SCANNER ACTIVE")
            self.flash_feedback(SUCCESS_COLOR)

            display_card = ctk.CTkFrame(self.right_panel, fg_color=CARD_COLOR, corner_radius=28, padding=40)
            display_card.pack(fill="x")

            self.info_row_ui(display_card, "STUDENT ID", self.info_name)
            self.info_row_ui(display_card, "LOG TIME", self.info_time)
            self.info_row_ui(display_card, "SYSTEM STATUS", self.info_status)

            self.attendance_catcher = ctk.CTkEntry(self.right_panel, textvariable=self.qr_hash_input, width=0, height=0, border_width=0)
            self.attendance_catcher.pack()
            self.attendance_catcher.focus_set()
            self.attendance_catcher.bind("<Return>", lambda e: self.process_attendance())
        else:
            self.status_text.set("● HARDWARE ERROR")
            self.flash_feedback(DANGER_COLOR)
            
            error_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
            error_frame.pack(expand=True)
            ctk.CTkLabel(error_frame, text="⚠️", font=("Arial", 80)).pack()
            ctk.CTkLabel(error_frame, text="DEVICE NOT FOUND", font=(FONT_BOLD, 24), text_color=DANGER_COLOR).pack(pady=10)
            ctk.CTkLabel(error_frame, text="Connect your hardware scanner to begin.", 
                         font=(FONT_MAIN, 14), text_color=TEXT_DIM).pack()

    def process_attendance(self):
        if not self.is_scanning_active:
            return

        scanned_hash = self.qr_hash_input.get().strip()
        self.qr_hash_input.set("")

        # Use the QRScanner class to process the scanned QR code
        student_id = self.qr_scanner.process_qr_code(scanned_hash)

        if student_id:
            now = datetime.now().strftime("%I:%M:%S %p")
            self.info_name.set(student_id)
            self.info_time.set(now)
            self.info_status.set("SUCCESSFULLY SCANNED")
            self.status_text.set(f"● WELCOME {student_id}")
            self.flash_feedback(SUCCESS_COLOR)
        else:
            self.info_name.set("UNKNOWN")
            self.info_time.set("---")
            self.info_status.set("FAILED / NOT REGISTERED")
            self.status_text.set("● UNRECOGNIZED QR CODE")
            self.flash_feedback(DANGER_COLOR)

        self.attendance_catcher.focus_set()

    # =====================================================
    # UTILITIES
    # =====================================================
    def lock_id_and_wait_qr(self):
        sid = self.student_id_input.get().strip().upper()
        if not sid: return
        if not self.is_qr_scanner_connected():
            self.status_text.set("● ERROR: DISCONNECTED")
            self.flash_feedback(DANGER_COLOR)
            return

        self.is_scanning_active = True
        self.status_text.set(f"● READY FOR ID {sid}")
        
        self.qr_hidden_entry = ctk.CTkEntry(self.right_panel, textvariable=self.qr_hash_input, width=0, height=0, border_width=0)
        self.qr_hidden_entry.pack()
        self.qr_hidden_entry.focus_set() 
        self.qr_hidden_entry.bind("<Return>", lambda e: self.complete_registration())

    def complete_registration(self):
        sid = self.student_id_input.get().strip().upper()
        h_data = self.qr_hash_input.get().strip()
        if h_data:
            self.students.append({"id": sid, "qr_hash": h_data, "date": datetime.now().strftime("%Y-%m-%d %H:%M")})
            self.save_to_json()
            self.flash_feedback(SUCCESS_COLOR)
            self.status_text.set(f"● REGISTERED {sid}")
            self.after(1000, self.register_screen)

    def info_row_ui(self, parent, label, var):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=18)
        ctk.CTkLabel(row, text=label, font=(FONT_BOLD, 12), width=220, anchor="w", text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(row, textvariable=var, font=(FONT_BOLD, 22), text_color=TEXT_MAIN).pack(side="left")

    def flash_feedback(self, color):
        self.status_box.configure(fg_color=color)
        self.after(600, lambda: self.status_box.configure(fg_color=HEADER_COLOR))

    def stop_loading(self):
        self.is_scanning_active = False
        self.status_text.set("● STANDBY")
        self.home_screen()

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
                                                                  