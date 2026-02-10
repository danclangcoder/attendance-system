import customtkinter as ctk

# =====================================================
# CONFIG
# =====================================================
BG_COLOR = "#202020"
CARD_COLOR = "#383838"
HEADER_COLOR = "#575656"
GREY_COLOR = "#464545"
WHITE_TEXT = "#F6F9FC"
SUCCESS_COLOR = "#2E7D32"
DANGER_COLOR = "#E53935"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


# =====================================================
# MAIN APP (GUI ONLY)
# =====================================================
class AttendanceApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("QR Attendance System")
        self.geometry("1100x600")
        self.resizable(False, False)

        # Dummy variables for animation / labels
        self.status_text = ctk.StringVar(value="IDLE")
        self.student_id_var = ctk.StringVar()
        self.info_name = ctk.StringVar(value="---")
        self.info_time = ctk.StringVar(value="---")
        self.info_status = ctk.StringVar(value="---")

        self.build_ui()
        self.home_screen()

    # =====================================================
    # UI
    # =====================================================
    def build_ui(self):

        header = ctk.CTkFrame(self, height=90, fg_color=HEADER_COLOR)
        header.pack(fill="x")

        # Add menu icon to the top-left corner
        self.menu_icon = ctk.CTkButton(header, text="≡", width=40, fg_color=HEADER_COLOR,
                                       command=self.toggle_left_panel)
        self.menu_icon.pack(side="left", padx=10, pady=25)

        ctk.CTkLabel(header, text="MENU",
                     font=("Segoe UI", 24, "bold"),
                     text_color=WHITE_TEXT).pack(pady=25)

        main = ctk.CTkFrame(self, fg_color=BG_COLOR)
        main.pack(fill="both", expand=True, padx=20, pady=15)

        self.left_panel = ctk.CTkFrame(main, width=260, fg_color=CARD_COLOR)
        self.left_panel.pack(side="left", fill="y", padx=(0, 15))
        self.left_panel.pack_propagate(False)

        self.right_container = ctk.CTkFrame(main, fg_color=BG_COLOR)
        self.right_container.pack(side="right", fill="both", expand=True)

        self.right_panel = ctk.CTkFrame(self.right_container, fg_color=GREY_COLOR)
        self.right_panel.place(relwidth=1)

        self.status_box = ctk.CTkFrame(self.right_container, height=80, fg_color=CARD_COLOR)
        self.status_box.pack(side="bottom", fill="x")

        ctk.CTkLabel(self.status_box, textvariable=self.status_text,
                     font=("Segoe UI", 14, "bold")).pack(expand=True)

        # Add buttons to the left panel
        self.buttons = []
        self.buttons.append(self.make_btn("HOME", self.home_screen))
        self.buttons.append(self.make_btn("ID REGISTRATION", self.register_screen))
        self.buttons.append(self.make_btn("ATTENDANCE SCANNING", self.attendance_screen))
        self.buttons.append(self.make_btn("STOP SCANNING", self.stop_loading, DANGER_COLOR))

        # Initially hide the left panel
        self.left_panel_visible = True
        self.toggle_left_panel()

    def toggle_left_panel(self):
        if self.left_panel_visible:
            for i in range(260, -1, -20):
                self.left_panel.configure(width=i)
                self.left_panel.update()
            for button in self.buttons:
                button.pack_forget()
            self.left_panel.pack_forget()
        else:
            self.left_panel.pack(side="left", fill="y", padx=(0, 15))
            for i in range(0, 261, 20):
                self.left_panel.configure(width=i)
                self.left_panel.update()
            for button in self.buttons:
                button.pack(fill="x", padx=20, pady=12)
        self.left_panel_visible = not self.left_panel_visible

    def make_btn(self, text, cmd, color=CARD_COLOR):
        button = ctk.CTkButton(self.left_panel, text=text, fg_color=color, command=cmd)
        return button

    # =====================================================
    # GUI SCREENS (no backend)
    # =====================================================
    def register_screen(self):
        self.clear_right_panel()

        ctk.CTkLabel(self.right_panel, text="ID REGISTRATION",
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE_TEXT).pack(pady=15)

        self.info_row("STUDENT ID :", self.info_name)
        self.info_row("TIME :", self.info_time)
        self.info_row("STATUS :", self.info_status)

        # Flash animation demo
        self.flash_success()

    def attendance_screen(self):
        self.clear_right_panel()

        ctk.CTkLabel(self.right_panel, text="ATTENDANCE SCANNING",
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE_TEXT).pack(pady=15)

        self.info_row("STUDENT ID :", self.info_name)
        self.info_row("TIME :", self.info_time)
        self.info_row("STATUS :", self.info_status)

        # Dummy scan button to show flash animation
        ctk.CTkButton(self.right_panel, text="SCAN QR",
                      command=self.flash_success).pack(pady=20)

    def home_screen(self):
        self.clear_right_panel()

        ctk.CTkLabel(self.right_panel, text="HOME SCREEN",
                     font=("Segoe UI", 16, "bold"),
                     text_color=WHITE_TEXT).pack(pady=15)

        ctk.CTkLabel(self.right_panel, text="Welcome to the QR Attendance System!",
                     font=("Segoe UI", 14),
                     text_color=WHITE_TEXT).pack(pady=10)

    # =====================================================
    # HELPERS
    # =====================================================
    def clear_right_panel(self):
        for w in self.right_panel.winfo_children():
            w.destroy()

    def info_row(self, label, var):
        row = ctk.CTkFrame(self.right_panel, fg_color=GREY_COLOR)
        row.pack(anchor="w", padx=40, pady=8)
        ctk.CTkLabel(row, text=label, width=15).pack(side="left")
        ctk.CTkLabel(row, textvariable=var).pack(side="left")

    def flash_success(self):
        # Flash animation demo
        self.status_box.configure(fg_color=SUCCESS_COLOR)
        self.after(400, lambda: self.status_box.configure(fg_color=CARD_COLOR))

    def stop_loading(self):
        self.status_text.set("IDLE")


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()