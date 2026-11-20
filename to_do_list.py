"""
To-Do List App
--------------
A simple desktop to-do list built with Python and Tkinter.

Features: add, edit, complete, remove and clear tasks. Tasks are saved
automatically to tasks.json (next to this file) and loaded on startup.
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog

DATA_FILE = Path(__file__).with_name("tasks.json")
OLD_TXT_FILE = Path(__file__).with_name("tasks.txt")  # from the first version


class ToDoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("To-Do List")
        self.root.minsize(420, 420)
        self.tasks = []  # each task: {"text": str, "done": bool}

        self._build_ui()
        self.load_tasks()
        self.refresh()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- UI ----------
    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.task_input = tk.Entry(top, font=("Arial", 11))
        self.task_input.pack(side="left", fill="x", expand=True, ipady=3)
        self.task_input.bind("<Return>", lambda e: self.add_task())
        self.task_input.focus()

        tk.Button(top, text="Add Task", width=10, command=self.add_task).pack(
            side="left", padx=(8, 0)
        )

        mid = tk.Frame(self.root)
        mid.pack(fill="both", expand=True, padx=12, pady=6)

        self.listbox = tk.Listbox(
            mid, font=("Arial", 11), activestyle="none", selectmode="browse"
        )
        scrollbar = tk.Scrollbar(mid, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.listbox.bind("<Double-Button-1>", lambda e: self.toggle_done())
        self.listbox.bind("<Delete>", lambda e: self.remove_task())

        buttons = tk.Frame(self.root)
        buttons.pack(fill="x", padx=12, pady=6)
        for text, cmd in [
            ("Done / Undo", self.toggle_done),
            ("Edit", self.edit_task),
            ("Remove", self.remove_task),
            ("Clear Completed", self.clear_completed),
        ]:
            tk.Button(buttons, text=text, command=cmd).pack(
                side="left", expand=True, fill="x", padx=2
            )

        self.status = tk.Label(self.root, anchor="w", fg="gray30")
        self.status.pack(fill="x", padx=12, pady=(0, 10))

    # ---------- Helpers ----------
    def selected_index(self):
        selection = self.listbox.curselection()
        return selection[0] if selection else None

    def refresh(self, keep=None):
        self.listbox.delete(0, tk.END)
        for i, task in enumerate(self.tasks):
            mark = "[x]" if task["done"] else "[ ]"
            self.listbox.insert(tk.END, f"{mark}  {task['text']}")
            if task["done"]:
                self.listbox.itemconfig(i, fg="gray55")
        if keep is not None and 0 <= keep < len(self.tasks):
            self.listbox.selection_set(keep)
        done = sum(t["done"] for t in self.tasks)
        self.status.config(text=f"{len(self.tasks)} tasks, {done} completed")

    def need_selection(self):
        index = self.selected_index()
        if index is None:
            messagebox.showwarning("Selection Error", "Please select a task first.")
        return index

    # ---------- Actions ----------
    def add_task(self):
        text = self.task_input.get().strip()
        if not text:
            messagebox.showwarning("Input Error", "Task cannot be empty.")
            return
        self.tasks.append({"text": text, "done": False})
        self.task_input.delete(0, tk.END)
        self.save_tasks()
        self.refresh()

    def toggle_done(self):
        index = self.need_selection()
        if index is None:
            return
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        self.save_tasks()
        self.refresh(keep=index)

    def edit_task(self):
        index = self.need_selection()
        if index is None:
            return
        new_text = simpledialog.askstring(
            "Edit Task", "Update the task:", initialvalue=self.tasks[index]["text"],
            parent=self.root,
        )
        if new_text is None:
            return  # cancelled
        new_text = new_text.strip()
        if not new_text:
            messagebox.showwarning("Input Error", "Task cannot be empty.")
            return
        self.tasks[index]["text"] = new_text
        self.save_tasks()
        self.refresh(keep=index)

    def remove_task(self):
        index = self.need_selection()
        if index is None:
            return
        self.tasks.pop(index)
        self.save_tasks()
        self.refresh(keep=min(index, len(self.tasks) - 1))

    def clear_completed(self):
        if not any(t["done"] for t in self.tasks):
            messagebox.showinfo("Nothing to clear", "No completed tasks yet.")
            return
        if messagebox.askyesno("Clear Completed", "Remove all completed tasks?"):
            self.tasks = [t for t in self.tasks if not t["done"]]
            self.save_tasks()
            self.refresh()

    # ---------- Storage ----------
    def save_tasks(self):
        try:
            DATA_FILE.write_text(json.dumps(self.tasks, indent=2), encoding="utf-8")
        except OSError as err:
            messagebox.showerror("Save Error", f"Could not save tasks:\n{err}")

    def load_tasks(self):
        if DATA_FILE.exists():
            try:
                data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self.tasks = [
                    {"text": str(t["text"]), "done": bool(t.get("done", False))}
                    for t in data
                ]
            except (OSError, ValueError, KeyError, TypeError):
                messagebox.showwarning(
                    "Load Error", "tasks.json could not be read. Starting with an empty list."
                )
        elif OLD_TXT_FILE.exists():  # import tasks from the earlier tasks.txt
            lines = OLD_TXT_FILE.read_text(encoding="utf-8").splitlines()
            self.tasks = [{"text": l.strip(), "done": False} for l in lines if l.strip()]

    def on_close(self):
        self.save_tasks()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ToDoApp(root)
    root.mainloop()
