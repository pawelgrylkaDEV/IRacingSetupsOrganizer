import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import toml
from datetime import datetime, timedelta

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
        # Pobieramy ścieżkę
        pathDownloads = self.download_folder_path.get()
        setups_folder_path = self.setups_folder_path.get()
        print(f"Checking folder: {pathDownloads}")

        dateNow = datetime.now()
        timeDelta = timedelta(minutes=30)  # Szukamy plików z ostatnich 30 minut

        # Sprawdzamy czy ścieżka istnieje
        if pathDownloads and os.path.exists(pathDownloads):
            try:
                found_count = 0  # Licznik znalezionych plików
                found_files_names = []  # Lista nazw do ewentualnego wyświetlenia

                # Używamy 'with' dla bezpieczeństwa zasobów
                with os.scandir(pathDownloads) as items:
                    print("--- Scanning files... ---")

                    for item in items:
                        # Sprawdzamy tylko pliki
                        if item.is_file():
                            try:
                                itemName = item.name
                                creationTime = item.stat().st_ctime
                                creationTimeConverted = datetime.fromtimestamp(creationTime)

                                # Logika porównania czasu
                                if dateNow - creationTimeConverted < timeDelta and itemName.endswith(".sto"):
                                    print(f"MATCH: {item.name} | Time: {creationTimeConverted}")
                                    found_files_names.append(item.name)
                                    found_count += 1
                                    if "P1Doks" in itemName:
                                        carName = itemName.split("_")[1]  # Np. "BMWM4"

                                        # 1. Sprawdzenie czy ścieżka do folderu z setupami w ogóle istnieje
                                        if os.path.exists(setups_folder_path):
                                            try:
                                                with os.scandir(setups_folder_path) as entries:
                                                    print(
                                                        f"--- Szukam folderu dla auta: {carName} w {setups_folder_path} ---")

                                                    found_car_folder = False

                                                    for entry in entries:
                                                        # 2. Kluczowy moment: sprawdzamy czy to FOLDER (nie plik)
                                                        if entry.is_dir():
                                                            print(f"Znaleziono folder: {entry.name}")

                                                            # (Opcjonalnie) Sprawdzenie czy folder nazywa się tak jak auto
                                                            if entry.name.lower() == carName.lower():
                                                                print(f"!!! SUKCES: Mam folder dla {carName} !!!")
                                                                found_car_folder = True

                                                    if not found_car_folder:
                                                        print(f"Nie znaleziono folderu o nazwie {carName}")

                                            except Exception as e:
                                                print(f"Błąd podczas skanowania folderów: {e}")
                                                messagebox.showerror("Error", f"Błąd: {e}")
                                                return
                                        else:
                                            messagebox.showerror("Error",
                                                                 "Ścieżka 'setups_folder_path' jest nieprawidłowa!")
                                            return

                            except OSError:
                                continue  # Jeśli plik jest zablokowany, pomijamy go

                # Logika wyświetlania komunikatów PO zakończeniu skanowania
                if found_count == 0:
                    messagebox.showinfo("Info", "No recent files found (last 30 mins).")
                else:
                    # Możesz wypisać np. pierwsze 5 plików w komunikacie
                    msg_text = f"Found {found_count} recent files.\nCheck console for details."
                    messagebox.showinfo("Success", msg_text)

            except Exception as e:
                print(f"Error loading setups: {e}")
                messagebox.showerror("Error", f"Failed to load setups: {e}")
        else:
            messagebox.showwarning("Warning", "Download path is invalid or does not exist!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()