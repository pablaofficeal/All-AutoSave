import customtkinter as ctk
from customtkinter import CTkTabview
import pyautogui
import time
import threading
from plyer import notification
import logging
import os
from datetime import datetime
import importlib.util
import tkinter.filedialog as filedialog
import sys

# Определение пути к логам и ресурсам
if getattr(sys, 'frozen', False):  # Если запущен как .exe
    base_path = os.path.dirname(sys.executable)
else:  # Если запущен как .py
    base_path = os.path.dirname(os.path.abspath(__file__))

log_dir = os.path.join(base_path, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "autosave_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format="%(asctime)s - %(message)s")

class AutoSaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Premiere AutoSave Pro")
        self.root.geometry("450x550")
        self.running = False
        self.custom_script = None
        # нужно добавить иконку для самого окна
        self.root.resizable(False, False)
        self.root.configure(bg="#2b2b2b")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_propagate(False)
        self.root.configure(bg="#2b2b2b")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # Установка иконки
        icon_path = os.path.join(base_path, "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Заголовок
        self.header = ctk.CTkLabel(root, text="Premiere AutoSave Pro", font=("Arial", 20, "bold"))
        self.header.pack(pady=10)

        # Вкладки
        self.tabview = CTkTabview(root, fg_color="#2b2b2b", segmented_button_fg_color="#1f538d")
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)
        self.tabview.add("Автосохранение")
        self.tabview.add("Кастомный скрипт")

        self.setup_autosave_tab(self.tabview.tab("Автосохранение"))
        self.setup_custom_script_tab(self.tabview.tab("Кастомный скрипт"))

        # Футер
        self.footer = ctk.CTkLabel(root, text="© 2025 Premiere AutoSave Pro | Все права защищены", font=("Arial", 10))
        self.footer.pack(pady=5)

    def setup_autosave_tab(self, tab):
        self.label = ctk.CTkLabel(tab, text="Интервал автосохранения (сек):", font=("Arial", 14))
        self.label.pack(pady=10)
        self.entry = ctk.CTkEntry(tab, placeholder_text="Введите число", width=200, font=("Arial", 12))
        self.entry.pack(pady=10)
        self.start_button = ctk.CTkButton(tab, text="Старт", command=self.start_autosave, 
                                         fg_color="#1f538d", hover_color="#14375e", font=("Arial", 12))
        self.start_button.pack(pady=10)
        self.stop_button = ctk.CTkButton(tab, text="Стоп", command=self.stop_autosave, 
                                        state="disabled", fg_color="#8d1f1f", hover_color="#5e1414", font=("Arial", 12))
        self.stop_button.pack(pady=10)
        self.progress = ctk.CTkProgressBar(tab, width=250, progress_color="#1f538d")
        self.progress.pack(pady=10)
        self.progress.set(0)
        self.status_label = ctk.CTkLabel(tab, text="Статус: Остановлено", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def setup_custom_script_tab(self, tab):
        self.script_label = ctk.CTkLabel(tab, text="Нет загруженного скрипта", font=("Arial", 14))
        self.script_label.pack(pady=10)
        self.load_button = ctk.CTkButton(tab, text="Загрузить скрипт", command=self.load_custom_script,
                                        fg_color="#1f8d53", hover_color="#145e37", font=("Arial", 12))
        self.load_button.pack(pady=10)
        self.script_interval_label = ctk.CTkLabel(tab, text="Интервал выполнения (сек):", font=("Arial", 14))
        self.script_interval_label.pack(pady=10)
        self.script_entry = ctk.CTkEntry(tab, placeholder_text="Введите число", width=200, font=("Arial", 12))
        self.script_entry.pack(pady=10)
        self.script_start_button = ctk.CTkButton(tab, text="Старт", command=self.start_custom_script,
                                                fg_color="#1f538d", hover_color="#14375e", state="disabled", font=("Arial", 12))
        self.script_start_button.pack(pady=10)
        self.script_stop_button = ctk.CTkButton(tab, text="Стоп", command=self.stop_autosave,
                                               state="disabled", fg_color="#8d1f1f", hover_color="#5e1414", font=("Arial", 12))
        self.script_stop_button.pack(pady=10)
        self.script_status_label = ctk.CTkLabel(tab, text="Статус: Остановлено", font=("Arial", 12))
        self.script_status_label.pack(pady=10)

    def save_project(self):
        pyautogui.hotkey("ctrl", "s")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification.notify(title="Premiere AutoSave", message=f"Проект сохранён в {current_time}", timeout=5)
        logging.info(f"Проект сохранён в {current_time}")

    def execute_custom_script(self):
        if self.custom_script:
            try:
                self.custom_script.execute()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                notification.notify(title="Custom Script", message=f"Скрипт выполнен в {current_time}", timeout=5)
                logging.info(f"Кастомный скрипт выполнен в {current_time}")
            except Exception as e:
                self.script_status_label.configure(text=f"Ошибка в скрипте: {str(e)}")

    def autosave_loop(self):
        while self.running:
            self.save_project()
            for i in range(int(self.interval * 10)):
                if not self.running:
                    break
                self.progress.set(i / (self.interval * 10))
                time.sleep(0.1)
        self.progress.set(0)

    def custom_script_loop(self):
        while self.running:
            self.execute_custom_script()
            time.sleep(self.interval)

    def start_autosave(self):
        try:
            self.interval = int(self.entry.get())
            if self.interval <= 0:
                raise ValueError("Интервал должен быть положительным!")
            self.running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text=f"Статус: Работает (каждые {self.interval} сек)")
            self.thread = threading.Thread(target=self.autosave_loop)
            self.thread.start()
        except ValueError as e:
            self.status_label.configure(text=f"Ошибка: {str(e)}")

    def start_custom_script(self):
        try:
            self.interval = int(self.script_entry.get())
            if self.interval <= 0:
                raise ValueError("Интервал должен быть положительным!")
            self.running = True
            self.script_start_button.configure(state="disabled")
            self.script_stop_button.configure(state="normal")
            self.script_status_label.configure(text=f"Статус: Работает (каждые {self.interval} сек)")
            self.thread = threading.Thread(target=self.custom_script_loop)
            self.thread.start()
        except ValueError as e:
            self.script_status_label.configure(text=f"Ошибка: {str(e)}")

    def stop_autosave(self):
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Статус: Остановлено")
        self.script_start_button.configure(state="normal" if self.custom_script else "disabled")
        self.script_stop_button.configure(state="disabled")
        self.script_status_label.configure(text="Статус: Остановлено")

    def load_custom_script(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            spec = importlib.util.spec_from_file_location("custom_script", file_path)
            self.custom_script = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.custom_script)
            self.script_label.configure(text=f"Скрипт: {os.path.basename(file_path)}")
            self.script_start_button.configure(state="normal")
            logging.info(f"Загружен кастомный скрипт: {file_path}")

if __name__ == "__main__":
    # Установка зависимостей при первом запуске (если не установлены)
    try:
        import customtkinter
        import pyautogui
        import plyer
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "pyautogui", "plyer"])
    
    root = ctk.CTk()
    app = AutoSaveApp(root)
    root.mainloop()