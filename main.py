import tkinter as tk
# Importujemy naszą klasę z pliku kontroler.py
# Składnia: from [nazwa_pliku_bez_py] import [NazwaKlasy]
from controller import AppController

if __name__ == "__main__":
    # 1. Tworzymy główne okno
    root = tk.Tk()

    # 2. Inicjalizujemy nasz kontroler, przekazując mu okno
    app = AppController(root)

    # 3. Uruchamiamy pętlę
    root.mainloop()