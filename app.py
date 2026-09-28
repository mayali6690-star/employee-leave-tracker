import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class ModernEmployeeLeaveTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة إجازات الموظفين - احترافي")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # Modern Dark Theme Colors
        self.dark_bg = "#1a1a2e"
        self.darker_bg = "#0f3460"
        self.accent_blue = "#00d4ff"
        self.accent_purple = "#7e22ce"
        self.text_light = "#e0e0e0"
        self.text_white = "#ffffff"
        self.success_green = "#10b981"
        self.warning_red = "#ef4444"

        self.root.configure(bg=self.dark_bg)

        # Initialize data file
        self.data_file = self.get_data_file()
        self.load_data()
        
        # Setup theme
        self.setup_modern_style()
        
        # Setup UI
        self.setup_ui()
        self.refresh_all()

    def get_data_file(self):
        """Get stable data file path"""
        if getattr(sys, 'frozen', False):
            base = Path(os.environ.get('APPDATA', Path.home())) / 'EmployeeLeaveTracker'
        else:
            base = Path(__file__).resolve().parent
        base.mkdir(parents=True, exist_ok=True)
        return base / 'employees_data.json'

    def setup_modern_style(self):
        """Setup modern dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.dark_bg)
        style.configure('TLabel', background=self.dark_bg, foreground=self.text_light, font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=self.dark_bg, foreground=self.accent_blue,
                       font=('Segoe UI', 20, 'bold'))
        style.configure('Header.TLabel', background=self.darker_bg, foreground=self.accent_blue,
                       font=('Segoe UI', 12, 'bold'), padding=10)
        style.configure('TLabelframe', background=self.dark_bg, foreground=self.accent_blue)
        style.configure('TLabelframe.Label', background=self.dark_bg, foreground=self.accent_blue,
                       font=('Segoe UI', 11, 'bold'))
        
        # Button style
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), background=self.darker_bg, foreground=self.text_white)
        style.map('TButton',
                 background=[('active', self.accent_purple), ('pressed', self.accent_blue)],
                 foreground=[('active', self.text_white)])
        
        # Notebook (Tabs) style
        style.configure('TNotebook', background=self.dark_bg, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[25, 15], font=('Segoe UI', 11, 'bold'), background=self.darker_bg, foreground=self.text_light)
        style.map('TNotebook.Tab',
                 background=[('selected', self.accent_purple), ('!selected', self.darker_bg)],
                 foreground=[('selected', self.text_white), ('!selected', self.text_light)])
        
        # Entry style
        style.configure('TEntry', fieldbackground=self.darker_bg, foreground=self.text_light, font=('Segoe UI', 10))
        style.configure('TCombobox', fieldbackground=self.darker_bg, foreground=self.text_light, font=('Segoe UI', 10))

    def setup_ui(self):
        """Setup main UI"""
        # Header
        self.header = tk.Label(
            self.root,
            text='📊 نظام إدارة إجازات الموظفين',
            bg=self.darker_bg,
            fg=self.accent_blue,
            font=('Segoe UI', 22, 'bold'),
            pady=20,
            padx=20
        )
        self.header.pack(fill=tk.X)

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Dashboard
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text='📈 لوحة التحكم')
        self.setup_dashboard_tab()

        # Tab 2: Employees
        self.employees_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.employees_tab, text='👥 الموظفين')
        self.setup_employees_tab()

        # Tab 3: Leaves
        self.leaves_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.leaves_tab, text='📅 الإجازات')
        self.setup_leaves_tab()

        # Tab 4: Reports
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text='📄 التقارير')
        self.setup_reports_tab()

        # Status bar
        self.status_label = tk.Label(
            self.root,
            text='✅ جاهز',
            bg=self.dark_bg,
            fg=self.success_green,
            font=('Segoe UI', 10),
            pady=10,
            padx=15,
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_dashboard_tab(self):
        """Setup dashboard"""
        frame = ttk.Frame(self.dashboard_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Stats containers
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill=tk.X, pady=20)

        self.create_stat_card(stats_frame, 'عدد الموظفين', '0', self.accent_blue, 0)
        self.create_stat_card(stats_frame, 'إجمالي الإجازات', '0', self.accent_purple, 1)
        self.create_stat_card(stats_frame, 'الإجازات المستخدمة', '0', self.warning_red, 2)
        self.create_stat_card(stats_frame, 'الإجازات المتبقية', '0', self.success_green, 3)

        # Dashboard info
        info_frame = ttk.LabelFrame(frame, text='📊 ملخص الأداء', padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        self.dashboard_text = tk.Text(
            info_frame,
            bg=self.darker_bg,
            fg=self.text_light,
            font=('Courier', 11),
            height=15,
            width=80,
            borderwidth=0
        )
        self.dashboard_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(info_frame, command=self.dashboard_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dashboard_text['yscrollcommand'] = scrollbar.set

    def create_stat_card(self, parent, title, value, color, column):
        """Create stat card"""
        card = tk.Frame(parent, bg=self.darker_bg, highlightthickness=2, highlightcolor=color)
        card.grid(row=0, column=column, padx=10, pady=10, sticky='nsew', ipadx=20, ipady=15)
        parent.grid_columnconfigure(column, weight=1)

        tk.Label(card, text=title, bg=self.darker_bg, fg=self.text_light, font=('Segoe UI', 11)).pack()
        value_label = tk.Label(card, text=value, bg=self.darker_bg, fg=color, font=('Segoe UI', 24, 'bold'))
        value_label.pack()
        
        # Store reference for updates
        if not hasattr(self, 'stat_cards'):
            self.stat_cards = {}
        self.stat_cards[title] = value_label

    def setup_employees_tab(self):
        """Setup employees management tab"""
        frame = ttk.Frame(self.employees_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Form frame
        form_frame = ttk.LabelFrame(frame, text='➕ إضافة / تعديل موظف', padding=20)
        form_frame.pack(fill=tk.X, pady=10)

        # Row 1
        ttk.Label(form_frame, text='اسم الموظف:').grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.name_entry = ttk.Entry(form_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(form_frame, text='المسمى الوظيفي:').grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        self.position_entry = ttk.Entry(form_frame, width=25)
        self.position_entry.grid(row=0, column=3, padx=10, pady=10)

        # Row 2
        ttk.Label(form_frame, text='الإجازة السنوية:').grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.annual_entry = ttk.Entry(form_frame, width=15)
        self.annual_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        ttk.Label(form_frame, text='المستخدمة:').grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)
        self.used_entry = ttk.Entry(form_frame, width=15)
        self.used_entry.grid(row=1, column=3, padx=10, pady=10, sticky=tk.W)

        ttk.Label(form_frame, text='تاريخ البدء:').grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.start_date_entry = ttk.Entry(form_frame, width=18)
        self.start_date_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        self.start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Menu button instead of individual buttons
        menu_frame = ttk.Frame(frame)
        menu_frame.pack(fill=tk.X, pady=15)

        ttk.Label(menu_frame, text='الإجراءات:').pack(side=tk.LEFT, padx=5)
        
        # Actions menu
        action_menu = ttk.Combobox(menu_frame, state='readonly', width=25, values=[
            '✏️ إضافة موظف جديد',
            '📝 تحديث الموظف المختار',
            '🗑️ حذف الموظف المختار',
            '🧹 مسح الحقول',
            '💾 حفظ البيانات يدويًا',
            '📤 تصدير CSV'
        ])
        action_menu.pack(side=tk.LEFT, padx=10)
        action_menu.bind('<<ComboboxSelected>>', self.handle_action)

        # Table
        table_frame = ttk.LabelFrame(frame, text='📋 قائمة الموظفين', padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.employees_tree = ttk.Treeview(
            table_frame,
            columns=('name', 'position', 'annual', 'used', 'remaining'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=12
        )
        scrollbar.config(command=self.employees_tree.yview)

        columns = {
            'name': ('اسم الموظف', 180),
            'position': ('المسمى الوظيفي', 200),
            'annual': ('السنوية', 100),
            'used': ('المستخدمة', 100),
            'remaining': ('المتبقية', 100),
        }
        for key, (label, width) in columns.items():
            self.employees_tree.heading(key, text=label)
            self.employees_tree.column(key, width=width, anchor=tk.CENTER)

        self.employees_tree.pack(fill=tk.BOTH, expand=True)
        self.employees_tree.bind('<<TreeviewSelect>>', self.on_employee_select)

    def setup_leaves_tab(self):
        """Setup leaves tab"""
        frame = ttk.Frame(self.leaves_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Selection frame
        select_frame = ttk.Frame(frame)
        select_frame.pack(fill=tk.X, pady=10)

        ttk.Label(select_frame, text='🔍 اختر موظف:').pack(side=tk.LEFT, padx=10)
        self.leaves_combo = ttk.Combobox(select_frame, state='readonly', width=35)
        self.leaves_combo.pack(side=tk.LEFT, padx=10)
        self.leaves_combo.bind('<<ComboboxSelected>>', self.refresh_leaves_tab)

        # Details frame
        self.leaves_detail = ttk.LabelFrame(frame, text='📊 تفاصيل الإجازة', padding=20)
        self.leaves_detail.pack(fill=tk.BOTH, expand=True, pady=10)

        self.leaves_info = tk.Text(
            self.leaves_detail,
            bg=self.darker_bg,
            fg=self.text_light,
            font=('Courier', 12),
            height=18,
            width=80,
            borderwidth=0
        )
        self.leaves_info.pack(fill=tk.BOTH, expand=True)

    def setup_reports_tab(self):
        """Setup reports tab"""
        frame = ttk.Frame(self.reports_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text='📄 إنشاء التقارير', style='Title.TLabel').pack(pady=20)

        # Report menu
        report_menu_frame = ttk.Frame(frame)
        report_menu_frame.pack(fill=tk.X, pady=15)

        ttk.Label(report_menu_frame, text='نوع التقرير:').pack(side=tk.LEFT, padx=10)
        
        report_menu = ttk.Combobox(report_menu_frame, state='readonly', width=35, values=[
            '📊 تقرير شامل (PDF)',
            '📋 تقرير الإجازات المستخدمة',
            '⏳ تقرير الإجازات المتبقية',
            '📈 تقرير الإحصائيات',
            '📤 تصدير جميع البيانات (CSV)'
        ])
        report_menu.pack(side=tk.LEFT, padx=10)
        report_menu.bind('<<ComboboxSelected>>', self.handle_report)

        # Report info
        info_frame = ttk.LabelFrame(frame, text='ℹ️ معلومات التقرير', padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        self.report_text = tk.Text(
            info_frame,
            bg=self.darker_bg,
            fg=self.text_light,
            font=('Segoe UI', 10),
            height=15,
            width=80,
            borderwidth=0
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def handle_action(self, event):
        """Handle action menu"""
        action = self.notebook.nametowidget(self.notebook.select()).winfo_name()
        selection = event.widget.get()
        
        if 'إضافة' in selection:
            self.add_employee()
        elif 'تحديث' in selection:
            self.update_employee()
        elif 'حذف' in selection:
            self.delete_employee()
        elif 'مسح' in selection:
            self.clear_fields()
        elif 'حفظ' in selection:
            self.manual_save()
        elif 'تصدير' in selection:
            self.export_csv()
        
        event.widget.set('')

    def handle_report(self, event):
        """Handle report menu"""
        selection = event.widget.get()
        
        if 'شامل' in selection:
            self.generate_pdf_report()
        elif 'المستخدمة' in selection:
            self.show_used_leaves_report()
        elif 'المتبقية' in selection:
            self.show_remaining_leaves_report()
        elif 'الإحصائيات' in selection:
            self.show_statistics_report()
        elif 'CSV' in selection:
            self.export_csv()
        
        event.widget.set('')

    def get_default_data(self):
        """Get default data"""
        return [
            {'id': 1, 'name': 'أحمد محمد', 'position': 'مهندس برمجيات', 'annual': 30, 'used': 10, 'start_date': '2024-01-01'},
            {'id': 2, 'name': 'فاطمة علي', 'position': 'مديرة مبيعات', 'annual': 30, 'used': 15, 'start_date': '2024-02-01'},
            {'id': 3, 'name': 'محمود حسن', 'position': 'محاسب', 'annual': 30, 'used': 5, 'start_date': '2024-03-01'},
            {'id': 4, 'name': 'نور الدين', 'position': 'مصمم جرافيك', 'annual': 30, 'used': 8, 'start_date': '2024-01-15'},
            {'id': 5, 'name': 'ليلى خالد', 'position': 'مسؤول موارد بشرية', 'annual': 30, 'used': 12, 'start_date': '2024-04-01'},
        ]

    def load_data(self):
        """Load data safely"""
        try:
            if self.data_file.exists():
                with self.data_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                self.employees = data if isinstance(data, list) else data.get('employees', [])
                if not isinstance(self.employees, list):
                    self.employees = self.get_default_data()
            else:
                self.employees = self.get_default_data()
                self.save_data()
        except Exception as e:
            self.employees = self.get_default_data()
            self.update_status(f'⚠️ تم تحميل البيانات الافتراضية: {str(e)[:50]}')

    def save_data(self):
        """Save data safely with backup"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup
            backup_file = self.data_file.with_suffix('.backup')
            if self.data_file.exists():
                self.data_file.rename(backup_file)
            
            # Write new data
            with self.data_file.open('w', encoding='utf-8') as f:
                json.dump(self.employees, f, ensure_ascii=False, indent=2)
            
            self.update_status('✅ تم الحفظ بنجاح')
            return True
        except Exception as e:
            self.update_status(f'❌ خطأ في الحفظ: {str(e)[:50]}')
            messagebox.showerror('خطأ', f'فشل الحفظ:\n{e}')
            return False

    def refresh_all(self):
        """Refresh all tabs"""
        self.refresh_employees_tree()
        self.update_employee_combo()
        self.refresh_dashboard()
        self.refresh_leaves_tab()

    def refresh_employees_tree(self):
        """Refresh employees table"""
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        for emp in self.employees:
            remaining = emp['annual'] - emp['used']
            self.employees_tree.insert('', tk.END, values=(
                emp['name'], emp['position'], emp['annual'], emp['used'], remaining
            ))

    def update_employee_combo(self):
        """Update combo boxes"""
        names = [emp['name'] for emp in self.employees]
        self.leaves_combo['values'] = names

    def refresh_dashboard(self):
        """Refresh dashboard"""
        if not self.employees:
            return
        
        total_annual = sum(e['annual'] for e in self.employees)
        total_used = sum(e['used'] for e in self.employees)
        total_remaining = total_annual - total_used
        
        self.stat_cards['عدد الموظفين'].config(text=str(len(self.employees)))
        self.stat_cards['إجمالي الإجازات'].config(text=str(total_annual))
        self.stat_cards['الإجازات المستخدمة'].config(text=str(total_used))
        self.stat_cards['الإجازات المتبقية'].config(text=str(total_remaining))
        
        # Update dashboard text
        self.dashboard_text.delete('1.0', tk.END)
        
        top_user = max(self.employees, key=lambda e: e['used']) if self.employees else None
        least_user = min(self.employees, key=lambda e: e['used']) if self.employees else None
        
        dashboard_content = f"""
{'='*70}
                    ملخص إدارة الإجازات
{'='*70}

📊 الإحصائيات العامة:
   • عدد الموظفين: {len(self.employees)}
   • إجمالي الإجازات السنوية: {total_annual} يوم
   • الإجازات المستخدمة: {total_used} يوم
   • الإجازات المتبقية: {total_remaining} يوم

📈 النسب المئوية:
   • معدل الاستخدام: {(total_used/total_annual*100):.1f}%
   • النسبة المتبقية: {(total_remaining/total_annual*100):.1f}%

🏆 الأداء الفردي:
   • أكثر موظف استخدم إجازات: {top_user['name']} ({top_user['used']} يوم)
   • أقل موظف استخدم إجازات: {least_user['name']} ({least_user['used']} يوم)

{'='*70}
        """
        
        self.dashboard_text.insert('1.0', dashboard_content)

    def refresh_leaves_tab(self, event=None):
        """Refresh leaves details"""
        name = self.leaves_combo.get()
        if not name:
            self.leaves_info.delete('1.0', tk.END)
            self.leaves_info.insert('1.0', 'اختر موظفًا لعرض تفاصيل إجازاته')
            return
        
        emp = next((e for e in self.employees if e['name'] == name), None)
        if not emp:
            return
        
        remaining = emp['annual'] - emp['used']
        percentage_used = (emp['used'] / emp['annual'] * 100) if emp['annual'] else 0
        
        content = f"""
{'='*70}
                    تفاصيل إجازة الموظف
{'='*70}

👤 بيانات الموظف:
   • الاسم: {emp['name']}
   • المسمى الوظيفي: {emp['position']}
   • تاريخ البدء: {emp.get('start_date', 'غير محدد')}

📅 الإجازات:
   • الإجازة السنوية: {emp['annual']} يوم
   • المستخدمة: {emp['used']} يوم
   • المتبقية: {remaining} يوم

📊 الإحصائيات:
   • نسبة الاستخدام: {percentage_used:.1f}%
   • النسبة المتبقية: {(100-percentage_used):.1f}%

⏳ معلومات إضافية:
   • متوسط الإجازة الشهري: {(emp['annual']/12):.1f} يوم
   • الإجازات المتوقعة المتبقية: {remaining} يوم

{'='*70}
        """
        
        self.leaves_info.delete('1.0', tk.END)
        self.leaves_info.insert('1.0', content)

    def read_form(self):
        """Read form data"""
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        start_date = self.start_date_entry.get().strip()
        
        if not name or not position:
            messagebox.showwarning('تحذير', 'أدخل اسم الموظف والمسمى الوظيفي')
            return None
        
        try:
            annual = int(self.annual_entry.get())
            used = int(self.used_entry.get())
            if annual < 0 or used < 0 or used > annual:
                raise ValueError('الأرقام غير صحيحة')
        except ValueError:
            messagebox.showwarning('تحذير', 'أدخل أرقامًا صحيحة')
            return None
        
        return name, position, annual, used, start_date

    def add_employee(self):
        """Add employee"""
        values = self.read_form()
        if not values:
            return
        
        name, position, annual, used, start_date = values
        
        if any(e['name'] == name for e in self.employees):
            messagebox.showwarning('تحذير', 'الموظف موجود بالفعل')
            return
        
        new_id = max((e.get('id', 0) for e in self.employees), default=0) + 1
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
        self.update_status(f'✅ تم إضافة الموظف: {name}')

    def update_employee(self):
        """Update employee"""
        selection = self.employees_tree.selection()
        if not selection:
            messagebox.showwarning('تحذير', 'اختر موظفًا من الجدول')
            return
        
        values = self.read_form()
        if not values:
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
        self.update_status(f'✅ تم تحديث: {name}')

    def delete_employee(self):
        """Delete employee"""
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
            self.update_status(f'✅ تم حذف: {name}')

    def clear_fields(self):
        """Clear form"""
        for field in (self.name_entry, self.position_entry, self.annual_entry, self.used_entry):
            field.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

    def on_employee_select(self, event):
        """Load employee to form"""
        selection = self.employees_tree.selection()
        if not selection:
            return
        
        emp = self.employees[self.employees_tree.index(selection[0])]
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, emp['name'])
        self.position_entry.delete(0, tk.END); self.position_entry.insert(0, emp['position'])
        self.annual_entry.delete(0, tk.END); self.annual_entry.insert(0, str(emp['annual']))
        self.used_entry.delete(0, tk.END); self.used_entry.insert(0, str(emp['used']))
        self.start_date_entry.delete(0, tk.END); self.start_date_entry.insert(0, emp.get('start_date', ''))

    def manual_save(self):
        """Manual save"""
        if self.save_data():
            messagebox.showinfo('نجاح', 'تم حفظ البيانات بنجاح')

    def export_csv(self):
        """Export CSV"""
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['اسم الموظف', 'المسمى', 'السنوية', 'المستخدمة', 'المتبقية', 'البدء'])
                for emp in self.employees:
                    writer.writerow([
                        emp['name'], emp['position'], emp['annual'], emp['used'],
                        emp['annual'] - emp['used'], emp.get('start_date', '')
                    ])
            messagebox.showinfo('نجاح', 'تم التصدير بنجاح')
            self.update_status('✅ تم تصدير CSV')
        except Exception as e:
            messagebox.showerror('خطأ', f'فشل التصدير: {e}')

    def generate_pdf_report(self):
        """Generate PDF report"""
        file_path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF', '*.pdf')])
        if not file_path:
            return
        
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#00d4ff'),
                alignment=1,
            )
            story.append(Paragraph('تقرير إدارة الإجازات', title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Date
            story.append(Paragraph(f'التاريخ: {datetime.now().strftime("%Y-%m-%d %H:%M")}', getSampleStyleSheet()['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Summary
            total_annual = sum(e['annual'] for e in self.employees)
            total_used = sum(e['used'] for e in self.employees)
            total_remaining = total_annual - total_used
            
            summary_data = [
                ['البيان', 'القيمة'],
                ['عدد الموظفين', str(len(self.employees))],
                ['إجمالي الإجازات', f'{total_annual} يوم'],
                ['المستخدمة', f'{total_used} يوم'],
                ['المتبقية', f'{total_remaining} يوم'],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Employees table
            story.append(Paragraph('تفاصيل الموظفين', getSampleStyleSheet()['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            emp_data = [['الاسم', 'المسمى', 'السنوية', 'المستخدمة', 'المتبقية']]
            for emp in self.employees:
                emp_data.append([
                    emp['name'],
                    emp['position'],
                    str(emp['annual']),
                    str(emp['used']),
                    str(emp['annual'] - emp['used']),
                ])
            
            emp_table = Table(emp_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
            emp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(emp_table)
            
            doc.build(story)
            messagebox.showinfo('نجاح', 'تم إنشاء التقرير بنجاح')
            self.update_status('✅ تم إنشاء تقرير PDF')
        except Exception as e:
            messagebox.showerror('خطأ', f'فشل إنشاء التقرير: {e}')

    def show_used_leaves_report(self):
        """Show used leaves report"""
        self.report_text.delete('1.0', tk.END)
        
        content = "📋 تقرير الإجازات المستخدمة\n"
        content += "="*70 + "\n\n"
        
        for emp in sorted(self.employees, key=lambda e: e['used'], reverse=True):
            percentage = (emp['used'] / emp['annual'] * 100) if emp['annual'] else 0
            content += f"{emp['name']:20} {emp['position']:20} {emp['used']:3}/30 أيام ({percentage:.1f}%)\n"
        
        self.report_text.insert('1.0', content)

    def show_remaining_leaves_report(self):
        """Show remaining leaves report"""
        self.report_text.delete('1.0', tk.END)
        
        content = "⏳ تقرير الإجازات المتبقية\n"
        content += "="*70 + "\n\n"
        
        for emp in sorted(self.employees, key=lambda e: e['annual'] - e['used'], reverse=True):
            remaining = emp['annual'] - emp['used']
            percentage = (remaining / emp['annual'] * 100) if emp['annual'] else 0
            content += f"{emp['name']:20} {emp['position']:20} {remaining:3} أيام ({percentage:.1f}%)\n"
        
        self.report_text.insert('1.0', content)

    def show_statistics_report(self):
        """Show statistics report"""
        self.report_text.delete('1.0', tk.END)
        
        total_annual = sum(e['annual'] for e in self.employees)
        total_used = sum(e['used'] for e in self.employees)
        total_remaining = total_annual - total_used
        
        content = "📈 تقرير الإحصائيات\n"
        content += "="*70 + "\n\n"
        content += f"عدد الموظفين: {len(self.employees)}\n"
        content += f"إجمالي الإجازات: {total_annual} يوم\n"
        content += f"المستخدمة: {total_used} يوم\n"
        content += f"المتبقية: {total_remaining} يوم\n"
        content += f"معدل الاستخدام: {(total_used/total_annual*100):.1f}%\n\n"
        
        if self.employees:
            top = max(self.employees, key=lambda e: e['used'])
            least = min(self.employees, key=lambda e: e['used'])
            content += f"أكثر استخدامًا: {top['name']} ({top['used']} يوم)\n"
            content += f"أقل استخدامًا: {least['name']} ({least['used']} يوم)\n"
        
        self.report_text.insert('1.0', content)

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text='✅ جاهز'))

    def close_app(self):
        """Close app"""
        self.save_data()
        self.root.destroy()


if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = ModernEmployeeLeaveTracker(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror('خطأ', f'فشل تشغيل البرنامج:\n{e}')
