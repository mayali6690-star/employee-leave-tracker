# نظام إدارة إجازات الموظفين - احترافي

## الملفات الموجودة

✅ `app.py` - البرنامج الرئيسي (احترافي - Dark Theme)
✅ `requirements.txt` - المتطلبات والمكتبات
✅ `run.bat` - ملف تشغيل سهل على Windows
✅ `README.md` - التعليمات الكاملة
✅ `employees.json` - ملف البيانات الافتراضية

## التشغيل السريع

### الطريقة الأسهل (Windows):

1. افتح مجلد المشروع
2. ابحث عن ملف `run.bat`
3. اضغط عليه نقرتين
4. البرنامج سيشتغل تلقائياً ✅

### الطريقة اليدوية:

1. افتح PowerShell في المجلد (Shift + Right Click)
2. اكتب:
```bash
python -m pip install reportlab==4.0.4
```
3. ثم:
```bash
python app.py
```

## المواصفات

✨ **واجهة احترافية جداً**
- موضوع أسود وأزرق عصري
- تبويبات منظمة
- قوائم منسدلة

📊 **4 تبويبات رئيسية:**
1. 📈 لوحة التحكم - ملخص إحصائي
2. 👥 الموظفين - إضافة/تعديل/حذف
3. 📅 الإجازات - تفاصيل إجازة كل موظف
4. 📄 التقارير - تقارير PDF وإحصائيات

💾 **حفظ آمن:**
- حفظ تلقائي مع backup
- بدون مشاكل في الحفظ
- بيانات محفوظة محلياً

📊 **تقارير شاملة:**
- تصدير PDF احترافي
- تقارير CSV
- إحصائيات تفصيلية

## حل مشاكل شائعة

**المشكلة: "فشل تشغيل التطبيق"**

الحل:
```bash
python -m pip install --upgrade pip
python -m pip install reportlab==4.0.4
python app.py
```

**المشكلة: "لا توجد وحدة tkinter"**

الحل: Python يجب أن يكون مثبتاً مع tkinter
- حمّل Python من https://www.python.org/downloads/
- تأكد من تحديد ✅ tcl/tk and IDLE

**المشكلة: "فشل في حفظ البيانات"**

الحل: البرنامج سيحفظ البيانات في:
- Windows: `C:\Users\USERNAME\AppData\Roaming\EmployeeLeaveTracker\`
- تأكد من توفر الصلاحيات

## إنشاء exe (اختياري)

إذا تريد ملف تشغيل واحد بدون Python:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed app.py
```

الملف الجديد سيكون في: `dist\app.exe`

---

**تم التطوير بواسطة:** GitHub Copilot
**آخر تحديث:** 2026
