import customtkinter as ctk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import os
import keyword
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

PY_KEYWORDS = r"\b(" + "|".join(keyword.kwlist) + r")\b"

class PythonIDE(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("my very own ide in python... made by liquidify.net on discord")
        self.geometry("1100x700")
        self.tab_files = {}
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(top, text="New Tab", command=self.new_tab).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Close Tab", command=self.close_tab, fg_color="#e74c3c").pack(side="left", padx=5)
        ctk.CTkButton(top, text="Open", command=self.open_file).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Save", command=self.save_file).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Run ▶", fg_color="#2ecc71", command=self.run_script).pack(side="left", padx=5)

        self.notebook = ttk.Notebook(self)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1E1E1E', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2D2D2D', foreground='white')
        style.map('TNotebook.Tab', background=[('selected', '#3C3C3C')])
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.new_tab()

    def new_tab(self, content="", filename=None):
        frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(frame, text="Untitled" if not filename else os.path.basename(filename))
        self.tab_files[frame] = filename

        editor_frame = ctk.CTkFrame(frame)
        editor_frame.pack(fill="both", expand=True)

        linenumbers = ctk.CTkTextbox(editor_frame, width=50, state="disabled", fg_color='#1E1E1E', text_color='white')
        linenumbers.pack(side="left", fill="y")

        textbox = ctk.CTkTextbox(editor_frame, wrap="none", fg_color='#1E1E1E', text_color='white')
        textbox.pack(side="right", fill="both", expand=True)
        textbox.insert("1.0", content)

        # Syntax highlighting tags
        textbox.tag_config("keyword", foreground="#569CD6")
        textbox.tag_config("string", foreground="#CE9178")
        textbox.tag_config("comment", foreground="#6A9955")
        textbox.tag_config("number", foreground="#B5CEA8")
        textbox.bind("<KeyRelease>", lambda e, t=textbox, l=linenumbers: self.update_editor(t, l))

        frame.textbox = textbox
        frame.linenumbers = linenumbers
        self.update_editor(textbox, linenumbers)
        return frame

    def get_active_tab(self):
        return self.notebook.nametowidget(self.notebook.select())

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()
        self.new_tab(data, filepath)

    def save_file(self):
        tab = self.get_active_tab()
        filepath = self.tab_files.get(tab)

        # If no file path exists, prompt user to save
        if not filepath:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            )
            if not filepath:
                return
            self.tab_files[tab] = filepath

        # Save file content
        text = tab.textbox.get("1.0", "end")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        # Update tab title
        self.notebook.tab(tab, text=os.path.basename(filepath))

    def close_tab(self):
        tab = self.get_active_tab()
        if tab:
            self.notebook.forget(tab)
            self.tab_files.pop(tab, None)

    def run_script(self):
        tab = self.get_active_tab()
        filepath = self.tab_files.get(tab)
        if not filepath:
            return
        self.save_file()
        file_dir = os.path.dirname(filepath)
        file_name = os.path.basename(filepath)
        cmd = f'cd "{file_dir}"; py "{file_name}"'
        subprocess.Popen(["powershell", "-NoLogo", "-NoProfile", "-Command", cmd])

    def update_editor(self, textbox, linenumbers):
        self.update_linenumbers(textbox, linenumbers)
        self.highlight_syntax(textbox)

    def update_linenumbers(self, textbox, linenumbers):
        text = textbox.get("1.0", "end")
        lines = text.count("\n")
        linenumbers.configure(state="normal")
        linenumbers.delete("1.0", "end")
        for i in range(1, lines + 1):
            linenumbers.insert("end", f"{i}\n")
        linenumbers.configure(state="disabled")

    def highlight_syntax(self, textbox):
        code = textbox.get("1.0", "end")
        for tag in ("keyword", "string", "comment", "number"):
            textbox.tag_remove(tag, "1.0", "end")
        for match in re.finditer(PY_KEYWORDS, code):
            textbox.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r"(['\"]).*?\1", code):
            textbox.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r"#.*", code):
            textbox.tag_add("comment", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        for match in re.finditer(r"\b\d+\b", code):
            textbox.tag_add("number", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

if __name__ == "__main__":
    PythonIDE().mainloop()
