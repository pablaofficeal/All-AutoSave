import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import shutil
from pathlib import Path
import sys

# Путь для установки
desktop_path = Path.home() / "Desktop"
install_dir = desktop_path / "PremiereAutoSave"
resources_dir = install_dir / "resources"

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Установщик Premiere AutoSave")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Заголовок
        self.label = tk.Label(root, text="Установка Premiere AutoSave", font=("Arial", 16, "bold"))
        self.label.pack(pady=20)

        # Прогресс-бар
        self.progress = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Статус
        self.status_label = tk.Label(root, text="Готов к установке", font=("Arial", 10))
        self.status_label.pack(pady=10)

        # Кнопка установки
        self.install_button = tk.Button(root, text="Установить", command=self.start_installation, 
                                       bg="#4CAF50", fg="white", font=("Arial", 12), width=20)
        self.install_button.pack(pady=20)

    def update_status(self, message, progress_value):
        self.status_label.config(text=message)
        self.progress["value"] = progress_value
        self.root.update()

    def install_dependencies(self):
        self.update_status("Установка зависимостей...", 20)
        dependencies = ["customtkinter", "pyautogui", "plyer"]
        for dep in dependencies:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            except subprocess.CalledProcessError:
                raise Exception(f"Не удалось установить {dep}")

    def setup_app(self):
        self.update_status("Создание папок...", 50)
        os.makedirs(install_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)

        # Копирование основного скрипта
        main_script = os.path.join(os.path.dirname(__file__), "main_app.py")
        if not os.path.exists(main_script):
            raise Exception("main_app.py не найден!")
        shutil.copy(main_script, install_dir)

        # Копирование иконки
        icon_src = os.path.join(os.path.dirname(__file__), "resources", "icon.ico")
        icon_dest = os.path.join(resources_dir, "icon.ico")
        if not os.path.exists(icon_src):
            raise Exception("icon.ico не найден!")
        shutil.copy(icon_src, icon_dest)

        # Создание ярлыка (Windows)
        if os.name == "nt":
            self.update_status("Создание ярлыка...", 80)
            try:
                import winshell
                from win32com.client import Dispatch
                shortcut_path = desktop_path / "PremiereAutoSave.lnk"
                target = install_dir / "main_app.py"
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = sys.executable
                shortcut.Arguments = f'"{target}"'
                shortcut.IconLocation = icon_dest
                shortcut.save()
            except ImportError:
                self.update_status("Не удалось создать ярлык (установите pywin32)", 80)

    def start_installation(self):
        self.install_button.config(state="disabled")
        try:
            self.update_status("Начинаем установку...", 10)
            self.install_dependencies()
            self.setup_app()
            self.update_status("Установка завершена!", 100)
            messagebox.showinfo("Успех", f"Приложение установлено в {install_dir}\nЗапустите с рабочего стола!")
        except Exception as e:
            self.update_status(f"Ошибка: {str(e)}", 0)
            messagebox.showerror("Ошибка", f"Не удалось установить: {str(e)}")
        finally:
            self.install_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()