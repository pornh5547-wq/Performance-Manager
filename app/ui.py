import customtkinter as ctk
import threading
from app.config import Config, log
from app.notifications import ToastManager
from app.pages.dashboard import DashboardPage
from app.pages.gaming_mode import GamingModePage
from app.pages.performance_mode import PerformanceModePage
from app.pages.health_check import HealthCheckPage
from app.pages.network_repair import NetworkRepairPage
from app.pages.logs_page import LogsPage
from app.pages.settings_page import SettingsPage
from app.pages.startup_manager import StartupManagerPage
from app.pages.system_info_page import SystemInfoPage
from app.pages.drives_page import DrivesPage
from app.pages.privacy_page import PrivacyPage
from app.pages.services_page import ServicesPage
from app.pages.bloatware_page import BloatwarePage
from app.pages.hosts_page import HostsPage
from app.pages.ram_optimizer_page import RamOptimizerPage
from app.pages.large_files_page import LargeFilesPage
from app.pages.battery_page import BatteryPage
from app.pages.features_page import FeaturesPage
from app.pages.visual_toggles_page import VisualTogglesPage
from app.pages.speed_test_page import SpeedTestPage
from app.utils.scheduler import MaintenanceScheduler
from app.utils.update_checker import UpdateChecker
from app.utils.scan_manager import ScanManager
from app.widgets.scan_overlay import ScanOverlay
from app.plugins.loader import PluginLoader

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

NAV_CATEGORIES = [
    ("\U0001f4ca", "Dashboard", [
        ("dashboard", "Dashboard"),
    ]),
    ("\u2139\ufe0f", "System Info", [
        ("sysinfo", "System Info"),
        ("battery", "Battery"),
        ("drives", "Drives"),
    ]),
    ("\u26a1", "Performance", [
        ("performance", "Performance"),
        ("ram", "RAM Optimizer"),
        ("privacy", "Privacy"),
        ("visual", "Visual Effects"),
        ("bloatware", "Bloatware"),
    ]),
    ("\U0001f3ae", "Gaming", [
        ("gaming", "Gaming Mode"),
    ]),
    ("\U0001f310", "Network", [
        ("network", "Network"),
        ("speedtest", "Speed Test"),
        ("hosts", "Hosts Editor"),
    ]),
    ("\U0001f527", "System Tools", [
        ("health", "Health Check"),
        ("services", "Services"),
        ("features", "Windows Features"),
        ("startup", "Startup Manager"),
        ("largefiles", "Large Files"),
    ]),
    ("\U0001f4cb", "Logs & Settings", [
        ("logs", "Logs"),
        ("settings", "Settings"),
    ]),
]

NAV_ITEMS = []
for _icon, _cat, items in NAV_CATEGORIES:
    for key, label in items:
        NAV_ITEMS.append((key, label))

NAV_BG = "#111827"
NAV_ACCENT = "#3b82f6"
NAV_HOVER = "#1e293b"
NAV_ACTIVE = "#1e3a5f"
CONTENT_BG = "#0f172a"

COLOR_THEMES = {
    "dark-blue": "dark-blue",
    "blue": "blue",
    "green": "green",
}

PAGE_CLASSES = {
    "dashboard": DashboardPage, "privacy": PrivacyPage, "gaming": GamingModePage,
    "performance": PerformanceModePage, "ram": RamOptimizerPage, "health": HealthCheckPage,
    "services": ServicesPage, "network": NetworkRepairPage, "speedtest": SpeedTestPage,
    "hosts": HostsPage, "drives": DrivesPage, "largefiles": LargeFilesPage,
    "startup": StartupManagerPage, "sysinfo": SystemInfoPage, "battery": BatteryPage,
    "features": FeaturesPage, "visual": VisualTogglesPage, "bloatware": BloatwarePage,
    "logs": LogsPage, "settings": SettingsPage,
}

class PerformanceManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.current_page = None
        self.nav_buttons = {}
        self.page_frames = {}
        self.scheduler = MaintenanceScheduler(self.config)
        self.plugin_loader = PluginLoader()
        self.toast = None
        self.scan_manager = ScanManager()
        self.config.scan_manager = self.scan_manager

        self._apply_theme()

        self.title("PM Performance Manager")
        self.geometry("1200x780")
        self.minsize(960, 640)

        self._show_startup_overlay()
        self._build_layout()
        self._bind_events()
        self._post_init()

    def _apply_theme(self):
        mode = self.config.get("appearance_mode", "Dark")
        ctk.set_appearance_mode(mode)
        theme = self.config.get("color_theme", "dark-blue")
        ctk.set_default_color_theme(COLOR_THEMES.get(theme, "dark-blue"))

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.nav_frame = ctk.CTkFrame(self, fg_color=NAV_BG, corner_radius=0, width=240)
        self.nav_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.nav_frame.grid_propagate(False)

        self.top_bar = ctk.CTkFrame(self, fg_color="#1a2332", corner_radius=0, height=48)
        self.top_bar.grid(row=0, column=1, sticky="nsew")
        self.top_bar.grid_propagate(False)

        self.content_frame = ctk.CTkFrame(self, fg_color=CONTENT_BG, corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._build_topbar()
        self._build_navbar()
        self._build_pages()

    def _build_topbar(self):
        self.page_title = ctk.CTkLabel(self.top_bar, text="Dashboard", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.page_title.pack(side="left", padx=20)

        right = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        right.pack(side="right", padx=15)

        self.update_indicator = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11))
        self.update_indicator.pack(side="left", padx=5)

        self.status_dot = ctk.CTkLabel(right, text="\u25cf", font=ctk.CTkFont(size=10), text_color="#4ade80")
        self.status_dot.pack(side="left", padx=2)
        self.status_text = ctk.CTkLabel(right, text="Starting...", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_text.pack(side="left", padx=2)

        self.scan_status = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=10), text_color="#475569")
        self.scan_status.pack(side="left", padx=5)

    def _build_navbar(self):
        logo_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent", height=60)
        logo_frame.pack(fill="x", pady=(0, 15))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="\u26a1 PM", font=ctk.CTkFont(size=24, weight="bold"), text_color=NAV_ACCENT).pack(pady=(12, 0))

        nav_container = ctk.CTkScrollableFrame(self.nav_frame, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=8)

        for icon, cat_name, items in NAV_CATEGORIES:
            cat_frame = ctk.CTkFrame(nav_container, fg_color="transparent")
            cat_frame.pack(fill="x", pady=2)

            item_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            item_frame.pack(fill="x")

            for page_key, label in items:
                btn = ctk.CTkButton(
                    item_frame, text=f"  {label}", anchor="w",
                    fg_color="transparent", hover_color=NAV_HOVER,
                    text_color="#94a3b8", font=ctk.CTkFont(size=13),
                    height=32, corner_radius=6,
                    command=lambda k=page_key: self._switch_page(k),
                )
                btn.pack(fill="x", pady=1)
                self.nav_buttons[page_key] = btn

        bottom = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0, 12))
        ctk.CTkLabel(bottom, text="v1.0.0", font=ctk.CTkFont(size=10), text_color="#475569").pack()

    def _build_pages(self):
        dashboard = DashboardPage(self.content_frame, self.config)
        dashboard.grid(row=0, column=0, sticky="nsew")
        self.page_frames["dashboard"] = dashboard
        self._page_titles = {k: v for k, v in NAV_ITEMS}

    def _lazy_load_page(self, page_key):
        if page_key in self.page_frames:
            return
        cls = PAGE_CLASSES.get(page_key)
        if not cls:
            return
        if page_key == "settings":
            frame = cls(self.content_frame, self.config, self.scheduler)
        else:
            frame = cls(self.content_frame, self.config)
        frame.grid(row=0, column=0, sticky="nsew")
        self.page_frames[page_key] = frame

    def _switch_page(self, page_key):
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color=NAV_ACTIVE, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8")

        if self.current_page:
            old = self.page_frames.get(self.current_page)
            if old and hasattr(old, 'stop_monitoring'):
                old.stop_monitoring()
            old.grid_remove()

        self._lazy_load_page(page_key)
        new_page = self.page_frames.get(page_key)
        if not new_page:
            return
        new_page.grid()
        if hasattr(new_page, 'start_monitoring'):
            new_page.start_monitoring()
        if hasattr(new_page, 'on_activate'):
            new_page.on_activate()

        self.current_page = page_key
        self.page_title.configure(text=self._page_titles.get(page_key, page_key.capitalize()))

    def _bind_events(self):
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _show_startup_overlay(self):
        self.overlay = ScanOverlay(self, on_complete=self._on_startup_done)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.scan_manager.start_scan(callback=self._on_scan_complete)
        self._poll_scan_progress()

    def _poll_scan_progress(self):
        if not self.overlay:
            return
        if self.overlay.winfo_exists():
            self.overlay.set_status(self.scan_manager.get_progress())
            self.after(200, self._poll_scan_progress)

    def _post_init(self):
        self.toast = ToastManager(self)
        self._switch_page("dashboard")
        self.update()

    def _on_scan_complete(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.finish()

    def _on_startup_done(self):
        self.overlay = None
        self.status_text.configure(text="Ready")
        self._update_scan_status()
        self._finish_init()
        self._schedule_periodic_scan()

    def _schedule_periodic_scan(self):
        self.after(300000, self._do_periodic_scan)

    def _do_periodic_scan(self):
        self.status_text.configure(text="Scanning...")
        log("Starting periodic 5-minute scan")
        self.scan_manager.start_scan(callback=self._on_periodic_done)
        self.after(300000, self._do_periodic_scan)

    def _on_periodic_done(self):
        self.status_text.configure(text="Ready")
        self._update_scan_status()
        log("Periodic scan complete")

    def _update_scan_status(self):
        ago = self.scan_manager.last_scan_ago()
        self.scan_status.configure(text=f"Scan: {ago}")

    def _finish_init(self):
        if self.config.get("scheduled_maintenance", False):
            self.scheduler.start()
        if self.config.get("plugins_enabled", True):
            loaded = self.plugin_loader.load_all()
            log(f"Loaded {len(loaded)} plugins")
        if self.config.get("check_updates", True):
            UpdateChecker().check(self._on_update_check)
        log("Application started")

    def _on_update_check(self, result):
        if result.get("has_update"):
            self.update_indicator.configure(text="Update available", text_color="#f59e0b")

    def show_toast(self, message, type="info", duration=3.0):
        if self.toast:
            self.toast.show(message, type, duration)

    def _on_close(self):
        log("Application shutting down")
        self.scheduler.stop()
        self.plugin_loader.unload_all()
        for frame in self.page_frames.values():
            if hasattr(frame, 'stop_monitoring'):
                frame.stop_monitoring()
        self.destroy()

    def run(self):
        self.mainloop()
