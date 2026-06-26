import customtkinter as ctk
import threading
from app.monitors.system_monitor import SystemMonitor

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.monitor = SystemMonitor()
        self.monitoring = False
        self.after_id = None
        self._last_proc = ""
        self._cached_stats = {}
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True)

        top_cards = ctk.CTkFrame(main, fg_color="transparent")
        top_cards.pack(fill="x", padx=15, pady=(15, 5))
        top_cards.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="g")

        self.cpu_card = self._big_card(top_cards, "CPU", "#3b82f6", 0)
        self.ram_card = self._big_card(top_cards, "RAM", "#8b5cf6", 1)
        self.gpu_card = self._big_card(top_cards, "GPU", "#ec4899", 2)
        self.disk_card = self._big_card(top_cards, "Disk", "#14b8a6", 3)

        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self.process_frame = ctk.CTkFrame(bottom, corner_radius=10)
        self.process_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(self.process_frame, text="Top Processes", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(8, 2))
        self.process_text = ctk.CTkTextbox(self.process_frame, wrap="none", state="disabled", font=ctk.CTkFont(size=11, family="Consolas"))
        self.process_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.quick_frame = ctk.CTkFrame(bottom, corner_radius=10, width=220)
        self.quick_frame.pack(side="right", fill="y", padx=(5, 0))
        self.quick_frame.pack_propagate(False)

        ctk.CTkLabel(self.quick_frame, text="Quick Actions", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(8, 5))

        actions = [
            ("Quick Cleanup", "#7c3aed", lambda: self._quick_action("Quick Cleanup")),
            ("Boost Now", "#16a34a", lambda: self._quick_action("Boost Now")),
            ("Flush DNS", "#0891b2", lambda: self._quick_action("Flush DNS")),
        ]
        for text, color, action in actions:
            ctk.CTkButton(self.quick_frame, text=text, fg_color=color,
                          hover_color=self._darken(color), height=32, corner_radius=6,
                          command=action).pack(fill="x", padx=10, pady=3)

    def _darken(self, c):
        r = max(int(c[1:3], 16) - 25, 0)
        g = max(int(c[3:5], 16) - 25, 0)
        b = max(int(c[5:7], 16) - 25, 0)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _big_card(self, parent, name, color, col):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1e293b")
        card.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(top, text=name, font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(side="left")

        val = ctk.CTkLabel(card, text="0%", font=ctk.CTkFont(size=32, weight="bold"))
        val.pack(anchor="w", padx=12, pady=(0, 0))

        sub = ctk.CTkLabel(card, text="Initializing...", font=ctk.CTkFont(size=11), text_color="#64748b", anchor="w")
        sub.pack(fill="x", padx=12, pady=(0, 4))

        bar = ctk.CTkProgressBar(card, height=4, corner_radius=2, progress_color=color)
        bar.pack(fill="x", padx=12, pady=(0, 8))
        bar.set(0)

        return {"value": val, "sub": sub, "bar": bar}

    def start_monitoring(self):
        if self.monitoring:
            return
        self.monitoring = True
        self._pending_refresh = False
        self._do_collect_and_update()

    def stop_monitoring(self):
        self.monitoring = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def _do_collect_and_update(self):
        if not self.monitoring:
            return
        self._pending_refresh = False
        threading.Thread(target=self._collect_stats, daemon=True).start()
        self.after_id = self.after(100, self._poll_stats)

    def _poll_stats(self):
        if not self.monitoring:
            return
        if self._pending_refresh:
            self._update_ui()
            self._pending_refresh = False
            interval = max(int(self.config.get("monitoring_interval", 3000)), 500)
            self.after_id = self.after(interval, self._do_collect_and_update)
        else:
            self.after_id = self.after(100, self._poll_stats)

    def _collect_stats(self):
        try:
            stats = {
                "cpu": self.monitor.get_cpu_usage(),
                "cpu_info": self.monitor.get_cpu_info(),
                "ram": self.monitor.get_ram_usage(),
                "gpus": self.monitor.get_gpu_usage(),
                "disks": self.monitor.get_disk_usage(),
                "top": self.monitor.get_top_processes(12),
            }
            self._cached_stats = stats
            self._pending_refresh = True
        except:
            pass

    def _update_ui(self):
        stats = self._cached_stats
        if not stats:
            return

        cpu = stats.get("cpu", 0)
        cpu_info = stats.get("cpu_info", {})
        ram = stats.get("ram", {})
        gpus = stats.get("gpus", [])
        disks = stats.get("disks", [])
        top = stats.get("top", [])

        self.cpu_card["value"].configure(text=f"{cpu:.0f}%")
        self.cpu_card["sub"].configure(text=f"{cpu_info.get('physical_cores',0)}C/{cpu_info.get('total_cores',0)}T @ {cpu_info.get('current_frequency',0):.0f}MHz")
        self.cpu_card["bar"].set(cpu / 100)

        self.ram_card["value"].configure(text=f"{ram.get('percent', 0):.0f}%")
        self.ram_card["sub"].configure(text=f"{ram.get('used', 0)/(1024**3):.1f}GB / {ram.get('total', 0)/(1024**3):.1f}GB")
        self.ram_card["bar"].set(ram.get('percent', 0) / 100)

        if gpus:
            g = gpus[0]
            self.gpu_card["value"].configure(text=f"{g['load']:.0f}%")
            self.gpu_card["sub"].configure(text=f"{g['temperature']:.0f} C | {g['name'][:25]}")
            self.gpu_card["bar"].set(g['load'] / 100)
        else:
            self.gpu_card["value"].configure(text="N/A")
            self.gpu_card["sub"].configure(text="No GPU detected")
            self.gpu_card["bar"].set(0)

        if disks:
            d = disks[0]
            self.disk_card["value"].configure(text=f"{d['percent']:.0f}%")
            self.disk_card["sub"].configure(text=f"{d['free']/(1024**3):.1f}GB free / {d['total']/(1024**3):.1f}GB")
            self.disk_card["bar"].set(d['percent'] / 100)
        else:
            self.disk_card["value"].configure(text="N/A")
            self.disk_card["sub"].configure(text="No disk")
            self.disk_card["bar"].set(0)

        proc_text = ""
        for i, proc in enumerate(top, 1):
            name = (proc.get('name', 'Unknown') or 'Unknown')[:28]
            p_cpu = proc.get('cpu_percent', 0) or 0
            p_ram = proc.get('memory_percent', 0) or 0
            proc_text += f"{i:2d}. {name:<28s} CPU:{p_cpu:5.1f}% RAM:{p_ram:5.1f}%\n"
        if proc_text != self._last_proc:
            self._last_proc = proc_text
            self.process_text.configure(state="normal")
            self.process_text.delete("1.0", "end")
            self.process_text.insert("1.0", proc_text)
            self.process_text.configure(state="disabled")

    def _quick_action(self, name):
        from app.config import log
        log(f"Quick action: {name}")
        if name == "Quick Cleanup":
            from app.utils.cleanup import run_full_cleanup
            threading.Thread(target=run_full_cleanup, daemon=True).start()
        elif name == "Flush DNS":
            from app.utils.admin import clear_dns_cache
            clear_dns_cache()

    def on_activate(self):
        pass
