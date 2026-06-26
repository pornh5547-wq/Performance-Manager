import customtkinter as ctk
import threading
import time
from app.monitors.system_monitor import SystemMonitor
from app.utils.admin import get_windows_health
from app.utils.repair import WindowsRepair
from app.utils.ssd_optimizer import SSDOptimizer

class HealthCheckPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.monitor = SystemMonitor()
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="🩺 System Health Check", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Diagnose and repair system issues", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        health_card = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        health_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(health_card, text="System Status", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        self.checks = {}
        for name in ["DISM Image Health", "SFC File Integrity", "Disk SMART Status", "SSD TRIM Status", "System Uptime"]:
            row = ctk.CTkFrame(health_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=12), width=160, anchor="w").pack(side="left")
            val = ctk.CTkLabel(row, text="...", font=ctk.CTkFont(size=12), text_color="#64748b", anchor="w")
            val.pack(side="left", padx=10)
            self.checks[name] = val

        btn_row = ctk.CTkFrame(health_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(10, 10))
        self.check_btn = ctk.CTkButton(btn_row, text="🔄 Run Full Health Check", command=self.run_check,
                                        fg_color="#2563eb", hover_color="#1d4ed8", height=34)
        self.check_btn.pack(side="left")

        tools_card = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        tools_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tools_card, text="Repair Tools", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        for name, desc, color, action in [
            ("DISM ScanHealth", "Scan for image corruption", "#7c3aed", lambda: self._run_repair("DISM ScanHealth", WindowsRepair.run_dism_scan)),
            ("DISM Restore", "Repair system image", "#7c3aed", lambda: self._run_repair("DISM RestoreHealth", WindowsRepair.run_dism_restore)),
            ("SFC /scannow", "Scan system files", "#0891b2", lambda: self._run_repair("SFC", WindowsRepair.run_sfc_scan)),
            ("CHKDSK C:", "Check disk errors", "#db2777", lambda: self._run_repair("CHKDSK", WindowsRepair.run_chkdsk)),
        ]:
            row = ctk.CTkFrame(tools_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=13), width=130, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(size=11), text_color="#94a3b8", anchor="w").pack(side="left", padx=5, fill="x", expand=True)
            btn = ctk.CTkButton(row, text="Run", width=60, height=26,
                                command=lambda a=action, n=name: a(),
                                fg_color=color, hover_color=self._darken(color))
            btn.pack(side="right", padx=5)

        self.status_box = ctk.CTkTextbox(main, height=100, wrap="word", state="disabled", font=ctk.CTkFont(size=11))
        self.status_box.pack(fill="x")

    def _darken(self, c):
        r = max(int(c[1:3], 16) - 25, 0)
        g = max(int(c[3:5], 16) - 25, 0)
        b = max(int(c[5:7], 16) - 25, 0)
        return f"#{r:02x}{g:02x}{b:02x}"

    def run_check(self):
        self.check_btn.configure(state="disabled", text="Running...")

        def task():
            health = get_windows_health()
            smart = self.monitor.get_smart_status()
            trim = SSDOptimizer.check_trim_status()
            boot = self.monitor.get_system_info().get("boot_time", 0)
            uptime_s = time.time() - boot
            days = int(uptime_s // 86400)
            hours = int((uptime_s % 86400) // 3600)

            def update():
                dism = health.get("dism_health", "Unknown")
                self.checks["DISM Image Health"].configure(text=dism,
                    text_color="#4ade80" if dism == "Healthy" else "#f59e0b" if "Repair" in dism else "#ef4444")
                sfc = health.get("sfc_status", "Unknown")
                self.checks["SFC File Integrity"].configure(text=sfc,
                    text_color="#4ade80" if sfc == "Healthy" else "#ef4444")
                smart_ok = all(d.get("status", "").strip().lower() in ("ok", "good") for d in smart) if smart else False
                smart_count = len(smart)
                smart_text = f"{smart_count} drives OK" if smart_ok else f"{smart_count} drives, issues" if smart else "N/A"
                self.checks["Disk SMART Status"].configure(text=smart_text,
                    text_color="#4ade80" if smart_ok else "#ef4444" if smart else "#64748b")
                trim_ok = trim.get("trim_enabled")
                self.checks["SSD TRIM Status"].configure(text="Enabled" if trim_ok else "Disabled",
                    text_color="#4ade80" if trim_ok else "#f59e0b" if trim_ok is False else "#64748b")
                self.checks["System Uptime"].configure(text=f"{days}d {hours}h", text_color="white")
                self.check_btn.configure(state="normal", text="🔄 Run Full Health Check")
                self._log("Health check completed")
            self.after(0, update)

        threading.Thread(target=task, daemon=True).start()

    def _run_repair(self, name, func):
        self._log(f"Starting {name}...")
        func(lambda tool, ok, out: self.after(0, lambda: self._log(f"{'✓' if ok else '✗'} {name} finished")))

    def _log(self, msg):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", f"> {msg}\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")
