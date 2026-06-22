import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time

class MouseJigglerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Status Keeper (Mouse Jiggler)")
        self.root.geometry("320x380")
        self.root.resizable(False, False)
        
        # Make movements subtle and prevent failsafe crashes if mouse is in the corner
        pyautogui.FAILSAFE = False 

        self.is_running = False
        self.jiggle_thread = None

        # Time mapping (in seconds)
        self.time_options = {
            "1 min": 60,
            "5 min": 300,
            "10 min": 600,
            "15 min": 900,
            "30 min": 1800,
            "1 h": 3600,
            "2 h": 7200,
            "3 h": 10800,
            "Forever": -1,

        }

        self.create_widgets()
        
        # Handle window close event cleanly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- Title ---
        title_label = tk.Label(self.root, text="Select Duration:", font=("Arial", 12, "bold"))
        title_label.pack(pady=(15, 5))

        # --- Dropdown for time options ---
        self.selected_time = tk.StringVar()
        self.time_dropdown = ttk.Combobox(self.root, textvariable=self.selected_time, state="readonly")
        self.time_dropdown['values'] = list(self.time_options.keys())
        self.time_dropdown.current(1) # Default to 5 min
        self.time_dropdown.pack(pady=5)
        self.time_dropdown.bind("<<ComboboxSelected>>", self.toggle_custom_entry)

        # --- Custom Time Entry ---
        self.custom_frame = tk.Frame(self.root)
        self.custom_frame.pack(pady=5)
        
        tk.Label(self.custom_frame, text="Custom (mins):").pack(side=tk.LEFT)
        self.custom_entry = tk.Entry(self.custom_frame, width=10, state="disabled")
        self.custom_entry.pack(side=tk.LEFT, padx=5)

        # --- Start / Stop Buttons ---
        self.start_btn = tk.Button(self.root, text="START", bg="green", fg="white", font=("Arial", 12, "bold"), width=15, command=self.start_jiggler)
        self.start_btn.pack(pady=(20, 10))

        self.stop_btn = tk.Button(self.root, text="STOP", bg="red", fg="white", font=("Arial", 12, "bold"), width=15, state="disabled", command=self.stop_jiggler)
        self.stop_btn.pack(pady=5)

        # --- Status Label ---
        self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 10, "italic"), fg="gray")
        self.status_label.pack(pady=(20, 0))

    def toggle_custom_entry(self, event):
        """Enable custom entry box only if 'Custom Time' is selected."""
        if self.selected_time.get() == "Custom Time":
            self.custom_entry.config(state="normal")
        else:
            self.custom_entry.delete(0, tk.END)
            self.custom_entry.config(state="disabled")

    def get_duration_seconds(self):
        """Calculate the total duration in seconds based on user input."""
        selection = self.selected_time.get()
        if selection == "Custom Time":
            try:
                mins = float(self.custom_entry.get())
                return int(mins * 60)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for custom minutes.")
                return None
        return self.time_options[selection]

    def start_jiggler(self):
        duration = self.get_duration_seconds()
        if duration is None:
            return # Invalid custom input

        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.time_dropdown.config(state="disabled")
        self.custom_entry.config(state="disabled")
        
        mode = "Forever" if duration == -1 else f"for {duration // 60} min(s)"
        self.status_label.config(text=f"Status: Running {mode}...", fg="green")

        # Start the jiggler loop in a separate thread so the GUI doesn't freeze
        self.jiggle_thread = threading.Thread(target=self.jiggle_loop, args=(duration,))
        self.jiggle_thread.daemon = True
        self.jiggle_thread.start()

    def stop_jiggler(self):
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.time_dropdown.config(state="readonly")
        
        # Re-enable custom entry if custom was selected
        if self.selected_time.get() == "Custom Time":
            self.custom_entry.config(state="normal")

        self.status_label.config(text="Status: Stopped", fg="red")

    def jiggle_loop(self, duration_seconds):
        start_time = time.time()
        
        # Moves the mouse 2 pixels back and forth every 5 seconds
        movements = [(2, 0), (-2, 0)] 
        move_index = 0

        while self.is_running:
            # Check if time is up (unless it's set to -1 for Forever)
            if duration_seconds != -1 and (time.time() - start_time) >= duration_seconds:
                # Automatically stop when time is up
                self.root.after(0, self.stop_jiggler)
                self.root.after(0, lambda: self.status_label.config(text="Status: Time Completed", fg="blue"))
                break
            
            # Perform a tiny, almost unnoticeable mouse movement
            dx, dy = movements[move_index]
            pyautogui.moveRel(dx, dy)
            move_index = (move_index + 1) % len(movements)
            
            # Wait 5 seconds before moving again. 
            # We break this into smaller sleeps to make the STOP button responsive instantly.
            for _ in range(50):
                if not self.is_running:
                    break
                time.sleep(0.1)

    def on_closing(self):
        """Ensure background threads die when the window is closed."""
        self.is_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseJigglerApp(root)
    root.mainloop()