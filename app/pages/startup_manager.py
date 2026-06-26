import customtkinter as ctk
import threading
from app.utils.startup import StartupManager

class StartupManagerPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.manager = StartupManager()
        self.items = []
        self.checkboxes = {}
        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Startup Manager", font=ctk.CTkFont(size=24, weight="bold"), anchor="w")
        title.pack(pady=(20, 5), padx=20, fill="x")

        ctk.CTkLabel(self, text="Manage which programs run at Windows startup", font=ctk.CTkFont(size=12), text_color="gray", anchor="w").pack(anchor="w", padx=20)

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(10, 5))

        self.refresh_btn = ctk.CTkButton(controls, text="🔄 Refresh", command=self.load_items, fg_color="#1f538d", width=120)
        self.refresh_btn.pack(side="left")

        self.status_label = ctk.CTkLabel(controls, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=15)

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        self.list_frame = ctk.CTkScrollableFrame(main, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def on_activate(self):
        self.after(200, self.load_items_delayed)

    def load_items_delayed(self):
        self.load_items()

    def load_items(self):
        self.refresh_btn.configure(state="disabled", text="Loading...")

        def task():
            items = self.manager.get_startup_items()
            self.items = items
            self.after(0, self._display_items)
            self.after(0, lambda: self.refresh_btn.configure(state="normal", text="🔄 Refresh"))
            self.after(0, lambda: self.status_label.configure(text=f"{len(items)} startup items found"))

        threading.Thread(target=task, daemon=True).start()

    def _display_items(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.checkboxes.clear()

        if not self.items:
            ctk.CTkLabel(self.list_frame, text="No startup items found", text_color="gray").pack(pady=30)
            return

        header = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=(5, 0))
        ctk.CTkLabel(header, text="Program Name", font=ctk.CTkFont(size=12, weight="bold"), width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Command", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkLabel(header, text="Location", font=ctk.CTkFont(size=12, weight="bold"), width=100, anchor="w").pack(side="right", padx=10)

        for item in self.items:
            row = ctk.CTkFrame(self.list_frame, fg_color=("gray90", "gray17"), height=32)
            row.pack(fill="x", padx=5, pady=1)

            switch = ctk.CTkSwitch(row, text="", onvalue=True, offvalue=False, width=30,
                                   command=lambda n=item["name"], c=item.get("command",""), l=item.get("location",""): self._toggle_startup(n, c, l))
            switch.pack(side="left", padx=(8, 5))
            self.checkboxes[item["name"]] = switch

            ctk.CTkLabel(row, text=item["name"], font=ctk.CTkFont(size=12), width=200, anchor="w").pack(side="left", padx=5)
            cmd = item.get("command", "")
            if len(cmd) > 60:
                cmd = cmd[:57] + "..."
            ctk.CTkLabel(row, text=cmd, font=ctk.CTkFont(size=11), text_color="gray", anchor="w").pack(side="left", fill="x", expand=True, padx=5)
            loc = item.get("location", "")
            if "HKLM" in loc:
                loc_display = "HKLM"
            elif "HKCU" in loc:
                loc_display = "HKCU"
            elif "Startup" in loc:
                loc_display = "Startup Folder"
            else:
                loc_display = loc[:20]
            ctk.CTkLabel(row, text=loc_display, font=ctk.CTkFont(size=11), text_color="gray", width=100, anchor="w").pack(side="right", padx=5)

    def _toggle_startup(self, name, command, location):
        self.status_label.configure(text=f"Toggling {name}...")
        def task():
            ok = self.manager.disable_startup_item(name, location)
            self.after(0, lambda: self.status_label.configure(
                text=f"{'Disabled' if ok else 'Failed'} {name}",
                text_color="#4ade80" if ok else "#ef4444"))
            self.after(1000, self.load_items)
        threading.Thread(target=task, daemon=True).start()
