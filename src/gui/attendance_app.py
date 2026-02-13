import customtkinter as ctk
from typing import Tuple

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

        # Animation state
        self._panel_animating = False
        self._left_panel_target_width = 260
        self._pulse_active = False

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

        # Header title - start slightly dim and fade in
        self.header_title = ctk.CTkLabel(header, text="MENU",
                         font=("Segoe UI", 24, "bold"),
                         text_color="#9C9C9C")
        self.header_title.pack(pady=25)

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

        # start subtle header animation
        self.after(120, self.animate_header)

    def toggle_left_panel(self):
        if self._panel_animating:
            return
        self._panel_animating = True

        def animate(current, step, finish_cond, on_finish=None):
            if finish_cond(current):
                if on_finish:
                    on_finish()
                self._panel_animating = False
                return
            current = current + step
            self.left_panel.configure(width=max(0, min(self._left_panel_target_width, current)))
            self.after(12, lambda: animate(current, step, finish_cond, on_finish))

        if self.left_panel_visible:
            # close panel
            def finish_close():
                for button in self.buttons:
                    button.pack_forget()
                self.left_panel.pack_forget()
                self.menu_icon.configure(text="≡")

            animate(self._left_panel_target_width, -8, lambda w: w <= 0, finish_close)
        else:
            # open panel
            self.left_panel.pack(side="left", fill="y", padx=(0, 15))
            for button in self.buttons:
                button.pack(fill="x", padx=20, pady=12)

            def finish_open():
                self.menu_icon.configure(text="✕")

            animate(0, 8, lambda w: w >= self._left_panel_target_width, finish_open)

        self.left_panel_visible = not self.left_panel_visible

    def make_btn(self, text, cmd, color=CARD_COLOR):
        button = ctk.CTkButton(self.left_panel, text=text, fg_color=color, command=cmd)
        return button

    # ======================
    # Animation helpers
    # ======================
    def _hex_to_rgb(self, h: str) -> Tuple[int, int, int]:
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        return '#%02x%02x%02x' % rgb

    def _interpolate(self, a: str, b: str, t: float) -> str:
        ra = self._hex_to_rgb(a)
        rb = self._hex_to_rgb(b)
        r = tuple(int(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))
        return self._rgb_to_hex(r)

    def animate_header(self, steps: int = 12, delay: int = 40):
        # Fade header title from dim to WHITE_TEXT
        start = "#9C9C9C"
        end = WHITE_TEXT
        for i in range(steps):
            t = i / (steps - 1)
            color = self._interpolate(start, end, t)
            self.after(i * delay, lambda c=color: self.header_title.configure(text_color=c))

    def flash_success(self):
        # Flash animation demo with fade back to CARD_COLOR
        steps = 8
        start = SUCCESS_COLOR
        end = CARD_COLOR
        for i in range(steps):
            t = i / (steps - 1)
            color = self._interpolate(start, end, t)
            self.after(i * 50, lambda c=color: self.status_box.configure(fg_color=c))

    def pulse_button(self, button: ctk.CTkButton, base_color: str = CARD_COLOR, pulse_color: str = "#4A4A4A"):
        # Simple pulsing by toggling fg_color between base and pulse_color
        if not getattr(self, '_pulse_active', False):
            return
        current = getattr(button, '_pulse_state', 0)
        next_state = 1 - current
        t = 0.5 if next_state else 0.0
        color = self._interpolate(base_color, pulse_color, t)
        button.configure(fg_color=color)
        button._pulse_state = next_state
        self.after(600, lambda: self.pulse_button(button, base_color, pulse_color))

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
                     highlightthickness=0,
                     text_color=WHITE_TEXT).pack(pady=15)

        self.info_row("STUDENT ID :", self.info_name)
        self.info_row("TIME :", self.info_time)
        self.info_row("STATUS :", self.info_status)

        # Dummy scan button to show flash animation and pulsing
        self.scan_btn = ctk.CTkButton(self.right_panel, text="SCAN QR",
                          command=self.flash_success)
        self.scan_btn.pack(pady=20)
        # start pulsing
        self._pulse_active = True
        self.pulse_button(self.scan_btn)

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
        # stop any pulsing animation when leaving a screen
        self._pulse_active = False
        for w in self.right_panel.winfo_children():
            w.destroy()

    def info_row(self, label, var):
        row = ctk.CTkFrame(self.right_panel, fg_color=GREY_COLOR)
        row.pack(anchor="w", padx=40, pady=8)
        ctk.CTkLabel(row, text=label, width=15).pack(side="left")
        ctk.CTkLabel(row, textvariable=var).pack(side="left")

    # Animated flash_success defined earlier in the animation helpers

    def stop_loading(self):
        self.status_text.set("IDLE")


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
