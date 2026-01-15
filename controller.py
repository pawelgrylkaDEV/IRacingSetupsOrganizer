import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os


class AppController:
    def __init__(self, root):
        self.root = root
        self.root.title("App Controller")
        self.root.geometry("400x300")

        # Variables for paths
        self.download_folder_path = tk.StringVar()
        self.setups_folder_path = tk.StringVar()

        # 1. Load config (or force creation if missing)
        self.config_data = self.load_config()

        # 2. Main UI
        self.label_info = tk.Label(root,
                                   text=f"Current Download Path:\n{self.config_data.get('download_path', 'Not Set')}")
        self.label_info.pack(pady=20)

        # --- POPRAWKA TUTAJ ---

        # Przycisk 1: Load Setups (zmieniłem nazwę zmiennej na btn_load)
        # Zwróć uwagę: command=self.LoadSetups (bez nawiasów!)
        self.btn_load = tk.Button(root, text="Load Setups", command=self.LoadSetups, bg="lightblue")
        self.btn_load.pack(pady=10)

        # Przycisk 2: Settings
        self.btn_settings = tk.Button(root, text="Settings", command=self.open_config_form)
        self.btn_settings.pack(pady=10)

        self.btn_exit = tk.Button(root, text="Exit", command=root.quit, bg="#ffcccc")
        self.btn_exit.pack(pady=20)

    # ---------------------------------------------------------
    # CONFIGURATION LOGIC
    # ---------------------------------------------------------

    def load_config(self):
        config_file = "config.json"

        try:
            with open(config_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.download_folder_path.set(data.get("download_path", ""))
                self.setups_folder_path.set(data.get("setups_path", ""))
                return data

        except FileNotFoundError:
            print("Config file not found. Launching first-run setup...")
            messagebox.showinfo("First Run", "Welcome! Please configure the paths to continue.")

            config_window = self.open_config_form()
            self.root.wait_window(config_window)

            if os.path.exists(config_file):
                return self.load_config()
            else:
                default_config = {"download_path": "", "setups_path": ""}
                with open(config_file, "w", encoding="utf-8") as file:
                    json.dump(default_config, file, indent=4)
                return default_config

    def open_config_form(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Settings")
        config_window.geometry("500x300")
        config_window.grab_set()

        # --- Section 1: Downloads ---
        tk.Label(config_window, text="Download Folder:").pack(anchor="w", padx=20, pady=(10, 0))
        frame_download = tk.Frame(config_window)
        frame_download.pack(fill="x", padx=20)

        entry_download = tk.Entry(frame_download, textvariable=self.download_folder_path)
        entry_download.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))

        tk.Button(frame_download, text="Browse...",
                  command=lambda: self.select_folder(self.download_folder_path)).pack(side=tk.LEFT)

        # --- Section 2: Setups ---
        tk.Label(config_window, text="Setups Folder:").pack(anchor="w", padx=20, pady=(20, 0))
        frame_setups = tk.Frame(config_window)
        frame_setups.pack(fill="x", padx=20)

        entry_setups = tk.Entry(frame_setups, textvariable=self.setups_folder_path)
        entry_setups.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 10))

        tk.Button(frame_setups, text="Browse...",
                  command=lambda: self.select_folder(self.setups_folder_path)).pack(side=tk.LEFT)

        # --- Save Button ---
        tk.Button(config_window, text="Save & Close",
                  command=lambda: self.save_config(config_window),
                  bg="lightgreen", height=2, width=20).pack(pady=30)

        return config_window

    def select_folder(self, target_variable):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            target_variable.set(folder_path)

    def save_config(self, window):
        config_data = {
            "download_path": self.download_folder_path.get(),
            "setups_path": self.setups_folder_path.get()
        }

        try:
            with open("config.json", "w", encoding="utf-8") as file:
                json.dump(config_data, file, indent=4, ensure_ascii=False)

            messagebox.showinfo("Success", "Configuration saved successfully.")

            if hasattr(self, 'label_info'):
                self.label_info.config(text=f"Current Download Path:\n{config_data['download_path']}")

            window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    # ---------------------------------------------------------
    # ACTION LOGIC
    # ---------------------------------------------------------

    def LoadSetups(self):
        # Pobieramy ścieżki (upewniamy się, że mamy najnowsze dane z configu)
        # Warto odświeżyć dane z pliku lub użyć self.download_folder_path.get()
        pathDownloads = self.download_folder_path.get()

        print(f"Checking folder: {pathDownloads}")

        if pathDownloads and os.path.exists(pathDownloads):
            try:
                items = os.listdir(pathDownloads)

                if not items:
                    messagebox.showinfo("Info", "Folder is empty.")
                else:
                    # Wypiszmy co znaleziono w konsoli
                    print("--- Found files: ---")
                    for item in items:
                        print(item)

                    messagebox.showinfo("Success", f"Found {len(items)} files/folders. Check console.")

            except Exception as e:
                print(f"Error loading setups: {e}")
                messagebox.showerror("Error", f"Failed to load setups: {e}")
        else:
            messagebox.showwarning("Warning", "Download path is invalid or does not exist!")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()