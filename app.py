import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class EmployeeLeaveTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة إجازات الموظفين")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # theme colors
        self.bg_color = '#EAF2FF'
        self.primary_color = '#0057D9'
        self.secondary_color = '#1D6BFF'
        self.dark_color = '#0F2B5B'
        self.button_color = '#0057D9'

        # configure default root bg
        self.root.configure(bg=self.bg_color)

        self.data_file = self.get_data_file()
        self.load_data()
        self.setup_style()
        self.setup_ui()
        self.refresh_all()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.dark_color, font=('Arial', 10))
        style.configure('Title.TLabel', background=self.bg_color, foreground=self.dark_color,
                        font=('Arial', 18, 'bold'))
        style.configure('Header.TLabel', background=self.primary_color, foreground='white',
                        font=('Arial', 13, 'bold'))
        style.configure('TLabelframe', background=self.bg_color)
        style.configure('TLabelframe.Label', background=self.bg_color, foreground=self.dark_color,
                        font=('Arial', 10, 'bold'))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', self.secondary_color)], foreground=[('active', 'white')])
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.secondary_color, foreground='white',
                        font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', self.primary_color), ('!selected', self.secondary_color)])

    def get_data_file(self):
        if getattr(sys, 'frozen', False):
            base = Path(os.environ.get('APPDATA', Path.home())) / 'EmployeeLeaveTracker'
        else:
            base = Path(__file__).resolve().parent
        base.mkdir(parents=True, exist_ok=True)
        return base / 'employees.json'

    def setup_ui(self):
        # header
        self.header = tk.Label(
            self.root,
            text='نظام إدارة إجازات الموظفين',
            bg=self.primary_color,
            fg='white',
            font=('Arial', 18, 'bold'),
            pady=15,
            padx=20
        )
        self.header.pack(fill=tk.X)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # employees tab
        self.employees_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.employees_tab, text='🏢 الموظفين')
        self.setup_employees_tab()

        # leaves tab
        self.leaves_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.leaves_tab, text='📅 الإجازات')
        self.setup_leaves_tab()

        # stats tab
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text='📊 الإحصائيات')
        self.setup_stats_tab()

        self.status_label = ttk.Label(self.root, text='جاهز', relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

    def setup_employees_tab(self):
        frame = ttk.Frame(self.employees_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(frame, text='إضافة / تعديل موظف', padding=15)
        form.pack(fill=tk.X, pady=10)

        ttk.Label(form, text='اسم الموظف:').grid(row=0, column=0, padx=10, pady=8, sticky=tk.W)
        self.name_entry = ttk.Entry(form, width=25)
        self.name_entry.grid(row=0, column=1, padx=10, pady=8)

        ttk.Label(form, text='المسمى الوظيفي:').grid(row=0, column=2, padx=10, pady=8, sticky=tk.W)
        self.position_entry = ttk.Entry(form, width=25)
        self.position_entry.grid(row=0, column=3, padx=10, pady=8)

        ttk.Label(form, text='الإجازة السنوية:').grid(row=1, column=0, padx=10, pady=8, sticky=tk.W)
        self.annual_entry = ttk.Entry(form, width=12)
        self.annual_entry.grid(row=1, column=1, padx=10, pady=8, sticky=tk.W)

        ttk.Label(form, text='المستخدمة:').grid(row=1, column=2, padx=10, pady=8, sticky=tk.W)
        self.used_entry = ttk.Entry(form, width=12)
        self.used_entry.grid(row=1, column=3, padx=10, pady=8, sticky=tk.W)

        ttk.Label(form, text='تاريخ البدء:').grid(row=2, column=0, padx=10, pady=8, sticky=tk.W)
        self.start_date_entry = ttk.Entry(form, width=18)
        self.start_date_entry.grid(row=2, column=1, padx=10, pady=8, sticky=tk.W)
        self.start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=10)
        actions = [
            ('➕ إضافة موظف', self.add_employee),
            ('✏️ تحديث', self.update_employee),
            ('🗑️ حذف', self.delete_employee),
            ('🧹 مسح', self.clear_fields),
            ('💾 حفظ', self.manual_save),
            ('📤 تصدير CSV', self.export_csv),
        ]
        for text, cmd in actions:
            ttk.Button(buttons, text=text, command=cmd).pack(side=tk.LEFT, padx=5)

        table_frame = ttk.LabelFrame(frame, text='قائمة الموظفين', padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.employees_tree = ttk.Treeview(
            table_frame,
            columns=('name', 'position', 'annual', 'used', 'remaining'),
            show='headings',
            yscrollcommand=scroll_y.set
        )
        scroll_y.config(command=self.employees_tree.yview)

        columns = {
            'name': ('اسم الموظف', 170),
            'position': ('المسمى الوظيفي', 180),
            'annual': ('الإجازة السنوية', 110),
            'used': ('المستخدمة', 110),
            'remaining': ('المتبقية', 110),
        }
        for key, (label, width) in columns.items():
            self.employees_tree.heading(key, text=label)
            self.employees_tree.column(key, width=width, anchor=tk.CENTER)
        self.employees_tree.pack(fill=tk.BOTH, expand=True)
        self.employees_tree.bind('<<TreeviewSelect>>', self.on_employee_select)

    def setup_leaves_tab(self):
        frame = ttk.Frame(self.leaves_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(frame)
        top.pack(fill=tk.X, pady=10)
        ttk.Label(top, text='اختر موظف:').pack(side=tk.LEFT, padx=10)
        self.employee_combo = ttk.Combobox(top, state='readonly', width=30)
        self.employee_combo.pack(side=tk.LEFT, padx=10)
        self.employee_combo.bind('<<ComboboxSelected>>', self.refresh_leaves_tab)

        self.leaves_detail = ttk.LabelFrame(frame, text='تفاصيل الإجازة', padding=15)
        self.leaves_detail.pack(fill=tk.BOTH, expand=True)

        self.leaves_info = tk.Label(self.leaves_detail, text='اختر موظفًا لعرض تفاصيل إجازاته',
                                   font=('Arial', 12), bg='white', justify=tk.LEFT, padx=20, pady=30)
        self.leaves_info.pack(fill=tk.BOTH, expand=True)

    def setup_stats_tab(self):
        frame = ttk.Frame(self.stats_tab, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        self.stats_frame = ttk.LabelFrame(frame, text='الإحصائيات', padding=20)
        self.stats_frame.pack(fill=tk.BOTH, expand=True)

        self.stats_label = tk.Label(
            self.stats_frame,
            text='الإحصائيات ستظهر هنا',
            justify=tk.LEFT,
            font=('Courier', 11),
            bg='white',
            padx=20,
            pady=20
        )
        self.stats_label.pack(fill=tk.BOTH, expand=True)

    def get_default_data(self):
        return [
            {'id': 1, 'name': 'أحمد محمد', 'position': 'مهندس برمجيات', 'annual': 30, 'used': 10, 'start_date': '2024-01-01'},
            {'id': 2, 'name': 'فاطمة علي', 'position': 'مديرة مبيعات', 'annual': 30, 'used': 15, 'start_date': '2024-02-01'},
            {'id': 3, 'name': 'محمود حسن', 'position': 'محاسب', 'annual': 30, 'used': 5, 'start_date': '2024-03-01'},
            {'id': 4, 'name': 'نور الدين', 'position': 'مصمم جرافيك', 'annual': 30, 'used': 8, 'start_date': '2024-01-15'},
            {'id': 5, 'name': 'ليلى خالد', 'position': 'مسؤول موارد بشرية', 'annual': 30, 'used': 12, 'start_date': '2024-04-01'},
        ]

    def load_data(self):
        try:
            if self.data_file.exists():
                with self.data_file.open('r', encoding='utf-8') as file:
                    data = json.load(file)
                self.employees = data.get('employees', []) if isinstance(data, dict) else data
                if not isinstance(self.employees, list):
                    raise ValueError('صيغة الملف غير صحيحة')
            else:
                self.employees = self.get_default_data()
                self.save_data()
        except Exception:
            self.employees = self.get_default_data()

    def save_data(self):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            temp = self.data_file.with_suffix('.tmp')
            with temp.open('w', encoding='utf-8') as file:
                json.dump(self.employees, file, ensure_ascii=False, indent=2)
            temp.replace(self.data_file)
            return True
        except Exception as e:
            messagebox.showerror('خطأ', f'تعذر حفظ البيانات:\n{e}')
            return False

    def refresh_all(self):
        self.refresh_employees_table()
        self.refresh_employee_combo()
        self.refresh_stats()
        self.refresh_leaves_tab()

    def refresh_employees_table(self):
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        for emp in self.employees:
            remaining = emp['annual'] - emp['used']
            self.employees_tree.insert('', tk.END, values=(
                emp['name'], emp['position'], emp['annual'], emp['used'], remaining
            ))

    def refresh_employee_combo(self):
        self.employee_combo['values'] = [emp['name'] for emp in self.employees]

    def refresh_leaves_tab(self, event=None):
        name = self.employee_combo.get()
        if not name:
            self.leaves_info.config(text='اختر موظفًا لعرض تفاصيل إجازاته')
            return

        emp = next((e for e in self.employees if e['name'] == name), None)
        if not emp:
            self.leaves_info.config(text='لم يتم العثور على الموظف')
            return

        remaining = emp['annual'] - emp['used']
        percentage_used = (emp['used'] / emp['annual'] * 100) if emp['annual'] else 0
        percentage_remaining = (remaining / emp['annual'] * 100) if emp['annual'] else 0

        text = (
            f"اسم الموظف: {emp['name']}\n"
            f"المسمى: {emp['position']}\n"
            f"تاريخ البدء: {emp.get('start_date', 'غير محدد')}\n\n"
            f"إجمالي الإجازة السنوية: {emp['annual']} يوم\n"
            f"المستخدمة: {emp['used']} يوم\n"
            f"المتبقية: {remaining} يوم\n\n"
            f"نسبة الاستخدام: {percentage_used:.1f}%\n"
            f"نسبة المتبقي: {percentage_remaining:.1f}%"
        )
        self.leaves_info.config(text=text, bg='white', justify=tk.LEFT, font=('Arial', 12), padx=20, pady=20)

    def refresh_stats(self):
        if not self.employees:
            self.stats_label.config(text='لا توجد بيانات')
            return

        total_annual = sum(emp['annual'] for emp in self.employees)
        total_used = sum(emp['used'] for emp in self.employees)
        total_remaining = total_annual - total_used
        avg_remaining = total_remaining / len(self.employees) if self.employees else 0
        top = max(self.employees, key=lambda e: e['used'])
        least = min(self.employees, key=lambda e: e['used'])

        text = (
            f"عدد الموظفين: {len(self.employees)}\n\n"
            f"إجمالي الإجازات السنوية: {total_annual} يوم\n"
            f"إجمالي الإجازات المستخدمة: {total_used} يوم\n"
            f"إجمالي الإجازات المتبقية: {total_remaining} يوم\n\n"
            f"متوسط المتبقي لكل موظف: {avg_remaining:.1f} يوم\n"
            f"نسبة الاستخدام: {(total_used / total_annual * 100):.1f}%\n\n"
            f"أكثر موظف استخدم إجازات: {top['name']} ({top['used']} يوم)\n"
            f"أقل موظف استخدم إجازات: {least['name']} ({least['used']} يوم)"
        )
        self.stats_label.config(text=text, bg='white', justify=tk.LEFT, font=('Courier', 11), padx=20, pady=20)

    def read_form(self):
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        start_date = self.start_date_entry.get().strip()
        if not name or not position:
            messagebox.showwarning('تحذير', 'الرجاء إدخال اسم الموظف والمسمى الوظيفي')
            return None
        try:
            annual = int(self.annual_entry.get())
            used = int(self.used_entry.get())
            if annual < 0 or used < 0 or used > annual:
                raise ValueError
        except ValueError:
            messagebox.showwarning('تحذير', 'أدخل أرقامًا صحيحة، ويجب ألا تتجاوز الاستخدام السنوية')
            return None
        return name, position, annual, used, start_date

    def add_employee(self):
        values = self.read_form()
        if values is None:
            return
        name, position, annual, used, start_date = values
        if any(emp['name'] == name for emp in self.employees):
            messagebox.showwarning('تحذير', 'هذا الموظف موجود بالفعل')
            return
        new_id = max((emp.get('id', 0) for emp in self.employees), default=0) + 1
        self.employees.append({
            'id': new_id,
            'name': name,
            'position': position,
            'annual': annual,
            'used': used,
            'start_date': start_date,
        })
        self.save_data()
        self.refresh_all()
        self.clear_fields()
        self.status_label.config(text=f'✅ تم إضافة الموظف: {name}')

    def update_employee(self):
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning('تحذير', 'اختر موظفًا من الجدول أولاً')
            return
        values = self.read_form()
        if values is None:
            return
        index = self.employees_tree.index(selection[0])
        name, position, annual, used, start_date = values
        self.employees[index].update({
            'name': name,
            'position': position,
            'annual': annual,
            'used': used,
            'start_date': start_date,
        })
        self.save_data()
        self.refresh_all()
        self.clear_fields()
        self.status_label.config(text=f'✅ تم تحديث الموظف: {name}')

    def delete_employee(self):
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning('تحذير', 'اختر موظفًا للحذف')
            return
        if messagebox.askyesno('تأكيد', 'هل تريد حذف هذا الموظف؟'):
            index = self.employees_tree.index(selection[0])
            name = self.employees[index]['name']
            del self.employees[index]
            self.save_data()
            self.refresh_all()
            self.clear_fields()
            self.status_label.config(text=f'✅ تم حذف الموظف: {name}')

    def clear_fields(self):
        for field in (self.name_entry, self.position_entry, self.annual_entry, self.used_entry, self.start_date_entry):
            field.delete(0, tk.END)
        self.start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

    def on_employee_select(self, event=None):
        selection = self.employees_tree.selection()
        if not selection:
            return
        emp = self.employees[self.employees_tree.index(selection[0])]
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, emp['name'])
        self.position_entry.delete(0, tk.END); self.position_entry.insert(0, emp['position'])
        self.annual_entry.delete(0, tk.END); self.annual_entry.insert(0, str(emp['annual']))
        self.used_entry.delete(0, tk.END); self.used_entry.insert(0, str(emp['used']))
        self.start_date_entry.delete(0, tk.END); self.start_date_entry.insert(0, emp.get('start_date', datetime.now().strftime('%Y-%m-%d')))

    def manual_save(self):
        if self.save_data():
            messagebox.showinfo('نجاح', 'تم حفظ البيانات بنجاح')
            self.status_label.config(text='✅ تم الحفظ بنجاح')

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['اسم الموظف', 'المسمى الوظيفي', 'الإجازة السنوية', 'المستخدمة', 'المتبقية', 'تاريخ البدء'])
                for emp in self.employees:
                    writer.writerow([
                        emp['name'], emp['position'], emp['annual'], emp['used'], emp['annual'] - emp['used'], emp.get('start_date', '')
                    ])
            messagebox.showinfo('نجاح', 'تم تصدير البيانات بنجاح')
            self.status_label.config(text='✅ تم تصدير ملف CSV بنجاح')
        except Exception as e:
            messagebox.showerror('خطأ', f'تعذر تصدير الملف:\n{e}')

    def close_app(self):
        self.save_data()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = EmployeeLeaveTracker(root)
    root.mainloop()
