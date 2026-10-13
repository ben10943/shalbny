"""
Internationalization (i18n) module for Shalbny.
Provides complete Arabic and English translation dictionaries and localization helpers.
"""
from typing import Dict, Any


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ar": {
        # Header & Status
        "app_title": "شقلبني | Shalbny",
        "engine_running": "🟢 المحرك يعمل الآن",
        "engine_paused": "⏸️ المحرك متوقف مؤقتاً",
        "theme_light": "☀️ الفاتح",
        "theme_dark": "🌙 الداكن",
        "lang_switch_btn": "🌐 English",

        # Tabs
        "tab_general": "⚙️ الإعدادات العامة",
        "tab_shortcut": "⌨️ مفتاح الاختصار",
        "tab_stats": "📊 الإحصائيات والدليل",
        "tab_developer": "👨‍💻 المطور والمعلومات",

        # How to use Guide
        "guide_title": "📖 دليل الاستخدام السريع (3 خطوات فقط):",
        "guide_step1": "1️⃣ حدد أي نص مكتوب بالخطأ في أي برنامج أو متصفح.",
        "guide_step2": "2️⃣ اضغط على الاختصار [ Alt + S ].",
        "guide_step3": "3️⃣ ينقلب النص فوراً وتتبدل لغة كيبورد الويندوز تلقائياً!",

        # General Tab
        "profile_label": "🌐 ملف لغة التبديل:",
        "behavior_title": "⚙️ سلوك النظام والحافظة:",
        "switch_layout_lbl": "تبديل لغة كيبورد الويندوز تلقائياً بعد الشقلبة",
        "restore_clipboard_lbl": "استرجاع الحافظة السابقة (عدم فقدان ما تم نسخه)",
        "autostart_lbl": "بدء التشغيل تلقائياً مع تشغيل جهاز الكمبيوتر",
        "audio_title": "🔊 إعدادات الصوت والتنبيه:",
        "sound_lbl": "تشغيل تنبيه صوتي عند نجاح الشقلبة",
        "sound_theme_lbl": "نغمة التنبيه:",
        "tone_soft_pop": "🫧 نقرة فقاعة ناعمة (Soft Pop - هادئة ومريحة)",
        "tone_windows_chime": "🔔 رنة ويندوز الهادئة (Windows Chime)",
        "tone_gentle_harmony": "🎵 نغمة تأكيد موسيقية (Gentle Harmony)",
        "tone_mute": "🔇 كتم الصوت تماماً (Silent / Mute)",
        "test_sound_btn": "▶️ استمع للنغمة",
        "playground_title": "🧪 صندوق التجربة المباشرة (Playground):",
        "playground_desc": "حدد النص أدناه ثم اضغط الاختصار، أو اضغط زر الشقلبة للتجربة:",
        "playground_placeholder": "اكتب هنا مثلا: fdv,j أو اثممخ",
        "flip_btn": "⚡ شقلب النص الآن",

        # Shortcut Tab
        "hotkey_active_lbl": "الاختصار النشط حالياً:",
        "record_btn_idle": "🎙️ تسجيل اختصار جديد (اضغط أي زر في الكيبورد)",
        "record_btn_listening": "⏳ اضغط أي زر أو تركيبة مفاتيح الآن...",
        "listening_badge": "[ جاري الاستماع... ]",
        "conflict_badge": "❌ فشل التسجيل (تعارض)",
        "presets_title": "أو اختر من الاختصارات السريعة الموصى بها:",
        "preset_alt_s": "Alt + S (المفضل والموصى به - خفيف وبدون أي تعارض)",
        "preset_ctrl_alt_s": "Ctrl + Alt + S (ثلاثي آمن 100% ومستحيل يتعارض)",
        "preset_alt_q": "Alt + Q (سريع ومريح جداً لليد اليسرى)",
        "preset_ctrl_shift_x": "Ctrl + Shift + X (مألوف وسهل)",
        "preset_ctrl_shift_s": "Ctrl + Shift + S (اختصار بديل خفيف)",
        "preset_alt_z": "Alt + Z (سريع وسهل الوصول)",

        # Stats & Guide Tab
        "stats_title": "📈 إحصائيات الاستخدام والإنقاذ:",
        "stats_count_lbl": "إجمالي النصوص التي تم شقلبتها بنجاح:",
        "stats_unit": "مرة",
        "stats_reset_btn": "🔄 تصفير العداد",
        "reset_defaults_title": "⚙️ ضبط المصنع واستعادة الإعدادات:",
        "reset_defaults_btn": "⚠️ استعادة كافة الإعدادات الافتراضية",
        "reset_done_msg": "تمت استعادة الإعدادات الافتراضية بنجاح!",

        # Developer Tab
        "dev_name": "KHALED ABDELMONEM",
        "dev_role": "Lead Software Engineer & System Architect",
        "dev_bio": "مهندس برمجيات ومطور حلول تقنية متقدمة | مطور شقلبني",
        "contacts_title": "🌐 حسابات المطور وبيانات التواصل:",
        "github_lbl": "🐙 GitHub:",
        "linkedin_lbl": "💼 LinkedIn:",
        "phone_lbl": "📞 الهاتف:",
        "open_link_btn": "فتح الحساب",
        "copy_btn": "نسخ",
        "save_and_copy_btn": "حفظ ونسخ",
        "copied_feedback": "تم النسخ!",
        "specs_title": "📊 المواصفات التقنية والمعمارية:",
        "spec_lead_dev": "المطور المسؤول:",
        "spec_version_lbl": "الإصدار:",
        "spec_version_val": "1.1.0 Stable (Windows 10 / 11 Native)",
        "spec_arch_lbl": "المعمارية:",
        "spec_arch_val": "Win32 Low-Level Keyboard Hook (WH_KEYBOARD_LL)",
        "spec_engine_lbl": "المحرك:",
        "spec_engine_val": "Shalbny Unicode Bi-directional Engine",
        "spec_latency_lbl": "زمن الاستجابة:",
        "spec_latency_val": "فوري (< 15ms)",
        "spec_memory_lbl": "استهلاك الذاكرة:",
        "spec_memory_val": "خفيف جداً (< 25MB RAM / 0% CPU Idle)",
        "spec_clipboard_lbl": "حماية الحافظة:",
        "spec_clipboard_val": "استرجاع تلقائي آمن للـ Clipboard",
        "spec_license_lbl": "الترخيص:",
        "spec_license_val": "MIT License (حر ومجاني بالكامل)",
        "check_updates_btn": "🔍 فحص التحديثات",
        "up_to_date_msg": "أنت تستخدم أحدث إصدار متوفر (v1.1.0)! ✨",

        # Tray Menu
        "tray_app_name": "شقلبني | Shalbny",
        "tray_tooltip_running": "شقلبني v1.1.0 (Alt + S) • المحرك نشط",
        "tray_tooltip_paused": "شقلبني v1.1.0 • المحرك متوقف مؤقتاً",
        "tray_open_settings": "لوحة التحكم والإعدادات...",
        "tray_guide": "دليل الاستخدام السريع...",
        "tray_hotkey_info": "اختصار الشقلبة: [ Alt + S ]",
        "tray_pause": "إيقاف المحرك مؤقتاً",
        "tray_resume": "استئناف تشغيل المحرك",
        "tray_exit": "إنهاء التطبيق"
    },
    "en": {
        # Header & Status
        "app_title": "Shalbny | Text Switcher",
        "engine_running": "🟢 Engine Active",
        "engine_paused": "⏸️ Engine Paused",
        "theme_light": "☀️ Light",
        "theme_dark": "🌙 Dark",
        "lang_switch_btn": "🌐 العربية",

        # Tabs
        "tab_general": "⚙️ General",
        "tab_shortcut": "⌨️ Shortcut Key",
        "tab_stats": "📊 Stats & Guide",
        "tab_developer": "👨‍💻 Developer & About",

        # How to use Guide
        "guide_title": "📖 Quick How-to-Use (Only 3 Steps):",
        "guide_step1": "1️⃣ Select mistyped text in any program or browser.",
        "guide_step2": "2️⃣ Press hotkey [ Alt + S ].",
        "guide_step3": "3️⃣ Text inverts instantly and Windows keyboard layout switches!",

        # General Tab
        "profile_label": "🌐 Language Switch Profile:",
        "behavior_title": "⚙️ System & Clipboard Behavior:",
        "switch_layout_lbl": "Automatically switch Windows keyboard layout after conversion",
        "restore_clipboard_lbl": "Restore previous clipboard content (never lose copies)",
        "autostart_lbl": "Start automatically when Windows boots",
        "audio_title": "🔊 Audio & Feedback Settings:",
        "sound_lbl": "Play subtle audio chime on successful conversion",
        "sound_theme_lbl": "Notification Tone:",
        "tone_soft_pop": "🫧 Soft Bubble Pop (Gentle & Modern)",
        "tone_windows_chime": "🔔 Windows Subtle Chime",
        "tone_gentle_harmony": "🎵 Gentle Musical Harmony",
        "tone_mute": "🔇 Completely Mute (Silent)",
        "test_sound_btn": "▶️ Preview Sound",
        "playground_title": "🧪 Interactive Playground:",
        "playground_desc": "Select text below and press hotkey, or click Flip button to test:",
        "playground_placeholder": "Type here e.g.: fdv,j or اثممخ",
        "flip_btn": "⚡ Flip Text Now",

        # Shortcut Tab
        "hotkey_active_lbl": "Currently Active Hotkey:",
        "record_btn_idle": "🎙️ Record New Shortcut (Press any key on keyboard)",
        "record_btn_listening": "⏳ Press any key or key combination now...",
        "listening_badge": "[ Listening... ]",
        "conflict_badge": "❌ Registration Failed (Conflict)",
        "presets_title": "Or pick from recommended fast presets:",
        "preset_alt_s": "Alt + S (Recommended - Fast & Zero Conflicts)",
        "preset_ctrl_alt_s": "Ctrl + Alt + S (Triple Key 100% Conflict-Free)",
        "preset_alt_q": "Alt + Q (Fast and ergonomic for left hand)",
        "preset_ctrl_shift_x": "Ctrl + Shift + X (Familiar and easy)",
        "preset_ctrl_shift_s": "Ctrl + Shift + S (Lightweight alternative)",
        "preset_alt_z": "Alt + Z (Fast and accessible)",

        # Stats & Guide Tab
        "stats_title": "📈 Rescue & Conversion Stats:",
        "stats_count_lbl": "Total text inversions performed successfully:",
        "stats_unit": "times",
        "stats_reset_btn": "🔄 Reset Counter",
        "reset_defaults_title": "⚙️ Factory Reset & Defaults:",
        "reset_defaults_btn": "⚠️ Reset All Settings to Default",
        "reset_done_msg": "Settings reset to defaults successfully!",

        # Developer Tab
        "dev_name": "KHALED ABDELMONEM",
        "dev_role": "Lead Software Engineer & System Architect",
        "dev_bio": "Software Engineer & Solutions Architect | Creator of Shalbny",
        "contacts_title": "🌐 Developer Social & Contact Info:",
        "github_lbl": "🐙 GitHub:",
        "linkedin_lbl": "💼 LinkedIn:",
        "phone_lbl": "📞 Phone:",
        "open_link_btn": "Open Profile",
        "copy_btn": "Copy",
        "save_and_copy_btn": "Save & Copy",
        "copied_feedback": "Copied!",
        "specs_title": "📊 Technical & Architectural Specifications:",
        "spec_lead_dev": "Lead Developer:",
        "spec_version_lbl": "Version:",
        "spec_version_val": "1.1.0 Stable (Windows 10 / 11 Native)",
        "spec_arch_lbl": "Architecture:",
        "spec_arch_val": "Win32 Low-Level Keyboard Hook (WH_KEYBOARD_LL)",
        "spec_engine_lbl": "Engine:",
        "spec_engine_val": "Shalbny Unicode Bi-directional Engine",
        "spec_latency_lbl": "Latency:",
        "spec_latency_val": "Instant (< 15ms)",
        "spec_memory_lbl": "Memory Footprint:",
        "spec_memory_val": "Ultra-lightweight (< 25MB RAM / 0% CPU Idle)",
        "spec_clipboard_lbl": "Clipboard Safety:",
        "spec_clipboard_val": "Safe automatic dual-stage clipboard restoration",
        "spec_license_lbl": "License:",
        "spec_license_val": "MIT License (Free & Open Source)",
        "check_updates_btn": "🔍 Check for Updates",
        "up_to_date_msg": "You are running the latest version (v1.1.0)! ✨",

        # Tray Menu
        "tray_app_name": "Shalbny | Text Switcher",
        "tray_tooltip_running": "Shalbny v1.1.0 (Alt + S) • Engine Active",
        "tray_tooltip_paused": "Shalbny v1.1.0 • Engine Paused",
        "tray_open_settings": "Control Center & Settings...",
        "tray_guide": "Quick How-to-Use Guide...",
        "tray_hotkey_info": "Active Hotkey: [ Alt + S ]",
        "tray_pause": "Pause Engine",
        "tray_resume": "Resume Engine",
        "tray_exit": "Exit Shalbny"
    }
}


class I18n:
    """Manages application locale and string translations."""

    def __init__(self, current_lang: str = "ar"):
        self.lang = current_lang if current_lang in TRANSLATIONS else "ar"

    def set_language(self, lang: str) -> None:
        if lang in TRANSLATIONS:
            self.lang = lang

    def t(self, key: str, **kwargs) -> str:
        """Retrieves translated text for given key."""
        text = TRANSLATIONS.get(self.lang, {}).get(key)
        if text is None:
            # Fallback to Arabic
            text = TRANSLATIONS.get("ar", {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text


# Global singleton instance
i18n = I18n("ar")
