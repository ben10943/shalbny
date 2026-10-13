# Design System: Shalbny Desktop App (شقلبني)

## 1. Visual Theme & Atmosphere
A refined, ultra-fast desktop utility application adhering to modern Windows 11 Fluent and luxury developer-tool ergonomics.
- **Density:** Daily App Balanced (6/10) with clear functional partitioning.
- **Variance:** Offset Asymmetric (6/10) with focused utility navigation.
- **Motion:** Perpetual Micro-Interactions (6/10) featuring a breathing status indicator, tactile push physics, and fluid theme transitions.
- **Mood:** Minimalist, calm, trustworthy, and razor-sharp. Designed for zero cognitive load while running in the background.

## 2. Color Palette & Roles (Dual Theme Architecture)

### Dark Mode (Default Mode)
- **Deep Slate Base** (`#0F172A`) — Primary window canvas (Slate 900)
- **Card Surface** (`#1E293B`) — Elevated panels, containers, and card layers (Slate 800)
- **Subtle Border** (`#334155`) — Clean 1px structural dividing borders (Slate 700)
- **Primary Text** (`#F8FAFC`) — High-contrast titanium white (Slate 50)
- **Secondary Text** (`#94A3B8`) — Descriptive labels, shortcuts, and helper notes (Slate 400)
- **Sapphire Accent** (`#3B82F6`) — Primary brand action, switches, active states (Blue 500)
- **Emerald Pulse** (`#10B981`) — Active live engine status indicator

### Light Mode
- **Clean Canvas** (`#F8FAFC`) — Primary window background (Slate 50)
- **Card Surface** (`#FFFFFF`) — Elevated panels with subtle drop shadow
- **Subtle Border** (`#E2E8F0`) — Clean 1px soft border (Slate 200)
- **Primary Text** (`#0F172A`) — Deep ink charcoal text (Slate 900)
- **Secondary Text** (`#64748B`) — Muted descriptive text (Slate 500)
- **Sapphire Accent** (`#2563EB`) — Vibrant interactive accent (Blue 600)
- **Emerald Pulse** (`#059669`) — Active status indicator

## 3. Typography Rules
- **Display & Headings:** `Segoe UI Variable Display`, `Outfit`, or `Geist` — Track-tight, bold, authoritative yet friendly.
- **Body & Labels:** `Segoe UI Variable Text` / system standard — Relaxed leading, maximum 65 characters per line, clean Arabic Naskh rendering for Arabic copy.
- **Monospace:** `Consolas` or `JetBrains Mono` — For keyboard shortcuts (`Pause`, `Ctrl+Shift+X`), technical keys, and version identifiers.
- **Banned:** Generic serif fonts in utility UI, distorted letter spacing, unreadable low-contrast light grays.

## 4. Component Stylings
- **Header & Branding:** Premium logo emblem alongside bold title and live pulsating status pill.
- **Tab Navigation (Segmented Control):** Modern pill-style tab bar with 3 tabs:
  1. `⚙️ الإعدادات العامة (General)`
  2. `⌨️ مفتاح الاختصار (Shortcut)`
  3. `👨‍💻 المطور والمعلومات (Developer & About)`
- **Shortcut Key Recorder:** An interactive tactile badge displaying the current shortcut. Clicking it enters "Listening mode" where pressing any key or combination instantly binds it.
- **Switches & Toggles:** Rounded fluent toggles with instant state feedback.
- **Interactive Sandbox:** A dedicated test area allowing users to type, select, and test text inversion in real-time.
- **Theme Switcher:** Seamless Dark / Light toggle button in the header.

## 5. Layout Principles
- Responsive single-window utility format (520px × 640px).
- Generous internal padding (16px - 20px) with clear card separation.
- Visual hierarchy driven by elevation and contrast, not clutter.

## 6. Motion & Micro-Interactions
- **Breathing Status Pulse:** The live engine pill subtly pulses (`alpha: 0.5 -> 1.0 -> 0.5`) on an infinite gentle loop.
- **Tactile Button Press:** Subtle active depression feedback (-1px) on clicks.
- **Flip Transition:** When text is flipped in the playground, a brief highlight pulse signals successful inversion.

## 7. Anti-Patterns (Banned)
- No generic AI purple neon glows or blinding gradients.
- No cluttered multi-level nested cards.
- No unhandled thread blocking or freezing UI.
- No invasive popups or annoying notifications.
