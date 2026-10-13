"""
Official Setup Wizard for Shalbny (معالج تثبيت شقلبني).
A modern, native Windows installer wizard built with CustomTkinter.
Handles installing files, creating Desktop and Start Menu shortcuts,
and configuring Windows autostart.
"""
import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
import customtkinter as ctk
from PIL import Image

# Ensure root directory is in sys.path
BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(BASE_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_PROJECT_DIR))

# Directories
if getattr(sys, "frozen", False):
    SOURCE_DIR = Path(sys._MEIPASS)
else:
    SOURCE_DIR = BASE_PROJECT_DIR

DEFAULT_INSTALL_DIR = Path.home() / "AppData" / "Local" / "Programs" / "Shalbny"


def get_user_folder(folder_name: str, fallback: Path) -> Path:
    """Accurately resolves Windows User Shell Folders (including OneDrive redirection)."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
        val, _ = winreg.QueryValueEx(key, folder_name)
        return Path(os.path.expandvars(val))
    except Exception:
        return fallback


class SetupWizard:
    """Graphical Windows Setup Installer for Shalbny."""

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("معالج تثبيت برنامج شقلبني | Shalbny Setup")
        self.root.geometry("540x620")
        self.root.resizable(False, False)

        self.logo_path = SOURCE_DIR / "assets" / "logo.png"
        self.icon_path = SOURCE_DIR / "assets" / "icon.ico"

        if self.icon_path.exists():
            try:
                self.root.iconbitmap(str(self.icon_path))
            except Exception:
                pass

        # Options state
        self.install_dir_var = ctk.StringVar(value=str(DEFAULT_INSTALL_DIR))
        self.create_desktop_var = ctk.BooleanVar(value=True)
        self.create_startmenu_var = ctk.BooleanVar(value=True)
        self.autostart_var = ctk.BooleanVar(value=True)
        self.launch_now_var = ctk.BooleanVar(value=True)

        self.current_step = 0
        self.steps = [
            self._render_welcome,
            self._render_location,
            self._render_options,
            self._render_installing,
            self._render_finish
        ]

        # Main dynamic container
        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self._show_step(0)

    def _show_step(self, step_idx: int) -> None:
        self.current_step = step_idx
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        self.steps[step_idx]()

    # -------------------------------------------------------------
    # STEP 0: Welcome Screen
    # -------------------------------------------------------------
    def _render_welcome(self) -> None:
        try:
            if self.logo_path.exists():
                pil_logo = Image.open(self.logo_path)
            else:
                from src.ui.assets import create_app_icon
                pil_logo = create_app_icon(size=90)
            logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(90, 90))
            ctk.CTkLabel(self.container, image=logo_ctk, text="").pack(pady=(20, 10))
        except Exception:
            pass

        ctk.CTkLabel(
            self.container,
            text="مرحباً بك في معالج تثبيت شقلبني",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        ).pack(pady=(5, 5))

        ctk.CTkLabel(
            self.container,
            text="Shalbny - Quick Keyboard Layout Text Switcher",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#3B82F6"
        ).pack(pady=(0, 20))

        desc = (
            "سيقوم هذا المعالج بتثبيت برنامج شقلبني على جهاز الكمبيوتر الخاص بك.\n\n"
            "✨ يتيح لك التطبيق تصحيح وعكس لغة النصوص المكتوبة بالخطأ فوراً\n"
            "بمجرد تحديد النص وضغط زر الاختصار (عربي ⟷ إنجليزي).\n\n"
            "اضغط على 'التالي' للمتابعة وتحديد خيارات التثبيت."
        )
        ctk.CTkLabel(
            self.container,
            text=desc,
            justify="center",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray80"
        ).pack(pady=10)

        # Nav Buttons
        nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ctk.CTkButton(
            nav_frame,
            text="إلغاء",
            width=100,
            fg_color="gray30",
            hover_color="gray40",
            command=self.root.quit
        ).pack(side="left")

        ctk.CTkButton(
            nav_frame,
            text="التالي >",
            width=120,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=lambda: self._show_step(1)
        ).pack(side="right")

    # -------------------------------------------------------------
    # STEP 1: Destination Folder
    # -------------------------------------------------------------
    def _render_location(self) -> None:
        ctk.CTkLabel(
            self.container,
            text="📁 تحديد مجلد التثبيت",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(anchor="w", pady=(15, 5))

        ctk.CTkLabel(
            self.container,
            text="سيتم تثبيت ملفات البرنامج في المجلد الموضح أدناه:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray70"
        ).pack(anchor="w", pady=(0, 20))

        dir_box = ctk.CTkFrame(self.container)
        dir_box.pack(fill="x", pady=10)

        entry = ctk.CTkEntry(
            dir_box,
            textvariable=self.install_dir_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=36
        )
        entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        ctk.CTkButton(
            dir_box,
            text="استعراض...",
            width=90,
            height=36,
            command=self._browse_dir
        ).pack(side="right", padx=(5, 10), pady=10)

        ctk.CTkLabel(
            self.container,
            text="المساحة المطلوبة: حوالي 12 ميجابايت.\nالمساحة المتوفرة كافية.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="gray60"
        ).pack(anchor="w", pady=15)

        # Nav Buttons
        nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ctk.CTkButton(
            nav_frame,
            text="< السابق",
            width=100,
            fg_color="gray30",
            hover_color="gray40",
            command=lambda: self._show_step(0)
        ).pack(side="left")

        ctk.CTkButton(
            nav_frame,
            text="التالي >",
            width=120,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=lambda: self._show_step(2)
        ).pack(side="right")

    def _browse_dir(self) -> None:
        from tkinter import filedialog
        chosen = filedialog.askdirectory(initialdir=self.install_dir_var.get())
        if chosen:
            self.install_dir_var.set(chosen)

    # -------------------------------------------------------------
    # STEP 2: Tasks & Shortcuts Options
    # -------------------------------------------------------------
    def _render_options(self) -> None:
        ctk.CTkLabel(
            self.container,
            text="⚙️ تحديد المهام الإضافية",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(anchor="w", pady=(15, 5))

        ctk.CTkLabel(
            self.container,
            text="اختر الاختصارات وخيارات الإقلاع التي تود تفعيلها:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray70"
        ).pack(anchor="w", pady=(0, 20))

        opts_card = ctk.CTkFrame(self.container)
        opts_card.pack(fill="x", pady=10)

        ctk.CTkCheckBox(
            opts_card,
            text="إنشاء أيقونة واختصار على سطح المكتب (Desktop Shortcut)",
            variable=self.create_desktop_var,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(anchor="w", padx=20, pady=12)

        ctk.CTkCheckBox(
            opts_card,
            text="إضافة البرنامج إلى قائمة ابدأ (Start Menu)",
            variable=self.create_startmenu_var,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(anchor="w", padx=20, pady=12)

        ctk.CTkCheckBox(
            opts_card,
            text="تشغيل شقلبني تلقائياً عند بدء تشغيل الويندوز",
            variable=self.autostart_var,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(anchor="w", padx=20, pady=12)

        # Nav Buttons
        nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ctk.CTkButton(
            nav_frame,
            text="< السابق",
            width=100,
            fg_color="gray30",
            hover_color="gray40",
            command=lambda: self._show_step(1)
        ).pack(side="left")

        ctk.CTkButton(
            nav_frame,
            text="تثبيت الآن",
            width=120,
            fg_color="#10B981",
            hover_color="#059669",
            command=lambda: self._show_step(3)
        ).pack(side="right")

    # -------------------------------------------------------------
    # STEP 3: Installing Progress
    # -------------------------------------------------------------
    def _render_installing(self) -> None:
        ctk.CTkLabel(
            self.container,
            text="⏳ جاري تثبيت شقلبني...",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(anchor="w", pady=(25, 10))

        self.install_status = ctk.CTkLabel(
            self.container,
            text="جاري تحضير ملفات التثبيت...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray70"
        )
        self.install_status.pack(anchor="w", pady=(0, 15))

        self.prog_bar = ctk.CTkProgressBar(self.container, width=480, height=14)
        self.prog_bar.set(0.1)
        self.prog_bar.pack(pady=20)

        # Run install asynchronously after render
        self.root.after(200, self._perform_installation)

    def _perform_installation(self) -> None:
        target_path = Path(self.install_dir_var.get())

        try:
            # Terminate any running Shalbny process before overwriting
            try:
                subprocess.run(["taskkill", "/F", "/IM", "Shalbny.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.3)
            except Exception:
                pass

            target_path.mkdir(parents=True, exist_ok=True)
            self.prog_bar.set(0.3)
            self.install_status.configure(text="جاري نسخ ملفات التطبيق والمحرك...")
            self.root.update()

            # If pre-built standalone Shalbny.exe exists in dist, copy it directly
            exe_source = SOURCE_DIR / "dist" / "Shalbny.exe"
            standalone_installed = False

            if exe_source.exists():
                shutil.copy2(exe_source, target_path / "Shalbny.exe")
                target_exec = str(target_path / "Shalbny.exe")
                standalone_installed = True
            else:
                # Copy src, assets, main.py
                for folder in ["src", "assets"]:
                    src_f = SOURCE_DIR / folder
                    dest_f = target_path / folder
                    if src_f.exists():
                        if dest_f.exists():
                            shutil.rmtree(dest_f)
                        shutil.copytree(src_f, dest_f)

                shutil.copy2(SOURCE_DIR / "main.py", target_path / "main.py")
                if (SOURCE_DIR / "requirements.txt").exists():
                    shutil.copy2(SOURCE_DIR / "requirements.txt", target_path / "requirements.txt")

                runner_vbs = target_path / "Shalbny.vbs"
                with open(runner_vbs, "w", encoding="utf-8") as f:
                    main_py_path = str(target_path / "main.py").replace('"', '""')
                    f.write(f'CreateObject("Wscript.Shell").Run "pythonw ""{main_py_path}""", 0, False\n')
                target_exec = str(runner_vbs)

            # Ensure assets folder exists for icons
            dest_assets = target_path / "assets"
            if not dest_assets.exists() and (SOURCE_DIR / "assets").exists():
                shutil.copytree(SOURCE_DIR / "assets", dest_assets)

            self.prog_bar.set(0.6)
            self.install_status.configure(text="جاري إنشاء الاختصارات...")
            self.root.update()

            icon_file = target_path / "assets" / "icon.ico"

            # Desktop Shortcut (Resolves OneDrive & User Shell Folders)
            if self.create_desktop_var.get():
                desktop_folder = get_user_folder("Desktop", Path.home() / "Desktop")
                desktop_lnk = desktop_folder / "شقلبني - Shalbny.lnk"
                self._create_windows_shortcut(
                    lnk_path=desktop_lnk,
                    target_path=target_exec,
                    icon_path=str(icon_file),
                    desc="شقلبني - مبدل لغة الكتابة الذكي"
                )

            # Start Menu Shortcut
            if self.create_startmenu_var.get():
                programs_folder = get_user_folder("Programs", Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs")
                start_dir = programs_folder / "Shalbny"
                start_dir.mkdir(parents=True, exist_ok=True)
                start_lnk = start_dir / "شقلبني - Shalbny.lnk"
                self._create_windows_shortcut(
                    lnk_path=start_lnk,
                    target_path=target_exec,
                    icon_path=str(icon_file),
                    desc="شقلبني - مبدل لغة الكتابة الذكي"
                )

            # Windows Startup Registry (points directly to installed target_exec)
            if self.autostart_var.get():
                try:
                    import winreg
                    reg_run = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_run, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, "Shalbny", 0, winreg.REG_SZ, f'"{target_exec}"')
                except Exception:
                    pass
                try:
                    from src.config import ConfigManager
                    cfg = ConfigManager()
                    cfg.set("autostart", True)
                except Exception:
                    pass

            self.prog_bar.set(1.0)
            self.install_status.configure(text="اكتمل التثبيت بنجاح!")
            self.root.update()

            self.root.after(500, lambda: self._show_step(4))

        except Exception as e:
            self.install_status.configure(text=f"حدث خطأ أثناء التثبيت: {str(e)}", text_color="#EF4444")

    def _create_windows_shortcut(self, lnk_path: Path, target_path: str, icon_path: str, desc: str) -> None:
        """Creates a native Windows .lnk shortcut via PowerShell COM object."""
        try:
            ps_cmd = (
                f"$ws = New-Object -ComObject WScript.Shell; "
                f"$s = $ws.CreateShortcut('{str(lnk_path)}'); "
                f"$s.TargetPath = '{target_path}'; "
                f"$s.WorkingDirectory = '{str(Path(target_path).parent)}'; "
                f"$s.IconLocation = '{icon_path}'; "
                f"$s.Description = '{desc}'; "
                f"$s.Save()"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, creationflags=0x08000000)
        except Exception:
            pass

    # -------------------------------------------------------------
    # STEP 4: Finish Screen
    # -------------------------------------------------------------
    def _render_finish(self) -> None:
        try:
            if self.logo_path.exists():
                pil_logo = Image.open(self.logo_path)
            else:
                from src.ui.assets import create_app_icon
                pil_logo = create_app_icon(size=90)
            logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(90, 90))
            ctk.CTkLabel(self.container, image=logo_ctk, text="").pack(pady=(20, 10))
        except Exception:
            pass

        ctk.CTkLabel(
            self.container,
            text="🎉 تم تثبيت شقلبني بنجاح!",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#10B981"
        ).pack(pady=(5, 5))

        ctk.CTkLabel(
            self.container,
            text="أصبح البرنامج جاهزاً للعمل على جهازك.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="gray80"
        ).pack(pady=(0, 20))

        ctk.CTkCheckBox(
            self.container,
            text="تشغيل برنامج شقلبني الآن في الخلفية بجوار الساعة",
            variable=self.launch_now_var,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(pady=15)

        # Finish Button
        ctk.CTkButton(
            self.container,
            text="إنهاء وتطبيق",
            width=160,
            height=38,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._finish_and_exit
        ).pack(side="bottom", pady=(20, 0))

    def _finish_and_exit(self) -> None:
        if self.launch_now_var.get():
            target_path = Path(self.install_dir_var.get())
            exe_target = target_path / "Shalbny.exe"
            vbs_script = target_path / "Shalbny.vbs"
            if exe_target.exists():
                try:
                    subprocess.Popen([str(exe_target)])
                except Exception:
                    pass
            elif vbs_script.exists():
                try:
                    subprocess.Popen(["wscript.exe", str(vbs_script)])
                except Exception:
                    pass
        self.root.destroy()
        sys.exit(0)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
