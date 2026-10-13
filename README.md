<div align="center">

<img src="assets/logo.png" alt="Shalbny Logo" width="110" height="110" />

# 🔄 شقلبني | Shalbny

**مبدّل لغة الكتابة الذكي والفوري لنظام ويندوز (عربي ⟷ إنجليزي)**  
*Smart & Instant Keyboard Layout Text Switcher for Windows*

[![Version](https://img.shields.io/badge/Version-v1.1.0_Stable-2563EB?style=for-the-badge)](https://github.com/ben10943/shalbny/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows_10%20%7C%2011-0078D6?style=for-the-badge&logo=windows)](https://github.com/ben10943/shalbny)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Size](https://img.shields.io/badge/Standalone_Size-11.1_MB-10B981?style=for-the-badge)](https://github.com/ben10943/shalbny/releases)
[![License](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

</div>

---

## 📌 نبذة عن المشروع (Overview)

هل سبق وكتبت جملة كاملة ثم اكتشفت أن لوحة المفاتيح كانت على اللغة الخاطئة؟ (مثل كتابة `hgsghl ugd;l` بدلاً من `السلام عليكم` أو `اثممخ` بدلاً من `hello`)؟

تطبيق **شقلبني (Shalbny)** هو أداة سطح مكتب احترافية، فائقة الخفة والسرعة لنظام ويندوز، تقوم **بتصحيح وعكس لغة النصوص المكتوبة بالخطأ فوراً** في أي برنامج (متصفح، وورد، واتساب، تليجرام، محررات الأكواد...) بمجرد **تحديد النص** والضغط على اختصار لوحة المفاتيح **`Alt + S`**، مع تبديل لغة الكتابة في الويندوز تلقائياً لتكمل كتابتك باللغة الصحيحة دون توقف!

---

## ✨ المميزات الرئيسية (Key Features)

- ⚡ **شقلبة فورية بجزء من الثانية (< 20ms):** حدد أي نص في أي تطبيق واضغط **`Alt + S`** (أو أي اختصار تخصصه بنفسك) ليتم استبداله بالنص الصحيح لحظياً.
- 🧠 **محرك تحويل ثنائي الاتجاه فائق الدقة:**
  - كشف تلقائي ذكي لاتجاه النص (عربي ⟵ إنجليزي أو إنجليزي ⟵ عربي).
  - دعم كامل للحروف المركبة (`لا`، `لأ`، `لإ`، `لآ`) والتشكيل وعلامات الترقيم ورموز `Shift`.
- 🌐 **تبديل تلقائي للغة كيبورد الويندوز:** يحول لغة الإدخال في النظام تلقائياً بعد تصحيح النص عبر واجهات `Win32 API` المباشرة.
- 🛡️ **حماية ذكية للحافظة والمحررات (Safe Clipboard & IDE Guard):**
  - يحتفظ بمحتوى الحافظة الأصلي (Clipboard) ويسترجعه تلقائياً بعد عملية التبديل.
  - مزود بنظام حماية يمنع استبدال السطر بالكامل عن طريق الخطأ في محررات الأكواد (مثل VS Code) إذا ضغطت الاختصار دون تحديد نص.
- 🎨 **واجهة رسومية فاخرة وثنائية اللغة (Arabic ⟷ English UI):**
  - تصميم عصري بمعيار **Double-Bezel Dark/Light UI** مع إمكانية التبديل الفوري بين الواجهة العربية والإنجليزية بضغطة زر.
  - **كونسول تجربة مباشر (Live Playground):** لتجربة شقلبة النصوص داخل الإعدادات مباشرة.
  - **مسجل اختصارات تفاعلي (Custom Hotkey Recorder):** لتخصيص اختصارك المفضل بضغطة واحدة.
- 🔊 **استوديو صوتي مدمج (Modern PCM Audio Engine):**
  - توليد موجات صوتية نقية وناعمة (`Soft Pop`, `Windows Chime`, `Gentle Harmony`) تعمل بشكل غير متزامن مع مفتاح كتم كامل (Master Mute) وزر معاينة حية.
- 📊 **إحصائيات ودليل استخدام تفاعلي:** عداد حي لتتبع عدد النصوص التي تم إنقاذها، مع إمكانية استعادة ضبط المصنع بنقرة واحدة.
- 🚀 **حجم رشيق وبدون أي متطلبات خارجية (Zero Dependencies):**
  - ملف تنفيذي مستقل `Shalbny.exe` بحجم **11.1 MB فقط** يعمل **100% Offline** ويستهلك أقل من **8 MB RAM** في الخلفية بجوار الساعة (System Tray).

---

## 🛠️ المكتبات والتقنيات المستخدمة (Tech Stack & Libraries)

تم بناء المشروع بالاعتماد على معمارية نظيفة (Clean Modular Architecture) باستخدام المكتبات التالية:

| المكتبة / التقنية | الإصدار | الوظيفة والدور داخل المشروع |
| :--- | :---: | :--- |
| **[Python](https://www.python.org/)** | `3.10+` | لغة البرمجة الأساسية للمحرك والواجهة |
| **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** | `>= 5.2.0` | بناء الواجهة الرسومية العصرية (الإعدادات، التبويبات، ومعالج التثبيت `Setup Wizard`) مع دعم الوضعين الداكن والفاتح |
| **[Pillow (PIL)](https://python-pillow.org/)** | `>= 10.0.0` | معالجة ورسم شعار التطبيق والأيقونات عالية الدقة (`PNG` / `ICO`) مع محرك رسم هندسي احتياطي |
| **[pystray](https://github.com/moses-palmer/pystray)** | `>= 0.19.5` | إدارة أيقونة التطبيق في شريط المهام بجوار الساعة (System Tray Icon) والقائمة التفاعلية السريعة |
| **[keyboard](https://github.com/boppreh/keyboard)** | `>= 0.13.5` | الاستماع العام لاختصارات لوحة المفاتيح على مستوى النظام (Global Hotkey Hook) وتسجيل الاختصارات المخصصة |
| **[pyperclip](https://github.com/asweigart/pyperclip)** | `>= 1.11.0` | قراءة وكتابة النصوص في حافظة النظام (Clipboard) واسترجاع محتواها الأصلي بأمان |
| **Win32 API (`ctypes` / `winreg`)** | `Built-in` | محاكاة ضغطات المفاتيح الفورية (`user32.keybd_event`)، تبديل لغة النظام (`WM_INPUTLANGCHANGEREQUEST`)، وإدارة بدء التشغيل التلقائي في سجل الويندوز (`Registry`) |
| **PCM Audio (`winsound` / `wave`)** | `Built-in` | توليد وتشغيل المؤثرات الصوتية النقية في الذاكرة (`In-Memory WAV Synthesis`) بدون ملفات صوتية خارجية |
| **[PyInstaller](https://pyinstaller.org/)** | `>= 6.0` | حزم وضغط التطبيق ومعالج التثبيت في ملفات تنفيذية مستقلة (`.exe`) مع تحسين البايت كود (`optimize=2`) |
| **[Pytest](https://pytest.org/)** | `>= 8.0.0` | إطار الاختبارات الآلية الشاملة (23 اختباراً للتحويل، اللغات، الإعدادات، والصوت) |

---

## 📥 طرق التنزيل والتثبيت (Download & Installation)

### الطريقة الأولى: للمستخدم العادي (بدون الحاجة لتثبيت Python) — *(موصى بها)*

يمكنك تحميل البرنامج جاهزاً للتشغيل مباشرة من صفحة الإصدارات [**GitHub Releases**](https://github.com/ben10943/shalbny/releases):

1. **معالج التثبيت الكامل (`Shalbny_Setup.exe` - 22.1 MB):**
   - قم بتحميل وتشغيل ملف `Shalbny_Setup.exe`.
   - سيفتح لك معالج تثبيت رسومي باللغة العربية يقوم بنسخ التطبيق، وإنشاء اختصار على **سطح المكتب (Desktop)** وفي **قائمة ابدأ (Start Menu)**، وتفعيل التشغيل التلقائي مع الويندوز.
2. **النسخة المحمولة المباشرة (`Shalbny.exe` - 11.1 MB):**
   - قم بتحميل ملف `Shalbny.exe` وتشغيله مباشرة بنقرة مزدوجة بدون أي تثبيت!

---

### الطريقة الثانية: للمطورين (التشغيل من الكود المصدري - Run from Source)

#### 1️⃣ استنساخ المستودع (Clone Repository):
```bash
git clone https://github.com/ben10943/shalbny.git
cd shalbny
```

#### 2️⃣ تثبيت المكتبات المطلوبة (Install Dependencies):
```bash
pip install -r requirements.txt
```

#### 3️⃣ تشغيل التطبيق (Run Application):
- **التشغيل في الخلفية بجوار الساعة (System Tray):**
  ```bash
  python main.py
  ```
- **التشغيل مع فتح نافذة الإعدادات مباشرة:**
  ```bash
  python main.py --settings
  ```
- **تشغيل معالج التثبيت الرسومي من الكود:**
  ```bash
  python installer/setup_wizard.py
  ```

---

## 🏗️ بناء النسخ التنفيذية والاختبار (Building & Testing)

- **تشغيل الاختبارات الآلية الشاملة (23 اختباراً):**
  ```bash
  python -m pytest -v
  ```
- **بناء الملف التنفيذي المستقل المضغوط (`dist/Shalbny.exe`):**
  ```bash
  python build_exe.py
  ```
- **بناء معالج التثبيت المستقل (`dist/Shalbny_Setup.exe`):**
  ```bash
  python build_setup_exe.py
  ```

---

## ⌨️ طريقة الاستخدام في 3 خطوات (How to Use)

1. **حدّد النص:** ظلل الكلمة أو الجملة التي كتبتها باللغة الخاطئة في أي برنامج (بالماوس أو `Shift + الأسهم` أو `Ctrl + A`).
2. **اضغط الاختصار:** اضغط على **`Alt + S`** (أو اختصارك المخصص).
3. **أكمل كتابتك فوراً:** سيتحول النص للغة الصحيحة في جزء من الثانية، وتتبدل لغة كيبورد الويندوز تلقائياً!

---

## 📂 هيكلية المشروع (Project Structure)

```text
shalbny/
├── assets/                  # الشعارات والأيقونات الرسمية (logo.png, icon.ico, tray_icon.png)
├── installer/
│   └── setup_wizard.py      # معالج التثبيت الرسومي لنظام ويندوز (Setup Wizard)
├── src/
│   ├── core/                # محرك التحويل، إدارة اللغات، الاختصارات، والمحرك الصوتي
│   ├── ui/                  # نافذة الإعدادات، أيقونة شريط المهام، وإدارة الأصول المرئية
│   ├── app.py               # المتحكم الرئيسي ودورة حياة التطبيق
│   ├── config.py            # إدارة الإعدادات (JSON) والريجستري (Autostart)
│   └── i18n.py              # نظام الترجمة والتوطين الثنائي (عربي / إنجليزي)
├── tests/                   # اختبارات الوحدة والفحص الشامل (Pytest Suite)
├── main.py                  # نقطة الدخول الرئيسية للتطبيق
├── build_exe.py             # سكربت بناء النسخة التنفيذية المحسّنة (Shalbny.exe)
├── build_setup_exe.py       # سكربت بناء معالج التثبيت (Shalbny_Setup.exe)
├── Shalbny.spec             # إعدادات الضغط والاستبعاد لـ PyInstaller
├── Shalbny_Setup.spec       # إعدادات بناء معالج التثبيت لـ PyInstaller
└── requirements.txt         # قائمة المكتبات المعتمدة
```

---

## 👨‍💻 المطور والتواصل (Developer & Contact)

تم تصميم وتطوير وهندسة هذا المشروع بواسطة:

- **الاسم:** **KHALED ABDELMONEM** *(Lead Software Engineer & System Architect)*
- **GitHub:** [@ben10943](https://github.com/ben10943)
- **LinkedIn:** [khaled-moneam](https://www.linkedin.com/in/khaled-moneam)
- **الهاتف:** `01015362991`

---

## 📄 الترخيص (License)

هذا المشروع مرخص بموجب ترخيص **MIT License** — يمكنك الاطلاع على ملف [LICENSE](LICENSE) لمزيد من التفاصيل.
