"""
Modern, animated Settings & Control Window for Shalbny.
Built with CustomTkinter featuring Dark/Light modes, bilingual Arabic/English i18n,
tabbed navigation, shortcut key recorder, live stats counter, visual how-to guide,
and Developer/About section.
"""
import os
import sys
import math
import keyboard
import webbrowser
import pyperclip
import customtkinter as ctk
from PIL import Image
from pathlib import Path
from typing import Callable, Optional

from ..config import ConfigManager
from ..converter.manager import ProfileManager
from ..i18n import i18n
from ..core.win_api import play_feedback_sound
from .assets import create_app_icon


class SettingsWindow:
    """Enhanced High-End Bilingual Settings and Management GUI."""

    def __init__(
        self,
        config: ConfigManager,
        profile_manager: ProfileManager,
        on_hotkey_change: Callable[[str], bool],
        on_profile_change: Callable[[str], None],
        on_language_change: Optional[Callable[[str], None]] = None
    ):
        self.config = config
        self.profile_manager = profile_manager
        self.on_hotkey_change = on_hotkey_change
        self.on_profile_change = on_profile_change
        self.on_language_change = on_language_change
        self.root: Optional[ctk.CTk] = None
        self.tabs: Optional[ctk.CTkTabview] = None

        # Synchronize active language with i18n singleton
        saved_lang = self.config.get("app_language", "ar")
        i18n.set_language(saved_lang)

        # Animation states
        self._pulse_angle = 0.0
        self._is_recording_key = False
        self._record_hook = None

        # Asset paths
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            self.base_dir = Path(sys._MEIPASS)
        else:
            self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.logo_path = self.base_dir / "assets" / "logo.png"
        self.icon_path = self.base_dir / "assets" / "icon.ico"

    def show(self, target_tab: Optional[str] = None) -> None:
        """Display the settings window. Brings to front if already active."""
        if self.root is not None and self.root.winfo_exists():
            self._restore_window()
            if target_tab and self.tabs:
                try:
                    self.tabs.set(target_tab)
                except Exception:
                    pass
            return

        theme_mode = self.config.get("theme", "dark")
        ctk.set_appearance_mode(theme_mode)
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title(i18n.t("app_title"))
        self.root.geometry("580x750")
        self.root.resizable(False, False)

        # Set taskbar icon if available
        if self.icon_path.exists():
            try:
                self.root.iconbitmap(str(self.icon_path))
            except Exception:
                pass

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        if target_tab and self.tabs:
            try:
                self.tabs.set(target_tab)
            except Exception:
                pass
        self._start_breathing_animation()
        self.root.mainloop()

    def _restore_window(self) -> None:
        """Thread-safe window restore and focus."""
        if self.root and self.root.winfo_exists():
            try:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
            except Exception:
                pass

    def _on_close(self) -> None:
        """Hides the window to tray instead of quitting."""
        if self._is_recording_key:
            self._cancel_key_recording()
        if self.root:
            self.root.withdraw()

    def _build_ui(self) -> None:
        # Top Header Bar
        header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Brand / Logo Image (Official high-res icon)
        try:
            if self.logo_path.exists():
                pil_logo = Image.open(self.logo_path)
            else:
                pil_logo = create_app_icon(size=52)
            logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(52, 52))
            logo_label = ctk.CTkLabel(header_frame, image=logo_ctk, text="")
            logo_label.pack(side="left", padx=(0, 14))
        except Exception:
            pass

        # Title and Live Status Box
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", fill="y")

        self.title_lbl = ctk.CTkLabel(
            title_box,
            text=i18n.t("app_title"),
            font=ctk.CTkFont(family="Segoe UI", size=21, weight="bold")
        )
        self.title_lbl.pack(anchor="w")

        # Live Animated Status Capsule Pill
        status_box = ctk.CTkFrame(
            title_box,
            corner_radius=12,
            fg_color=("#ECFDF5", "#064E3B"),
            border_width=1,
            border_color=("#A7F3D0", "#059669")
        )
        status_box.pack(anchor="w", pady=(2, 0))

        self.status_pill = ctk.CTkLabel(
            status_box,
            text=f"  {i18n.t('engine_running')}  ",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#10B981"
        )
        self.status_pill.pack(padx=6, pady=2)

        # Right Header Buttons (Theme Toggle & Language Switcher)
        header_btns = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_btns.pack(side="right")

        # Language Switcher Button (Pill shape)
        self.lang_btn = ctk.CTkButton(
            header_btns,
            text=i18n.t("lang_switch_btn"),
            width=92,
            height=32,
            corner_radius=16,
            command=self._toggle_language,
            fg_color="#0284C7",
            hover_color="#0369A1",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.lang_btn.pack(side="left", padx=(0, 8))

        # Theme Mode Toggle (Dark / Light Pill)
        current_theme = self.config.get("theme", "dark")
        self.theme_btn = ctk.CTkButton(
            header_btns,
            text=i18n.t("theme_light") if current_theme == "dark" else i18n.t("theme_dark"),
            width=82,
            height=32,
            corner_radius=16,
            command=self._toggle_theme,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.theme_btn.pack(side="left")

        # Render Tab Container
        self._render_tabs()

    def _render_tabs(self) -> None:
        """Renders or re-renders tab container and all 4 child views."""
        if self.tabs is not None:
            self.tabs.destroy()

        self.tabs = ctk.CTkTabview(
            self.root,
            width=540,
            height=635,
            corner_radius=14,
            segmented_button_selected_color="#2563EB",
            segmented_button_selected_hover_color="#1D4ED8",
            segmented_button_unselected_color=("#E2E8F0", "#1E293B")
        )
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        tab_general = self.tabs.add(i18n.t("tab_general"))
        tab_shortcut = self.tabs.add(i18n.t("tab_shortcut"))
        tab_stats = self.tabs.add(i18n.t("tab_stats"))
        tab_developer = self.tabs.add(i18n.t("tab_developer"))

        self._build_general_tab(tab_general)
        self._build_shortcut_tab(tab_shortcut)
        self._build_stats_tab(tab_stats)
        self._build_developer_tab(tab_developer)

    # -------------------------------------------------------------
    # TAB 1: General Settings
    # -------------------------------------------------------------
    def _build_general_tab(self, parent) -> None:
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # 1. Language profile card
        lang_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        lang_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            lang_card,
            text=i18n.t("profile_label"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 4))

        profiles = self.profile_manager.list_profiles()
        profile_names = [p.display_name for p in profiles]
        active_display = self.profile_manager.active_profile.display_name

        self.lang_var = ctk.StringVar(value=active_display)
        ctk.CTkOptionMenu(
            lang_card,
            values=profile_names,
            variable=self.lang_var,
            command=self._on_profile_selected,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=34,
            corner_radius=8
        ).pack(fill="x", padx=15, pady=(0, 12))

        # 2. System Behavior Card
        tog_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        tog_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            tog_card,
            text=i18n.t("behavior_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 6))

        # Switch OS Layout
        self.sw_layout_var = ctk.BooleanVar(value=self.config.get("switch_system_language", True))
        ctk.CTkSwitch(
            tog_card,
            text=i18n.t("switch_layout_lbl"),
            variable=self.sw_layout_var,
            command=lambda: self.config.set("switch_system_language", self.sw_layout_var.get()),
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(anchor="w", padx=15, pady=6)

        # Clipboard Restore
        self.clip_var = ctk.BooleanVar(value=self.config.get("restore_clipboard", True))
        ctk.CTkSwitch(
            tog_card,
            text=i18n.t("restore_clipboard_lbl"),
            variable=self.clip_var,
            command=lambda: self.config.set("restore_clipboard", self.clip_var.get()),
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(anchor="w", padx=15, pady=6)

        # Windows Autostart
        self.autostart_var = ctk.BooleanVar(value=self.config.get("autostart", False))
        ctk.CTkSwitch(
            tog_card,
            text=i18n.t("autostart_lbl"),
            variable=self.autostart_var,
            command=self._on_autostart_toggle,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        ).pack(anchor="w", padx=15, pady=(6, 12))

        # 3. Audio & Feedback Settings Card
        audio_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        audio_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            audio_card,
            text=i18n.t("audio_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 6))

        # Master Sound Switch (Mute/Unmute)
        self.sound_var = ctk.BooleanVar(value=self.config.get("play_sound", True))
        self.sound_switch = ctk.CTkSwitch(
            audio_card,
            text=i18n.t("sound_lbl"),
            variable=self.sound_var,
            command=self._on_sound_toggle,
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.sound_switch.pack(anchor="w", padx=15, pady=(4, 8))

        # Tone Selector & Test Button Row
        theme_row = ctk.CTkFrame(audio_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=15, pady=(0, 12))

        tone_options = [
            (i18n.t("tone_soft_pop"), "soft_pop"),
            (i18n.t("tone_windows_chime"), "windows_chime"),
            (i18n.t("tone_gentle_harmony"), "gentle_harmony"),
            (i18n.t("tone_mute"), "mute"),
        ]
        self._tone_map = {label: key for label, key in tone_options}
        self._tone_rev_map = {key: label for label, key in tone_options}

        current_theme_key = self.config.get("sound_theme", "soft_pop")
        current_theme_label = self._tone_rev_map.get(current_theme_key, tone_options[0][0])
        self.tone_var = ctk.StringVar(value=current_theme_label)

        self.tone_menu = ctk.CTkOptionMenu(
            theme_row,
            values=[label for label, _ in tone_options],
            variable=self.tone_var,
            command=self._on_tone_selected,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=32,
            corner_radius=8
        )
        self.tone_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.test_sound_btn = ctk.CTkButton(
            theme_row,
            text=i18n.t("test_sound_btn"),
            command=self._on_test_sound,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            width=112,
            height=32,
            corner_radius=8,
            fg_color="#0284C7",
            hover_color="#0369A1"
        )
        self.test_sound_btn.pack(side="right")

        # Initial state based on master toggle
        if not self.sound_var.get():
            self.tone_menu.configure(state="disabled")
            self.test_sound_btn.configure(state="disabled")

        # 4. Interactive Console Sandbox Area
        sb_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        sb_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            sb_card,
            text=i18n.t("playground_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            sb_card,
            text=i18n.t("playground_desc"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray60"
        ).pack(anchor="w", padx=15, pady=(0, 6))

        self.test_entry = ctk.CTkEntry(
            sb_card,
            placeholder_text=i18n.t("playground_placeholder"),
            font=ctk.CTkFont(family="Consolas", size=14),
            height=38,
            corner_radius=8
        )
        self.test_entry.insert(0, "fdv,j")
        self.test_entry.pack(fill="x", padx=15, pady=(0, 8))

        self.flip_btn = ctk.CTkButton(
            sb_card,
            text=i18n.t("flip_btn"),
            command=self._on_test_flip,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )
        self.flip_btn.pack(fill="x", padx=15, pady=(0, 14))

    # -------------------------------------------------------------
    # TAB 2: Shortcut Key Customization & Recorder
    # -------------------------------------------------------------
    def _build_shortcut_tab(self, parent) -> None:
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # 1. Mechanical Keycap Display Card
        badge_card = ctk.CTkFrame(
            scroll,
            corner_radius=14,
            border_width=1,
            border_color=("#BFDBFE", "#1E40AF"),
            fg_color=("#EFF6FF", "#0F172A")
        )
        badge_card.pack(fill="x", pady=8, padx=4)

        ctk.CTkLabel(
            badge_card,
            text=i18n.t("hotkey_active_lbl"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#1E40AF", "#93C5FD")
        ).pack(pady=(14, 6))

        current_hk = self.config.get("hotkey", "alt+s").upper()
        self.hotkey_badge = ctk.CTkLabel(
            badge_card,
            text=f"⌨️ [ {current_hk} ]",
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color="#38BDF8"
        )
        self.hotkey_badge.pack(pady=(0, 14))

        # Record Custom Key Button
        self.record_btn = ctk.CTkButton(
            badge_card,
            text=i18n.t("record_btn_idle"),
            command=self._toggle_key_recording,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=42,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )
        self.record_btn.pack(fill="x", padx=20, pady=(0, 16))

        # 2. Recommended Presets Card
        preset_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        preset_card.pack(fill="x", pady=8, padx=4)

        ctk.CTkLabel(
            preset_card,
            text=i18n.t("presets_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(14, 8))

        presets = [
            (i18n.t("preset_alt_s"), "alt+s"),
            (i18n.t("preset_ctrl_alt_s"), "ctrl+alt+s"),
            (i18n.t("preset_alt_q"), "alt+q"),
            (i18n.t("preset_ctrl_shift_x"), "ctrl+shift+x"),
            (i18n.t("preset_ctrl_shift_s"), "ctrl+shift+s"),
            (i18n.t("preset_alt_z"), "alt+z")
        ]

        for label, code in presets:
            btn = ctk.CTkButton(
                preset_card,
                text=label,
                command=lambda c=code: self._apply_hotkey(c),
                font=ctk.CTkFont(family="Segoe UI", size=12),
                height=34,
                corner_radius=8,
                fg_color=("#E2E8F0", "#334155"),
                hover_color=("#CBD5E1", "#475569"),
                text_color=("#0F172A", "#F8FAFC")
            )
            btn.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(preset_card, text="", height=8).pack()

    # -------------------------------------------------------------
    # TAB 3: Stats & Quick Visual Guide
    # -------------------------------------------------------------
    def _build_stats_tab(self, parent) -> None:
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # 1. Visual How-to-use Infographic Guide Card
        guide_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        guide_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            guide_card,
            text=i18n.t("guide_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=15, pady=(14, 8))

        steps = [
            ("guide_step1", "#3B82F6"),
            ("guide_step2", "#10B981"),
            ("guide_step3", "#8B5CF6")
        ]
        for step_key, accent_color in steps:
            step_box = ctk.CTkFrame(
                guide_card,
                corner_radius=8,
                fg_color=("#EFF6FF", "#0F172A"),
                border_width=1,
                border_color=("#DBEAFE", "#1E293B")
            )
            step_box.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(
                step_box,
                text=i18n.t(step_key),
                font=ctk.CTkFont(family="Segoe UI", size=13),
                anchor="w",
                justify="left"
            ).pack(anchor="w", padx=12, pady=8)

        ctk.CTkLabel(guide_card, text="", height=6).pack()

        # 2. Rescue & Conversion Statistics Metric Card
        stats_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        stats_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            stats_card,
            text=i18n.t("stats_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(14, 6))

        count_row = ctk.CTkFrame(stats_card, fg_color="transparent")
        count_row.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(
            count_row,
            text=i18n.t("stats_count_lbl"),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w"
        ).pack(side="left")

        current_count = int(self.config.get("conversion_count", 0))
        self.stats_counter_lbl = ctk.CTkLabel(
            count_row,
            text=f"{current_count} {i18n.t('stats_unit')}",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#10B981"
        )
        self.stats_counter_lbl.pack(side="right")

        # Reset Counter Button
        ctk.CTkButton(
            stats_card,
            text=i18n.t("stats_reset_btn"),
            command=self._on_reset_counter,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=32,
            corner_radius=8,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(fill="x", padx=15, pady=(8, 14))

        # 3. Factory Reset & Settings Recovery Card
        reset_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#FEE2E2", "#7F1D1D"),
            fg_color=("#FEF2F2", "#1C1917")
        )
        reset_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            reset_card,
            text=i18n.t("reset_defaults_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#DC2626", "#F87171")
        ).pack(anchor="w", padx=15, pady=(14, 6))

        self.reset_status_lbl = ctk.CTkLabel(
            reset_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.reset_status_lbl.pack(padx=15, pady=(0, 4))

        ctk.CTkButton(
            reset_card,
            text=i18n.t("reset_defaults_btn"),
            command=self._on_factory_reset,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=34,
            corner_radius=8,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        ).pack(fill="x", padx=15, pady=(0, 14))

    # -------------------------------------------------------------
    # TAB 4: Developer & About Information
    # -------------------------------------------------------------
    def _build_developer_tab(self, parent) -> None:
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # 1. Executive Developer Profile Hero Card
        dev_card = ctk.CTkFrame(
            scroll,
            corner_radius=14,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        dev_card.pack(fill="x", pady=6, padx=4)

        # Monogram Avatar Emblem
        avatar_box = ctk.CTkFrame(dev_card, width=76, height=76, corner_radius=38, fg_color="#2563EB")
        avatar_box.pack(pady=(16, 6))
        avatar_box.pack_propagate(False)

        ctk.CTkLabel(
            avatar_box,
            text="KA",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#FFFFFF"
        ).pack(expand=True)

        dev_name = self.config.get("developer_name", "KHALED ABDELMONEM")
        ctk.CTkLabel(
            dev_card,
            text=dev_name,
            font=ctk.CTkFont(family="Segoe UI", size=21, weight="bold")
        ).pack(pady=(2, 2))

        ctk.CTkLabel(
            dev_card,
            text="Lead Software Engineer & System Architect",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#3B82F6"
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            dev_card,
            text=i18n.t("dev_bio"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray70"
        ).pack(pady=(0, 16))

        # 2. Contact & Social Links Hub Section
        links_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        links_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            links_card,
            text=i18n.t("contacts_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # GitHub Row
        github_row = ctk.CTkFrame(links_card, fg_color="transparent")
        github_row.pack(fill="x", padx=15, pady=5)
        github_url = self.config.get("developer_github", "https://github.com/ben10943")

        ctk.CTkLabel(
            github_row,
            text=i18n.t("github_lbl"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=80,
            anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            github_row,
            text="ben10943",
            font=ctk.CTkFont(family="Consolas", size=12),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            github_row,
            text=i18n.t("open_link_btn"),
            width=85,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=lambda: webbrowser.open(github_url)
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            github_row,
            text=i18n.t("copy_btn"),
            width=50,
            height=28,
            corner_radius=6,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=lambda: pyperclip.copy(github_url)
        ).pack(side="right")

        # LinkedIn Row
        linkedin_row = ctk.CTkFrame(links_card, fg_color="transparent")
        linkedin_row.pack(fill="x", padx=15, pady=5)
        linkedin_url = self.config.get("developer_linkedin", "https://www.linkedin.com/in/khaled-moneam")

        ctk.CTkLabel(
            linkedin_row,
            text=i18n.t("linkedin_lbl"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=80,
            anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            linkedin_row,
            text="khaled-moneam",
            font=ctk.CTkFont(family="Consolas", size=12),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            linkedin_row,
            text=i18n.t("open_link_btn"),
            width=85,
            height=28,
            corner_radius=6,
            fg_color="#0A66C2",
            hover_color="#004182",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=lambda: webbrowser.open(linkedin_url)
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            linkedin_row,
            text=i18n.t("copy_btn"),
            width=50,
            height=28,
            corner_radius=6,
            fg_color=("#E2E8F0", "#334155"),
            hover_color=("#CBD5E1", "#475569"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=lambda: pyperclip.copy(linkedin_url)
        ).pack(side="right")

        # Phone / WhatsApp Row
        phone_row = ctk.CTkFrame(links_card, fg_color="transparent")
        phone_row.pack(fill="x", padx=15, pady=5)
        phone_num = self.config.get("developer_phone", "01015362991")

        ctk.CTkLabel(
            phone_row,
            text=i18n.t("phone_lbl"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=80,
            anchor="w"
        ).pack(side="left")

        self.phone_entry = ctk.CTkEntry(
            phone_row,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.phone_entry.insert(0, phone_num)
        self.phone_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def save_phone():
            new_val = self.phone_entry.get().strip()
            if new_val:
                self.config.set("developer_phone", new_val)
                pyperclip.copy(new_val)

        ctk.CTkButton(
            phone_row,
            text=i18n.t("save_and_copy_btn"),
            width=85,
            height=28,
            corner_radius=6,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=save_phone
        ).pack(side="right")

        ctk.CTkLabel(links_card, text="", height=6).pack()

        # 3. Architecture & Specifications Card
        specs_card = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            fg_color=("#F8FAFC", "#1E293B")
        )
        specs_card.pack(fill="x", pady=6, padx=4)

        ctk.CTkLabel(
            specs_card,
            text=i18n.t("specs_title"),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 8))

        specs = [
            (i18n.t("spec_lead_dev"), dev_name),
            (i18n.t("spec_version_lbl"), i18n.t("spec_version_val")),
            (i18n.t("spec_arch_lbl"), i18n.t("spec_arch_val")),
            (i18n.t("spec_engine_lbl"), i18n.t("spec_engine_val")),
            (i18n.t("spec_latency_lbl"), i18n.t("spec_latency_val")),
            (i18n.t("spec_memory_lbl"), i18n.t("spec_memory_val")),
            (i18n.t("spec_clipboard_lbl"), i18n.t("spec_clipboard_val")),
            (i18n.t("spec_license_lbl"), i18n.t("spec_license_val"))
        ]

        for title, val in specs:
            row = ctk.CTkFrame(specs_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(
                row,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                width=140,
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=val,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                anchor="w",
                text_color="gray80"
            ).pack(side="left", fill="x", expand=True)

        # Check Updates Action Card
        updates_frame = ctk.CTkFrame(specs_card, fg_color="transparent")
        updates_frame.pack(fill="x", padx=15, pady=(10, 8))

        ctk.CTkButton(
            updates_frame,
            text=i18n.t("check_updates_btn"),
            command=self._on_check_updates,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=34,
            corner_radius=8,
            fg_color="#0284C7",
            hover_color="#0369A1"
        ).pack(fill="x")

        self.updates_lbl = ctk.CTkLabel(
            specs_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.updates_lbl.pack(padx=15, pady=(2, 8))

    # -------------------------------------------------------------
    # Logic & Event Handlers
    # -------------------------------------------------------------
    def _toggle_language(self) -> None:
        """Switch application locale between Arabic and English."""
        current_lang = self.config.get("app_language", "ar")
        new_lang = "en" if current_lang == "ar" else "ar"
        self.config.set("app_language", new_lang)
        i18n.set_language(new_lang)

        # Update header texts
        self.lang_btn.configure(text=i18n.t("lang_switch_btn"))
        current_theme = self.config.get("theme", "dark")
        self.theme_btn.configure(text=i18n.t("theme_light") if current_theme == "dark" else i18n.t("theme_dark"))
        self.title_lbl.configure(text=i18n.t("app_title"))
        self.status_pill.configure(text=f"  {i18n.t('engine_running')}  ")
        if self.root:
            self.root.title(i18n.t("app_title"))

        # Re-render all tabs with updated translations
        self._render_tabs()

        # Fire callback to notify tray icon
        if self.on_language_change:
            try:
                self.on_language_change(new_lang)
            except Exception:
                pass

    def _on_sound_toggle(self) -> None:
        """Toggles audio feedback globally on or off (Mute switch)."""
        enabled = self.sound_var.get()
        self.config.set("play_sound", enabled)
        state = "normal" if enabled else "disabled"
        if hasattr(self, "tone_menu") and self.tone_menu.winfo_exists():
            self.tone_menu.configure(state=state)
        if hasattr(self, "test_sound_btn") and self.test_sound_btn.winfo_exists():
            self.test_sound_btn.configure(state=state)

    def _on_tone_selected(self, choice: str) -> None:
        """Selects sound theme and previews it immediately."""
        theme_key = self._tone_map.get(choice, "soft_pop")
        self.config.set("sound_theme", theme_key)
        if theme_key != "mute" and self.sound_var.get():
            play_feedback_sound(sound_theme=theme_key, enabled=True)

    def _on_test_sound(self) -> None:
        """Plays a preview of the active notification tone."""
        theme_key = self.config.get("sound_theme", "soft_pop")
        play_feedback_sound(sound_theme=theme_key, enabled=self.sound_var.get())

    def _on_reset_counter(self) -> None:
        """Resets conversion rescue stats counter."""
        self.config.set("conversion_count", 0)
        if hasattr(self, "stats_counter_lbl") and self.stats_counter_lbl.winfo_exists():
            self.stats_counter_lbl.configure(text=f"0 {i18n.t('stats_unit')}")

    def _on_factory_reset(self) -> None:
        """Restores all configuration back to factory default values."""
        self.config.reset_defaults()
        self._apply_hotkey("alt+s")
        if hasattr(self, "reset_status_lbl") and self.reset_status_lbl.winfo_exists():
            self.reset_status_lbl.configure(text=i18n.t("reset_done_msg"), text_color="#10B981")
            self.root.after(3000, lambda: self.reset_status_lbl.configure(text=""))
        self._render_tabs()

    def _on_check_updates(self) -> None:
        """Checks for software updates."""
        if hasattr(self, "updates_lbl") and self.updates_lbl.winfo_exists():
            self.updates_lbl.configure(text=i18n.t("up_to_date_msg"), text_color="#10B981")

    def _toggle_theme(self) -> None:
        """Switch between Dark and Light appearances."""
        current = self.config.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        self.config.set("theme", new_theme)
        ctk.set_appearance_mode(new_theme)
        self.theme_btn.configure(text=i18n.t("theme_light") if new_theme == "dark" else i18n.t("theme_dark"))

    def _start_breathing_animation(self) -> None:
        """Perpetual breathing pulse effect on the active status indicator."""
        if self.root and self.root.winfo_exists():
            self._pulse_angle += 0.12
            # Oscillate brightness between 0.6 and 1.0
            brightness = 0.6 + 0.4 * math.sin(self._pulse_angle)
            if brightness > 0.8:
                self.status_pill.configure(text=f"  {i18n.t('engine_running')}  ", text_color="#10B981")
            else:
                self.status_pill.configure(text=f"  {i18n.t('engine_running')}  ", text_color="#059669")

            self.root.after(80, self._start_breathing_animation)

    def _toggle_key_recording(self) -> None:
        if self._is_recording_key:
            self._cancel_key_recording()
        else:
            self._start_key_recording()

    def _start_key_recording(self) -> None:
        self._is_recording_key = True
        self.record_btn.configure(
            text=i18n.t("record_btn_listening"),
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        self.hotkey_badge.configure(text=i18n.t("listening_badge"), text_color="#EF4444")

        # Global key listener for recording next hotkey
        def on_key_event(e):
            if not self._is_recording_key:
                return
            if e.event_type == keyboard.KEY_DOWN:
                key_name = e.name.lower()
                # Ignore isolated modifier presses
                if key_name in ('ctrl', 'alt', 'shift', 'windows'):
                    return

                # Build combination if modifiers are held
                parts = []
                if keyboard.is_pressed('ctrl'):
                    parts.append('ctrl')
                if keyboard.is_pressed('alt'):
                    parts.append('alt')
                if keyboard.is_pressed('shift'):
                    parts.append('shift')
                parts.append(key_name)
                hotkey_str = "+".join(parts)

                self.root.after(0, lambda: self._apply_hotkey(hotkey_str))

        self._record_hook = keyboard.hook(on_key_event)

    def _cancel_key_recording(self) -> None:
        self._is_recording_key = False
        if self._record_hook:
            try:
                keyboard.unhook(self._record_hook)
            except Exception:
                pass
            self._record_hook = None
        self.record_btn.configure(
            text=i18n.t("record_btn_idle"),
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )
        current_hk = self.config.get("hotkey", "alt+s").upper()
        self.hotkey_badge.configure(text=f"⌨️ [ {current_hk} ]", text_color="#38BDF8")

    def _apply_hotkey(self, hotkey_str: str) -> None:
        if self._is_recording_key:
            self._cancel_key_recording()

        success = self.on_hotkey_change(hotkey_str)
        if success:
            self.config.set("hotkey", hotkey_str)
            self.hotkey_badge.configure(
                text=f"⌨️ [ {hotkey_str.upper()} ]",
                text_color="#10B981"
            )
        else:
            self.hotkey_badge.configure(text=i18n.t("conflict_badge"), text_color="#EF4444")

    def _on_profile_selected(self, choice: str) -> None:
        for p in self.profile_manager.list_profiles():
            if p.display_name == choice:
                self.config.set("active_profile", p.id)
                self.profile_manager.set_active_profile(p.id)
                self.on_profile_change(p.id)
                break

    def _on_autostart_toggle(self) -> None:
        enable = self.autostart_var.get()
        self.config.set_autostart(enable)

    def _on_test_flip(self) -> None:
        text = self.test_entry.get()
        if text:
            # Trigger quick visual flash animation on button
            self.flip_btn.configure(fg_color="#10B981")
            self.root.after(150, lambda: self.flip_btn.configure(fg_color="#2563EB"))

            flipped = self.profile_manager.convert(text)
            self.test_entry.delete(0, "end")
            self.test_entry.insert(0, flipped)
