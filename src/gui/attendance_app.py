import tkinter as tk

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Attendance System")
        self.center_main_window(1280, 720)
        self.minsize(640, 480)
        self.create_widgets()

    def center_main_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        self.label = tk.Label(self, text="Welcome to the Attendance System")
        self.label.pack(pady=20)
        self.scan_button = tk.Button(self, text="Record Attendance")
        self.scan_button.pack(pady=10)
        self.register_button = tk.Button(self, text="Register Students", command= self.register_window)
        self.register_button.pack(pady=10)

    def register_window(self):
        register_window = tk.Toplevel(self)
        register_window.title("Register Students")
        self.center_toplevel(register_window, 640, 480)
        label = tk.Label(register_window, text="Register Student")
        label.pack(pady=20)

    def center_toplevel(self, toplevel, width, height):
        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        toplevel.geometry(f'{width}x{height}+{x}+{(y) - 100}')