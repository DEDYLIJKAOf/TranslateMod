"""
Простое GUI для переводчика модов Minecraft.
"""
from __future__ import annotations

import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from translator import MinecraftModTranslator
from jar_handler import translate_jar_mod


class TranslatorGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Переводчик модов Minecraft")
        self.root.geometry("700x520")

        self.mode_var = tk.StringVar(value="jar")
        self.path_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.source_var = tk.StringVar(value="en")
        self.target_var = tk.StringVar(value="ru")

        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Label(self.root, text="Переводчик модов Minecraft", font=("Segoe UI", 14, "bold"))
        header.pack(pady=10)

        mode_frame = tk.LabelFrame(self.root, text="Режим")
        mode_frame.pack(fill="x", padx=12, pady=6)

        tk.Radiobutton(
            mode_frame, text="Перевести .jar", value="jar", variable=self.mode_var, command=self._on_mode_change
        ).pack(side="left", padx=8, pady=6)
        tk.Radiobutton(
            mode_frame, text="Перевести папку", value="folder", variable=self.mode_var, command=self._on_mode_change
        ).pack(side="left", padx=8, pady=6)

        path_frame = tk.LabelFrame(self.root, text="Входной файл / папка")
        path_frame.pack(fill="x", padx=12, pady=6)

        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)

        self.browse_button = tk.Button(path_frame, text="Выбрать...", command=self._browse_input)
        self.browse_button.pack(side="left", padx=8, pady=6)

        output_frame = tk.LabelFrame(self.root, text="Выходной путь (опционально)")
        output_frame.pack(fill="x", padx=12, pady=6)

        self.output_entry = tk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)

        self.output_button = tk.Button(output_frame, text="Выбрать...", command=self._browse_output)
        self.output_button.pack(side="left", padx=8, pady=6)

        lang_frame = tk.LabelFrame(self.root, text="Языки")
        lang_frame.pack(fill="x", padx=12, pady=6)

        tk.Label(lang_frame, text="Исходный:").pack(side="left", padx=8)
        tk.Entry(lang_frame, textvariable=self.source_var, width=6).pack(side="left", padx=4)
        tk.Label(lang_frame, text="Целевой:").pack(side="left", padx=8)
        tk.Entry(lang_frame, textvariable=self.target_var, width=6).pack(side="left", padx=4)

        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=12, pady=8)

        self.start_button = tk.Button(action_frame, text="Начать перевод", command=self._start_translation)
        self.start_button.pack(side="left", padx=8)

        self.clear_button = tk.Button(action_frame, text="Очистить лог", command=self._clear_log)
        self.clear_button.pack(side="left", padx=8)

        log_frame = tk.LabelFrame(self.root, text="Лог")
        log_frame.pack(fill="both", expand=True, padx=12, pady=6)

        self.log_box = ScrolledText(log_frame, height=12)
        self.log_box.pack(fill="both", expand=True, padx=8, pady=6)
        self.log_box.config(state="disabled")

        self.status_label = tk.Label(self.root, text="Готово", anchor="w")
        self.status_label.pack(fill="x", padx=12, pady=6)

        self._on_mode_change()

    def _on_mode_change(self) -> None:
        if self.mode_var.get() == "jar":
            self.output_entry.delete(0, tk.END)
        else:
            self.output_entry.delete(0, tk.END)

    def _browse_input(self) -> None:
        if self.mode_var.get() == "jar":
            path = filedialog.askopenfilename(
                title="Выберите .jar файл",
                filetypes=[("Minecraft Mod", "*.jar"), ("Все файлы", "*.*")],
            )
        else:
            path = filedialog.askdirectory(title="Выберите папку мода")

        if path:
            self.path_var.set(path)

    def _browse_output(self) -> None:
        if self.mode_var.get() == "jar":
            path = filedialog.asksaveasfilename(
                title="Куда сохранить .jar",
                defaultextension=".jar",
                filetypes=[("Minecraft Mod", "*.jar"), ("Все файлы", "*.*")],
            )
        else:
            path = filedialog.askdirectory(title="Выберите папку для сохранения")

        if path:
            self.output_var.set(path)

    def _set_status(self, text: str) -> None:
        self.status_label.config(text=text)

    def _log(self, text: str) -> None:
        def _append() -> None:
            self.log_box.config(state="normal")
            self.log_box.insert(tk.END, text + "\n")
            self.log_box.see(tk.END)
            self.log_box.config(state="disabled")

        self.root.after(0, _append)

    def _clear_log(self) -> None:
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state="disabled")

    def _start_translation(self) -> None:
        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Ошибка", "Укажи путь к файлу или папке.")
            return

        self.start_button.config(state="disabled")
        self._set_status("Перевод в процессе...")
        self._log("=== Старт перевода ===")

        thread = threading.Thread(target=self._run_translation, daemon=True)
        thread.start()

    def _run_translation(self) -> None:
        try:
            source_lang = self.source_var.get().strip() or "en"
            target_lang = self.target_var.get().strip() or "ru"

            translator = MinecraftModTranslator(source_lang=source_lang, target_lang=target_lang)

            input_path = Path(self.path_var.get().strip())
            output_path = self.output_var.get().strip()

            if self.mode_var.get() == "jar" or input_path.suffix.lower() == ".jar":
                out = None
                if output_path:
                    out_path = Path(output_path)
                    if out_path.is_dir():
                        out = out_path / f"{input_path.stem}_ru.jar"
                    else:
                        out = out_path

                self._log(f"Режим: JAR ({input_path})")
                result = translate_jar_mod(input_path, translator, out)
                self._log(f"Готово: {result}")
            else:
                self._log(f"Режим: папка ({input_path})")
                stats = translator.translate_mod(str(input_path), output_path or None)
                self._log(
                    f"Файлов: {stats['files_processed']} | Переведено: {stats['translated']} | Пропущено: {stats['skipped']}"
                )

            self._set_status("Перевод завершен")
            self._log("=== Завершено ===")
            self.root.after(0, lambda: messagebox.showinfo("Готово", "Перевод завершен."))
        except Exception as exc:
            self._log(f"Ошибка: {exc}")
            self._set_status("Ошибка")
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(exc)))
        finally:
            self.root.after(0, lambda: self.start_button.config(state="normal"))


def main() -> None:
    root = tk.Tk()
    app = TranslatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
