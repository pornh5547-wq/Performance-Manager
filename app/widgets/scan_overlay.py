import tkinter as tk
import customtkinter as ctk
import math
import time

BG = "#050510"
PURPLE = "#8b5cf6"
PURPLE_DIM = "#4c1d95"
TEXT = "#c4b5fd"
TEXT_DIM = "#6b7280"

class ScanOverlay(ctk.CTkFrame):
    def __init__(self, parent, scan_manager, on_complete=None):
        super().__init__(parent, fg_color=BG)
        self.scan_manager = scan_manager
        self.on_complete = on_complete
        self._angle = 0
        self._pulse = 0.0
        self._dot_count = 0
        self._anim_id = None
        self._fading = False
        self._alpha = 1.0
        self._build()
        self._animate()

    def _build(self):
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", self._on_resize)

        self.title_label = ctk.CTkLabel(self, text="PM Performance Manager",
                                         font=ctk.CTkFont(size=26, weight="bold"), text_color=TEXT)
        self.title_label.place(relx=0.5, rely=0.48, anchor="center")

        self.dots_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16), text_color=PURPLE)
        self.dots_label.place(relx=0.5, rely=0.58, anchor="center")

        self.status_label = ctk.CTkLabel(self, text="Initializing...", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.status_label.place(relx=0.5, rely=0.64, anchor="center")

    def _on_resize(self, event):
        self._draw_triangle()

    def _draw_triangle(self):
        self.canvas.delete("tri")
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 600
        cx, cy = w // 2, h // 2 - 40

        base_size = min(w, h) * 0.1
        if base_size < 35:
            base_size = 35
        if base_size > 130:
            base_size = 130

        pulse = math.sin(self._pulse) * 0.5 + 0.5
        angle_rad = math.radians(self._angle)

        glow_size = base_size * (1.4 + 0.15 * pulse)
        glow_pts = []
        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            glow_pts.extend([cx + glow_size * math.cos(a), cy + glow_size * math.sin(a)])

        mid_size = base_size * (1.1 + 0.08 * pulse)
        mid_pts = []
        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            mid_pts.extend([cx + mid_size * math.cos(a), cy + mid_size * math.sin(a)])

        main_pts = []
        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            main_pts.extend([cx + base_size * math.cos(a), cy + base_size * math.sin(a)])

        inner_pts = []
        inner_size = base_size * 0.45
        for i in range(3):
            a = angle_rad + math.radians(180 + i * 120)
            inner_pts.extend([cx + inner_size * math.cos(a), cy + inner_size * math.sin(a)])

        glow_alpha = int(60 * pulse)
        self.canvas.create_polygon(glow_pts, fill="", outline=f"#8b5cf6{glow_alpha:02x}", width=2, tags="tri")

        mid_alpha = int(120 + 80 * pulse)
        mid_color = f"#a78bfa{mid_alpha:02x}"
        self.canvas.create_polygon(mid_pts, fill="", outline=mid_color, width=1, tags="tri")

        brightness = int(139 + 80 * pulse)
        main_color = f"#{brightness:02x}{max(92 - int(30 * pulse), 40):02x}{246:02x}"
        self.canvas.create_polygon(main_pts, fill="", outline=main_color, width=2.5, tags="tri")

        self.canvas.create_polygon(inner_pts, fill="", outline=PURPLE, width=1, tags="tri")

        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            x1 = cx + base_size * math.cos(a)
            y1 = cy + base_size * math.sin(a)
            r = 3 + 2 * pulse
            self.canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, fill=main_color, outline="", tags="tri")

    def _animate(self):
        if not self.winfo_exists():
            return
        self._angle = (self._angle + 1.5) % 360
        self._pulse += 0.04
        self._dot_count = (self._dot_count + 1) % 24

        self._draw_triangle()

        dots = "." * (1 + (self._dot_count // 8))
        self.dots_label.configure(text=f"Loading{dots}")

        progress = self.scan_manager.get_progress()
        if progress:
            self.status_label.configure(text=progress)

        if not self.scan_manager.is_running() and not self._fading:
            self._fading = True
            self._start_fade()
            return

        self._anim_id = self.after(35, self._animate)

    def _start_fade(self):
        self._alpha -= 0.05
        if self._alpha <= 0:
            self.destroy()
            if self.on_complete:
                self.on_complete()
            return
        self.configure(fg_color=self._blend(BG, self._alpha))
        self.canvas.configure(bg=self._blend(BG, self._alpha))
        for w in [self.title_label, self.dots_label, self.status_label]:
            c = w.cget("text_color")
            if c and c != "transparent":
                try:
                    w.configure(text_color=self._blend_text(c, self._alpha))
                except:
                    pass
        self.after(25, self._start_fade)

    def _blend(self, color, alpha):
        r, g, b = 5, 5, 16
        br, bg, bb = 15, 23, 42
        return f"#{int(r + (br - r) * (1 - alpha)):02x}{int(g + (bg - g) * (1 - alpha)):02x}{int(b + (bb - b) * (1 - alpha)):02x}"

    def _blend_text(self, color, alpha):
        try:
            hex_c = color.lstrip("#")
            r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
            tr, tg, tb = 226, 232, 240
            return f"#{int(r + (tr - r) * (1 - alpha)):02x}{int(g + (tg - g) * (1 - alpha)):02x}{int(b + (tb - b) * (1 - alpha)):02x}"
        except:
            return color
