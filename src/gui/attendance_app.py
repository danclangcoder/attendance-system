import customtkinter as ctk
import json
import os
import wmi
from datetime import datetime

# =====================================================
# CONFIG & THEME - REFINED COLORS
# =====================================================
BG_COLOR = "#0F0F10"        
CARD_COLOR = "#1C1C1E"      
HEADER_COLOR = "#161617"
ACCENT_COLOR = "#007AFF"    
SUCCESS_COLOR = "#28A745"
DANGER_COLOR = "#FF3B30"
TEXT_MAIN = "#FFFFFF"
TEXT_DIM = "#8E8E93"
DB_FILE = "attendance_db.json"

ctk.set_appearance_mode("Dark")

class AttendanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR Attendance System v3.0 - Professional")
        self.geometry("1100x680")
        self.resizable(False, False)

        self.load_database()

        # Variables
        self.status_text = ctk.StringVar(value="SYSTEM IDLE")
        self.student_id_input = ctk.StringVar()
        self.qr_hash_input = ctk.StringVar() 
        
        self.info_name = ctk.StringVar(value="---")
        self.info_time = ctk.StringVar(value="---")
        self.info_status = ctk.StringVar(value="---")

        self.is_scanning_active = False
        
        # UI State
        self.left_panel_visible = False # Naka-set sa False para hidden sa simula
        
        self.build_ui()
        self.home_screen()

    def is_qr_scanner_connected(self):
        try:
            c = wmi.WMI()
            for device in c.Win32_PnPEntity():
                device_name = str(device.Name).lower()
                if any(keyword in device_name for keyword in ["scanner", "barcode", "symbol", "zebra", "honeywell"]):
                    return True
            return False
        except:
            return False

    def load_database(self):
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w") as f: json.dump([], f)
            self.students = []
        else:
            with open(DB_FILE, "r") as f: self.students = json.load(f)

    def save_to_json(self):
        with open(DB_FILE, "w") as f: json.dump(self.students, f, indent=4)

    # =====================================================
    # UI MASTER BUILDER
    # =====================================================
    def build_ui(self):
        # Header Area
        header = ctk.CTkFrame(self, height=75, fg_color=HEADER_COLOR, corner_radius=10)
        header.pack(fill="x", pady=(10, 0), padx=10)

        # Menu Button (☰)
        ctk.CTkButton(header, text="☰", width=45, height=45, font=("Arial", 22), 
                      fg_color="transparent", hover_color=CARD_COLOR,
                      command=self.toggle_left_panel).pack(side="left", padx=15)

        ctk.CTkLabel(header, text="QR ATTENDANCE SYSTEM", 
                      font=("Segoe UI Semibold", 24), text_color=TEXT_MAIN).pack(side="left", padx=5)

        # Main Container
        self.main_container = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=10)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Sidebar Area (Hidden initially)
        self.left_panel = ctk.CTkFrame(self.main_container, width=260, fg_color=HEADER_COLOR, corner_radius=10)
        self.left_panel.pack_propagate(False)
        # HINDI natin ito i-papack dito para hidden sa start.

        # Nav Buttons
        self.make_nav_btn("DASHBOARD", "🏠", self.home_screen)
        self.make_nav_btn("REGISTRATION", "📝", self.register_screen)
        self.make_nav_btn("SCAN ATTENDANCE", "📡", self.check_device_and_start_attendance)
        self.make_nav_btn("STOP SYSTEM", "🛑", self.stop_loading, hover_color=DANGER_COLOR)

        # Right Panel
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="transparent", corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=10)

        # Status Footer
        self.status_box = ctk.CTkFrame(self, height=50, fg_color=HEADER_COLOR, corner_radius=10)
        self.status_box.pack(side="bottom", fill="x", pady=(0, 10), padx=10)
        
        self.status_label = ctk.CTkLabel(self.status_box, textvariable=self.status_text, 
                                        font=("Segoe UI Semibold", 13), text_color=TEXT_DIM)
        self.status_label.pack(expand=True)

    def make_nav_btn(self, text, icon, cmd, hover_color=None):
        btn = ctk.CTkButton(self.left_panel, text=f"  {icon}  {text}", height=60, corner_radius=8,
                            fg_color="transparent", anchor="w", font=("Segoe UI Semibold", 14),
                            hover_color=hover_color if hover_color else CARD_COLOR, command=cmd)
        btn.pack(fill="x", padx=10, pady=5)

    def toggle_left_panel(self):
        if self.left_panel_visible:
            self.left_panel.pack_forget()
        else:
            # Pinapakita ang panel sa kaliwa
            self.left_panel.pack(side="left", fill="y", padx=(0, 10))
            # Sinisiguro na ang right panel ay nananatili sa kanan
            self.right_panel.pack_forget()
            self.right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=10)
            
        self.left_panel_visible = not self.left_panel_visible

    def clear_right_panel(self):
        self.is_scanning_active = False
        for w in self.right_panel.winfo_children(): w.destroy()

    # =====================================================
    # DASHBOARD SCREEN
    # =====================================================
    def home_screen(self):
        self.clear_right_panel()
        ctk.CTkLabel(self.right_panel, text="Main Dashboard", font=("Segoe UI", 32, "bold")).pack(anchor="w", pady=(0, 20))
        
        stat_frame = ctk.CTkFrame(self.right_panel, fg_color=CARD_COLOR, height=150, corner_radius=20)
        stat_frame.pack(fill="x", pady=10)
        stat_frame.pack_propagate(False)
        
        ctk.CTkLabel(stat_frame, text="TOTAL REGISTERED STUDENTS", font=("Segoe UI Bold", 13), text_color=ACCENT_COLOR).pack(pady=(35,0))
        ctk.CTkLabel(stat_frame, text=str(len(self.students)), font=("Segoe UI", 56, "bold")).pack()

        ctk.CTkLabel(self.right_panel, text="Recently Registered Students", font=("Segoe UI Semibold", 16)).pack(anchor="w", pady=(20, 10))
        
        scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent", corner_radius=15)
        scroll.pack(fill="both", expand=True)
        
        for s in reversed(self.students):
            f = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, height=55, corner_radius=10)
            f.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(f, text=f"   ID: {s['id']}", font=("Consolas", 15, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"{s['date']}   ", font=("Segoe UI", 12), text_color=TEXT_DIM).pack(side="right", padx=10)

    # (Ang ibang functions tulad ng register_screen, check_device_and_start_attendance, process_attendance, flash_feedback, at stop_loading ay mananatiling pareho sa iyong original na logic)

    def register_screen(self):
        self.clear_right_panel()
        self.student_id_input.set("")
        ctk.CTkLabel(self.right_panel, text="New Registration", font=("Segoe UI", 32, "bold")).pack(anchor="w", pady=(0, 30))
        form_card = ctk.CTkFrame(self.right_panel, fg_color=CARD_COLOR, corner_radius=20)
        form_card.pack(fill="x", padx=10)
        inner = ctk.CTkFrame(form_card, fg_color="transparent")
        inner.pack(padx=50, pady=40, fill="both")
        ctk.CTkLabel(inner, text="STUDENT ID NUMBER", font=("Segoe UI Bold", 12), text_color=ACCENT_COLOR).pack(anchor="w")
        self.id_entry = ctk.CTkEntry(inner, textvariable=self.student_id_input, height=55, 
                                     placeholder_text="e.g., 2026-0001", font=("Segoe UI", 18), 
                                     border_color=HEADER_COLOR, corner_radius=10)
        self.id_entry.pack(pady=(10, 25), fill="x")
        self.id_entry.focus_set()
        ctk.CTkButton(inner, text="REGISTER ID AND QR", fg_color=ACCENT_COLOR, height=55, 
                      font=("Segoe UI Bold", 15), corner_radius=10, command=self.lock_id_and_wait_qr).pack(fill="x")

    def lock_id_and_wait_qr(self):
        sid = self.student_id_input.get().strip().upper()
        if not sid: return
        if not self.is_qr_scanner_connected():
            self.status_text.set("HARDWARE DISCONNECTED: PLEASE CONNECT QR SCANNER")
            self.flash_feedback(DANGER_COLOR)
            return
        self.is_scanning_active = True
        self.status_text.set(f"ID {sid} READY. AWAITING QR SCAN DATA...")
        self.qr_hidden_entry = ctk.CTkEntry(self.right_panel, textvariable=self.qr_hash_input, width=0, height=0, border_width=0)
        self.qr_hidden_entry.pack()
        self.qr_hidden_entry.focus_set() 
        self.qr_hidden_entry.bind("<Return>", lambda e: self.complete_registration())

    def complete_registration(self):
        sid = self.student_id_input.get().strip().upper()
        h_data = self.qr_hash_input.get().strip()
        if h_data:
            self.students.append({"id": sid, "qr_hash": h_data, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.save_to_json()
            self.flash_feedback(SUCCESS_COLOR)
            self.status_text.set(f"SUCCESSFULLY REGISTERED: {sid}")
            self.after(1000, self.register_screen)

    def check_device_and_start_attendance(self):
        self.clear_right_panel()
        self.info_name.set("---")
        self.info_time.set("---")
        self.info_status.set("AWAITING SCAN")
        ctk.CTkLabel(self.right_panel, text="Attendance Mode", font=("Segoe UI", 32, "bold")).pack(anchor="w", pady=(0, 30))
        if self.is_qr_scanner_connected():
            self.is_scanning_active = True
            self.status_text.set("HARDWARE ONLINE. YOU CAN NOW SCAN QR CODES.")
            self.flash_feedback(SUCCESS_COLOR)
            display_card = ctk.CTkFrame(self.right_panel, fg_color=CARD_COLOR, corner_radius=20, padding=35)
            display_card.pack(fill="x", padx=10)
            self.info_row_ui(display_card, "STUDENT ID :", self.info_name)
            self.info_row_ui(display_card, "TIME LOGGED :", self.info_time)
            self.info_row_ui(display_card, "SYSTEM STATUS :", self.info_status)
            self.attendance_catcher = ctk.CTkEntry(self.right_panel, textvariable=self.qr_hash_input, width=0, height=0, border_width=0)
            self.attendance_catcher.pack()
            self.attendance_catcher.focus_set()
            self.attendance_catcher.bind("<Return>", lambda e: self.process_attendance())
        else:
            self.status_text.set("PLEASE CONNECT YOUR HARDWARE SCANNER QR DEVICE")
            self.flash_feedback(DANGER_COLOR)
            error_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
            error_frame.pack(expand=True)
            ctk.CTkLabel(error_frame, text="⚠️", font=("Segoe UI", 72)).pack()
            ctk.CTkLabel(error_frame, text="SCANNER NOT DETECTED", font=("Segoe UI", 22, "bold"), text_color=DANGER_COLOR).pack(pady=10)
            ctk.CTkLabel(error_frame, text="Check USB cable and ensure device is plugged in.", font=("Segoe UI", 14), text_color=TEXT_DIM).pack()

    def process_attendance(self):
        if not self.is_scanning_active: return
        scanned_hash = self.qr_hash_input.get().strip()
        self.qr_hash_input.set("") 
        match = next((s for s in self.students if s['qr_hash'] == scanned_hash), None)
        if match:
            now = datetime.now().strftime("%I:%M:%S %p")
            self.info_name.set(match['id'])
            self.info_time.set(now)
            self.info_status.set("LOGGED SUCCESSFULLY")
            self.status_text.set(f"LOGGED: {match['id']}. READY FOR NEXT SCAN.")
            self.flash_feedback(SUCCESS_COLOR)
        else:
            self.info_name.set("NOT FOUND")
            self.info_time.set("---")
            self.info_status.set("ID NOT REGISTERED")
            self.status_text.set("DATABASE ERROR: QR CODE NOT RECOGNIZED")
            self.flash_feedback(DANGER_COLOR)
        self.attendance_catcher.focus_set()

    def info_row_ui(self, parent, label, var):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=15)
        ctk.CTkLabel(row, text=label, font=("Segoe UI Bold", 13), width=200, anchor="w", text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(row, textvariable=var, font=("Segoe UI Semibold", 18), text_color=TEXT_MAIN).pack(side="left")

    def flash_feedback(self, color):
        self.status_box.configure(fg_color=color)
        self.after(600, lambda: self.status_box.configure(fg_color=HEADER_COLOR))

    def stop_loading(self):
        self.is_scanning_active = False
        self.status_text.set("SYSTEM IDLE")
        self.home_screen()

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
