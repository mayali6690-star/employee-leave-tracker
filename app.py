import csv
import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


class EmployeeLeaveTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة إجازات الموظفين")
        self.root.geometry("900x600")
        self.root.minsize(700, 450)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        try:
            self.root.iconbitmap(self.resource_path("icon.ico"))
        except Exception:
            pass

        self.data_file = self.get_data_file()
        self.setup_ui()
        self.load_data()
        self.refresh_table()

    def resource_path(self, filename):
        """Return a bundled resource path when running normally or as an EXE."""
        base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
        return str(Path(base_path) / filename)

    def get_data_file(self):
        """Use a stable writable location so data is not lost when using a shortcut."""
        if getattr(sys, "frozen", False):
            # Windows: %APPDATA%\EmployeeLeaveTracker\employees.json
            base = Path(os.environ.get("APPDATA", Path.home())) / "EmployeeLeaveTracker"
        else:
            # During development, keep the file beside app.py.
            base = Path(__file__).resolve().parent
        base.mkdir(parents=True, exist_ok=True)
        return base / "employees.json"

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text="نظام إدارة إجازات الموظفين",
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        input_frame = ttk.LabelFrame(main_frame, text="إضافة / تعديل موظف", padding=8)
        input_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_frame, text="اسم الموظف:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="المسمى الوظيفي:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.position_entry = ttk.Entry(input_frame, width=30)
        self.position_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="الإجازة السنوية:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.annual_entry = ttk.Entry(input_frame, width=10)
        self.annual_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="المستخدمة:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.used_entry = ttk.Entry(input_frame, width=10)
        self.used_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="إضافة موظف", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تحديث", command=self.update_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حذف", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="مسح الحقول", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حفظ البيانات", command=lambda: self.save_data(show_message=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تصدير CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)

        table_frame = ttk.LabelFrame(main_frame, text="قائمة الموظفين", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("name", "position", "annual", "used", "remaining"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree.yview)
        headings = {
            "name": ("اسم الموظف", 180),
            "position": ("المسمى الوظيفي", 160),
            "annual": ("السنوية", 90),
            "used": ("المستخدمة", 90),
            "remaining": ("المتبقية", 90),
        }
        for column, (heading, width) in headings.items():
            self.tree.heading(column, text=heading)
            self.tree.column(column, anchor=tk.CENTER, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        self.status_label = ttk.Label(main_frame, text="جاهز", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=5)

    def get_default_data(self):
        return [
            {"id": 1, "name": "أحمد محمد", "position": "مهندس برمجيات", "annual": 30, "used": 10},
            {"id": 2, "name": "فاطمة علي", "position": "مديرة مبيعات", "annual": 30, "used": 15},
            {"id": 3, "name": "محمود حسن", "position": "محاسب", "annual": 30, "used": 5},
            {"id": 4, "name": "نور الدين", "position": "مصمم جرافيك", "annual": 30, "used": 8},
            {"id": 5, "name": "ليلى خالد", "position": "مسؤول موارد بشرية", "annual": 30, "used": 12},
        ]

    def load_data(self):
        try:
            if self.data_file.exists():
                with self.data_file.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                # Accept both the old list format and the optional object format.
                self.employees = data.get("employees", []) if isinstance(data, dict) else data
                if not isinstance(self.employees, list):
                    raise ValueError("صيغة ملف البيانات غير صحيحة")
            else:
                self.employees = self.get_default_data()
                self.save_data()
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self.employees = self.get_default_data()
            self.status_label.config(text=f"تعذر قراءة الملف، تم تحميل البيانات الافتراضية: {error}")

    def save_data(self, show_message=False):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            temporary_file = self.data_file.with_suffix(".tmp")
            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(self.employees, file, ensure_ascii=False, indent=2)
            temporary_file.replace(self.data_file)
            self.status_label.config(text=f"تم الحفظ بنجاح: {self.data_file}")
            if show_message:
                messagebox.showinfo("نجاح", "تم حفظ البيانات بنجاح")
            return True
        except OSError as error:
            self.status_label.config(text="فشل الحفظ")
            messagebox.showerror("خطأ في الحفظ", f"تعذر حفظ البيانات:\n{error}")
            return False

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for employee in self.employees:
            remaining = employee["annual"] - employee["used"]
            self.tree.insert("", tk.END, values=(
                employee["name"], employee["position"], employee["annual"], employee["used"], remaining
            ))

    def read_form(self):
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        if not name or not position:
            messagebox.showwarning("تنبيه", "الرجاء ملء اسم الموظف والمسمى الوظيفي")
            return None
        try:
            annual = int(self.annual_entry.get())
            used = int(self.used_entry.get())
            if annual < 0 or used < 0 or used > annual:
                raise ValueError
        except ValueError:
            messagebox.showwarning("تنبيه", "أدخل أرقاماً صحيحة، ويجب ألا تتجاوز المستخدمة السنوية")
            return None
        return name, position, annual, used

    def add_employee(self):
        values = self.read_form()
        if values is None:
            return
        name, position, annual, used = values
        if any(employee["name"] == name for employee in self.employees):
            messagebox.showwarning("تنبيه", "هذا الموظف موجود بالفعل")
            return
        new_id = max((employee.get("id", 0) for employee in self.employees), default=0) + 1
        self.employees.append({"id": new_id, "name": name, "position": position, "annual": annual, "used": used})
        self.save_data()
        self.refresh_table()
        self.clear_fields()
        self.status_label.config(text=f"تمت إضافة الموظف وحفظه: {name}")

    def update_employee(self):
        selection = self.tree.selection()
        values = self.read_form()
        if not selection or values is None:
            if not selection:
                messagebox.showwarning("تنبيه", "اختر موظفاً من الجدول أولاً")
            return
        index = self.tree.index(selection[0])
        name, position, annual, used = values
        self.employees[index].update(name=name, position=position, annual=annual, used=used)
        self.save_data()
        self.refresh_table()
        self.clear_fields()

    def delete_employee(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("تنبيه", "اختر موظفاً من الجدول أولاً")
            return
        if messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا الموظف؟"):
            index = self.tree.index(selection[0])
            name = self.employees[index]["name"]
            del self.employees[index]
            self.save_data()
            self.refresh_table()
            self.clear_fields()
            self.status_label.config(text=f"تم حذف الموظف وحفظ التغيير: {name}")

    def clear_fields(self):
        for entry in (self.name_entry, self.position_entry, self.annual_entry, self.used_entry):
            entry.delete(0, tk.END)

    def on_row_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        employee = self.employees[self.tree.index(selection[0])]
        fields = (self.name_entry, self.position_entry, self.annual_entry, self.used_entry)
        values = (employee["name"], employee["position"], employee["annual"], employee["used"])
        for entry, value in zip(fields, values):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["اسم الموظف", "المسمى الوظيفي", "الإجازة السنوية", "المستخدمة", "المتبقية"])
                for employee in self.employees:
                    writer.writerow([
                        employee["name"], employee["position"], employee["annual"],
                        employee["used"], employee["annual"] - employee["used"],
                    ])
            messagebox.showinfo("نجاح", "تم تصدير البيانات بنجاح")
        except OSError as error:
            messagebox.showerror("خطأ", f"تعذر تصدير البيانات:\n{error}")

    def close_app(self):
        self.save_data()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    EmployeeLeaveTracker(root)
    root.mainloop()
