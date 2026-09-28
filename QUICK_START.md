# تطبيق إدارة إجازات الموظفين - دليل سريع

## البدء السريع 🚀

### 1️⃣ التشغيل المباشر (بدون تثبيت)
```bash
python app.py
```

### 2️⃣ إنشاء ملف تنفيذي (Executable)

#### على Windows:
```bash
build_executable.bat
```

#### على Linux/Mac:
```bash
chmod +x build_executable.sh
./build_executable.sh
```

## المميزات الرئيسية

| الميزة | الوصف |
|--------|-------|
| 📝 إضافة موظف | أضف موظفين جدد بسهولة |
| ✏️ تعديل البيانات | عدّل معلومات الموظفين |
| 🗑️ حذف الموظفين | احذف الموظفين من النظام |
| 💾 حفظ تلقائي | احفظ بياناتك تلقائياً |
| 📊 تصدير CSV | صدّر البيانات لـ Excel |
| 🌐 بدون انترنت | يعمل بدون اتصال انترنت |

## الأوامر السريعة

```bash
# التثبيت
pip install -r requirements.txt

# التشغيل
python app.py

# البناء على Windows
pyinstaller --onefile --windowed app.py

# البناء على Linux/Mac
pyinstaller --onefile --windowed app.py
```

## استكشاف الأخطاء

**المشكلة**: "ModuleNotFoundError"  
**الحل**: `pip install -r requirements.txt`

**المشكلة**: التطبيق لا يشتغل  
**الحل**: تأكد من استخدام Python 3.7+

**المشكلة**: البيانات لا تُحفظ  
**الحل**: تأكد من صلاحيات المجلد وأن ملف `employees.json` موجود

---

لمزيد من المعلومات، اقرأ `README.md`
