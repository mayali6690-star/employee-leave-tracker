import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from pathlib import Path

class EmployeeLeaveTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("تطبيق حساب إجازات الموظفين")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Set icon if exists
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Data file location
        self.data_file = "employees.json"
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        self.refresh_table()
        
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ttk.Label(main_frame, text="نظام إدارة إجازات الموظفين", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="إضافة/تعديل موظف")
        input_frame.pack(fill=tk.X, pady=10)
        
        # Name
        ttk.Label(input_frame, text="اسم الموظف:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Position
        ttk.Label(input_frame, text="المسمى الوظيفي:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.position_entry = ttk.Entry(input_frame, width=30)
        self.position_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Annual Leave
        ttk.Label(input_frame, text="الإجازة السنوية:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.annual_entry = ttk.Entry(input_frame, width=10)
        self.annual_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Used Leave
        ttk.Label(input_frame, text="الإجازات المستخدمة:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.used_entry = ttk.Entry(input_frame, width=10)
        self.used_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="إضافة موظف", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تحديث", command=self.update_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حذف", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="مسح الحقول", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حفظ البيانات", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تصدير CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        
        # Table Frame
        table_frame = ttk.LabelFrame(main_frame, text="قائمة الموظفين")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview with scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(table_frame, columns=("name", "position", "annual", "used", "remaining"), 
                                 height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("name", anchor=tk.CENTER, width=150)
        self.tree.column("position", anchor=tk.CENTER, width=120)
        self.tree.column("annual", anchor=tk.CENTER, width=80)
        self.tree.column("used", anchor=tk.CENTER, width=80)
        self.tree.column("remaining", anchor=tk.CENTER, width=80)
        
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("name", text="اسم الموظف")
        self.tree.heading("position", text="المسمى الوظيفي")
        self.tree.heading("annual", text="السنوية")
        self.tree.heading("used", text="المستخدمة")
        self.tree.heading("remaining", text="المتبقية")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_row_select)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="جاهز", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, pady=5)
    
    def load_data(self):
        """Load employee data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.employees = json.load(f)
            except:
                self.employees = self.get_default_data()
        else:
            self.employees = self.get_default_data()
            self.save_data()
    
    def get_default_data(self):
        """Get default sample data"""
        return [
            {"id": 1, "name": "أحمد محمد", "position": "مهندس برمجيات", "annual": 30, "used": 10},
            {"id": 2, "name": "فاطمة علي", "position": "مديرة مبيعات", "annual": 30, "used": 15},
            {"id": 3, "name": "محمود حسن", "position": "محاسب", "annual": 30, "used": 5},
            {"id": 4, "name": "نور الدين", "position": "مصمم جرافيك", "annual": 30, "used": 8},
            {"id": 5, "name": "ليلى خالد", "position": "مسؤول موارد بشرية", "annual": 30, "used": 12},
        ]
    
    def save_data(self):
        """Save employee data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.employees, f, ensure_ascii=False, indent=2)
            self.status_label.config(text="تم الحفظ بنجاح ✓")
            messagebox.showinfo("نجاح", "تم حفظ البيانات بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في الحفظ: {str(e)}")
    
    def refresh_table(self):
        """Refresh the employee table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for emp in self.employees:
            remaining = emp["annual"] - emp["used"]
            self.tree.insert("", tk.END, values=(
                emp["name"],
                emp["position"],
                emp["annual"],
                emp["used"],
                remaining
            ))
    
    def add_employee(self):
        """Add new employee"""
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        
        if not name or not position:
            messagebox.showwarning("تحذير", "الرجاء ملء جميع الحقول")
            return
        
        try:
            annual = int(self.annual_entry.get())
            used = int(self.used_entry.get())
        except ValueError:
            messagebox.showwarning("تحذير", "الرجاء إدخال أرقام صحيحة للإجازات")
            return
        
        # Check if employee exists
        if any(emp["name"] == name for emp in self.employees):
            messagebox.showwarning("تحذير", "هذا الموظف موجود بالفعل")
            return
        
        new_id = max([emp["id"] for emp in self.employees], default=0) + 1
        self.employees.append({
            "id": new_id,
            "name": name,
            "position": position,
            "annual": annual,
            "used": used
        })
        
        self.refresh_table()
        self.clear_fields()
        self.status_label.config(text=f"تم إضافة الموظف: {name} ✓")
    
    def update_employee(self):
        """Update selected employee"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("تحذير", "الرجاء اختيار موظف")
            return
        
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        
        if not name or not position:
            messagebox.showwarning("تحذير", "الرجاء ملء جميع الحقول")
            return
        
        try:
            annual = int(self.annual_entry.get())
            used = int(self.used_entry.get())
        except ValueError:
            messagebox.showwarning("تحذير", "الرجاء إدخال أرقام صحيحة")
            return
        
        index = self.tree.index(selection[0])
        self.employees[index].update({
            "name": name,
            "position": position,
            "annual": annual,
            "used": used
        })
        
        self.refresh_table()
        self.clear_fields()
        self.status_label.config(text=f"تم تحديث الموظف: {name} ✓")
    
    def delete_employee(self):
        """Delete selected employee"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("تحذير", "الرجاء اختيار موظف")
            return
        
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذا الموظف؟"):
            index = self.tree.index(selection[0])
            name = self.employees[index]["name"]
            del self.employees[index]
            self.refresh_table()
            self.clear_fields()
            self.status_label.config(text=f"تم حذف الموظف: {name} ✓")
    
    def clear_fields(self):
        """Clear input fields"""
        self.name_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.annual_entry.delete(0, tk.END)
        self.used_entry.delete(0, tk.END)
    
    def on_row_select(self, event):
        """Handle row selection to load data into fields"""
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            emp = self.employees[index]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, emp["name"])
            self.position_entry.delete(0, tk.END)
            self.position_entry.insert(0, emp["position"])
            self.annual_entry.delete(0, tk.END)
            self.annual_entry.insert(0, str(emp["annual"]))
            self.used_entry.delete(0, tk.END)
            self.used_entry.insert(0, str(emp["used"]))
    
    def export_csv(self):
        """Export data to CSV file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("اسم الموظف,المسمى الوظيفي,الإجازة السنوية,المستخدمة,المتبقية\n")
                for emp in self.employees:
                    remaining = emp["annual"] - emp["used"]
                    f.write(f"{emp['name']},{emp['position']},{emp['annual']},{emp['used']},{remaining}\n")
            
            messagebox.showinfo("نجاح", f"تم التصدير بنجاح إلى:\n{file_path}")
            self.status_label.config(text="تم التصدير بنجاح ✓")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeLeaveTracker(root)
    root.mainloop()
