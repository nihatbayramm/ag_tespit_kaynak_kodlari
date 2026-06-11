"""
FFT Komuta Merkezi Dashboard v15.5 - Bilgilendirilmiş Siber Arayüz
Yazar: Nihat Bayram
Amaç: PCAP analizini yüksek çözünürlüklü arayüzde, detaylı saldırı teşhisi ve önerilerle sunmak.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time
import os
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Renk Paleti
BG_COLOR = "#0a0b10"
SIDE_COLOR = "#0d1117"
ACCENT_BLUE = "#00d4ff"
ACCENT_GREEN = "#39ff14"
ACCENT_RED = "#ff3131"
GOLDEN = "#e0a100"
TEXT_COLOR = "#e6edf3"
BORDER_COLOR = "#30363d"

ctk.set_appearance_mode("Dark")

class CommandCenter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AĞ GÜVENLİĞİ KOMUTA MERKEZİ - NİHAT BAYRAM")
        self.geometry("1600x980")
        self.configure(fg_color=BG_COLOR)

        self.target_path = None
        self.is_scanning = False
        self.uptime_start = time.time()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.update_system_stats()

    def setup_ui(self):
        # --- SOL PANEL ---
        self.left_sidebar = ctk.CTkFrame(self, fg_color=SIDE_COLOR, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.left_sidebar, text="🛡️ AĞ GÜVENLİĞİ", font=("Orbitron", 18, "bold"), text_color=ACCENT_BLUE)
        self.logo_label.pack(pady=(30, 5))
        ctk.CTkLabel(self.left_sidebar, text="KOMUTA MERKEZİ", font=("Consolas", 12), text_color=TEXT_COLOR).pack()

        self.status_badge = ctk.CTkButton(self.left_sidebar, text="SİSTEM DURUMU: GÜVENLİ", fg_color="transparent", 
                                          border_width=1, border_color=ACCENT_GREEN, text_color=ACCENT_GREEN, 
                                          height=28, hover=False, font=("Consolas", 11, "bold"))
        self.status_badge.pack(padx=20, fill="x", pady=20)

        self.create_sidebar_section(self.left_sidebar, "Aktif İzleyiciler", ["Canlı Trafik İzleyici", "İşlemci Monitörü", "Yük Analizörü", "Sinyal İşleyici"])
        self.create_sidebar_section(self.left_sidebar, "Tehdit Türleri", ["DDoS Saldırısı", "Kötü Amaçlı Yazılım"], bullet_color=ACCENT_RED)

        # Yeni: Canlı Sniffing Modu Toggle
        import random
        self.sniff_var = tk.BooleanVar(value=False)
        self.sniff_switch = ctk.CTkSwitch(self.left_sidebar, text="CANLI TRAFİK DİNLEME", variable=self.sniff_var, 
                                          progress_color=ACCENT_GREEN, font=("Consolas", 11, "bold"), command=self.toggle_sniffing)
        self.sniff_switch.pack(padx=20, pady=10)

        self.btn_select = ctk.CTkButton(self.left_sidebar, text="📁 PCAP DOSYASI SEÇ", fg_color="#21262d", command=self.dosya_sec)
        self.btn_select.pack(padx=20, fill="x", side="bottom", pady=10)
        self.btn_run = ctk.CTkButton(self.left_sidebar, text="⚡ ANALİZİ BAŞLAT", fg_color=ACCENT_BLUE, text_color="black", font=("Arial", 12, "bold"), command=self.analiz_thread_baslat)
        self.btn_run.pack(padx=20, fill="x", side="bottom", pady=(20, 0))

        # --- ORTA PANEL ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="SİSTEM ANALİTİK GENEL BAKIŞ", font=("Orbitron", 22, "bold"), text_color=TEXT_COLOR).pack(side="left")
        self.date_label = ctk.CTkLabel(header_frame, text="", font=("Consolas", 13), text_color=ACCENT_BLUE)
        self.date_label.pack(side="right")

        # Grafik Kutuları
        self.chart_area = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.chart_area.pack(fill="both", expand=True)

        self.chart_frame1 = self.create_chart_container(self.chart_area, "AĞ TRAFİK YOĞUNLUK TRENDİ")
        self.chart_frame2 = self.create_chart_container(self.chart_area, "SPEKTRAL FREKANS İMZASI")

        # --- RADAR OVERLAY (YENİLENMİŞ) ---
        self.overlay = tk.Canvas(self.chart_area, bg="#0a0b10", highlightthickness=0)
        self.radar_angle = 0
        
        # --- YENİ: DETAYLI ANALİZ RAPORU BÖLÜMÜ ---
        self.report_container = ctk.CTkFrame(self.main_content, fg_color="#0d1117", border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        self.report_container.pack(fill="both", expand=True, pady=(10, 0))
        
        ctk.CTkLabel(self.report_container, text="📑 DETAYLI ANALİZ VE İSTİHBARAT RAPORU", font=("Consolas", 12, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", padx=15, pady=10)
        
        self.report_text = ctk.CTkTextbox(self.report_container, fg_color="transparent", text_color=TEXT_COLOR, font=("Consolas", 12), border_width=0)
        self.report_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.report_text.insert("1.0", "Analiz başlatılmadı. Lütfen bir veri seti seçerek 'ANALİZİ BAŞLAT' butonuna tıklayın.")
        self.report_text.configure(state="disabled")

        self.setup_plots()

        # --- SAĞ PANEL ---
        self.right_sidebar = ctk.CTkFrame(self, fg_color=SIDE_COLOR, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(self.right_sidebar, text="SİSTEM STABİLİTESİ", font=("Consolas", 14, "bold"), text_color=TEXT_COLOR).pack(pady=(30, 5))
        self.stability_val = ctk.CTkLabel(self.right_sidebar, text="99.9%", font=("Orbitron", 42, "bold"), text_color=ACCENT_BLUE)
        self.stability_val.pack()
        self.stability_bar = ctk.CTkProgressBar(self.right_sidebar, fg_color="#161b22", progress_color=ACCENT_BLUE)
        self.stability_bar.pack(padx=30, fill="x", pady=10)
        self.stability_bar.set(0.999)

        self.stats_frame = ctk.CTkFrame(self.right_sidebar, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=30, pady=30)
        self.meta_uptime = self.add_stat_row(self.stats_frame, "Çalışma Süresi:", "0 Gün, 00:00:00")
        self.meta_cpu_avg = self.add_stat_row(self.stats_frame, "İşlemci Yükü:", "N/A")
        self.meta_mem = self.add_stat_row(self.stats_frame, "Bellek:", "N/A")
        self.meta_engine = self.add_stat_row(self.stats_frame, "FFT MOTORU:", "AKTİF", val_color=ACCENT_GREEN)

        ctk.CTkLabel(self.right_sidebar, text="AĞ DÜĞÜM DURUMLARI", font=("Consolas", 12, "bold"), text_color=TEXT_COLOR).pack(pady=(20, 10))
        self.nodes_frame = ctk.CTkFrame(self.right_sidebar, fg_color="transparent")
        self.nodes_frame.pack()
        self.node_indicators = []
        for r in range(3):
            for c in range(4):
                node = ctk.CTkLabel(self.nodes_frame, text="⬢", font=("Arial", 30), text_color=ACCENT_GREEN)
                node.grid(row=r, column=c, padx=5, pady=2)
                self.node_indicators.append(node)

    def toggle_sniffing(self):
        if self.sniff_var.get():
            self.status_badge.configure(text="SİSTEM DURUMU: CANLI DİNLEME", border_color=ACCENT_GREEN, text_color=ACCENT_GREEN)
            self.report_text.configure(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert("1.0", "[CANLI MOD] Ağ arayüzü dinleniyor... Paketler FFT motoruna aktarılıyor.")
            self.report_text.configure(state="disabled")
            self.sniff_thread = threading.Thread(target=self.live_sniff_simulation, daemon=True)
            self.sniff_thread.start()
        else:
            self.status_badge.configure(text="SİSTEM DURUMU: GÜVENLİ", border_color=ACCENT_GREEN, text_color=ACCENT_GREEN)

    def live_sniff_simulation(self):
        """Gerçek zamanlı trafik simülasyonu"""
        import random
        while self.sniff_var.get():
            from gercek_zamanli_test import uret_ve_kaydet_canli
            tmp_pcap = f"live_tmp_{int(time.time())}.pcap"
            uret_ve_kaydet_canli(tmp_pcap, tip=random.choice([0, 0, 0, 1, 2, 4])) 
            
            from analiz_motoru import pcap_analiz_et
            res = pcap_analiz_et(tmp_pcap)
            if res:
                self.after(0, lambda r=res: self.render_results(r))
            
            try: os.remove(tmp_pcap)
            except: pass
            time.sleep(2)

    def create_sidebar_section(self, parent, title, items, bullet_color=ACCENT_BLUE):
        ctk.CTkLabel(parent, text=title.upper(), font=("Consolas", 12, "bold"), text_color="#8b949e").pack(anchor="w", padx=20, pady=(20, 10))
        for item in items:
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", padx=20)
            ctk.CTkLabel(frame, text="•", text_color=bullet_color, font=("Arial", 16)).pack(side="left")
            ctk.CTkLabel(frame, text=item, font=("Consolas", 11), text_color=TEXT_COLOR).pack(side="left", padx=10)

    def create_chart_container(self, parent, title):
        container = ctk.CTkFrame(parent, fg_color="#0d1117", border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        container.pack(fill="both", expand=True, pady=5)
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(header, text=title, font=("Consolas", 11, "bold"), text_color=TEXT_COLOR).pack(side="left")
        return container

    def add_stat_row(self, parent, label, val, val_color=TEXT_COLOR):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label, font=("Consolas", 11), text_color="#8b949e").pack(side="left")
        val_lbl = ctk.CTkLabel(row, text=val, font=("Consolas", 11, "bold"), text_color=val_color)
        val_lbl.pack(side="right")
        return val_lbl

    def setup_plots(self):
        plt.style.use('dark_background')
        self.fig1, self.ax1 = plt.subplots(figsize=(8, 2.5), facecolor=BG_COLOR)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.chart_frame1)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10)

        self.fig2, self.ax2 = plt.subplots(figsize=(8, 2.5), facecolor=BG_COLOR)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.chart_frame2)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10)

    def update_system_stats(self):
        diff = int(time.time() - self.uptime_start)
        self.meta_uptime.configure(text=f"{diff // 86400} G, {(diff % 86400) // 3600:02d}:{(diff % 3600) // 60:02d}:{diff % 60:02d}")
        
        cpu_val = "N/A"
        mem_val = "N/A"

        if HAS_PSUTIL:
            cpu_val = f"%{psutil.cpu_percent()}"
            mem_val = f"%{psutil.virtual_memory().percent}"
        else:
            # Linux Fallback (Psutil yoksa)
            try:
                # CPU Fallback (Load Average)
                with open("/proc/loadavg", "r") as f:
                    load = f.read().split()[0]
                    cpu_val = f"Load: {load}"
                
                # Mem Fallback
                with open("/proc/meminfo", "r") as f:
                    lines = f.readlines()
                    total = int(lines[0].split()[1])
                    free = int(lines[1].split()[1])
                    used_pct = int(100 - (free / total * 100))
                    mem_val = f"%{used_pct}"
            except:
                pass

        self.meta_cpu_avg.configure(text=cpu_val)
        self.meta_mem.configure(text=mem_val)
        
        self.date_label.configure(text=time.strftime("%d %b %Y | %H:%M:%S UTC"))
        self.after(1000, self.update_system_stats)

    def dosya_sec(self):
        dosya = filedialog.askopenfilename(filetypes=[("Pcap Dosyası", "*.pcap")])
        if dosya:
            self.target_path = dosya
            self.status_badge.configure(text=f"YÜKLENDİ: {os.path.basename(dosya)}", border_color=ACCENT_BLUE, text_color=ACCENT_BLUE)

    def radar_update(self):
        if not self.is_scanning:
            return
        
        self.overlay.delete("all")
        w = self.overlay.winfo_width() / 2
        h = self.overlay.winfo_height() / 2
        if w < 10: 
            self.after(50, self.radar_update)
            return

        radius = min(w, h) * 0.4
        
        # Halkalar
        for i in range(1, 5):
            r = radius * (i / 4)
            self.overlay.create_oval(w-r, h-r, w+r, h+r, outline="#1f2937", width=1)
        
        # Tarama Çizgisi
        rad = np.deg2rad(self.radar_angle)
        ex = w + radius * np.cos(rad)
        ey = h + radius * np.sin(rad)
        self.overlay.create_line(w, h, ex, ey, fill=ACCENT_GREEN, width=3)
        
        # Granül
        glow = 5 + 5 * np.abs(np.sin(rad * 2))
        self.overlay.create_oval(ex-glow, ey-glow, ex+glow, ey+glow, fill=ACCENT_GREEN, outline="")

        self.overlay.create_text(w, h + radius + 40, text="SİNYAL ANALİZİ VE TEHDİT TARAMASI YAPILIYOR...", 
                                 fill=ACCENT_GREEN, font=("Consolas", 14, "bold"))

        self.radar_angle = (self.radar_angle + 6) % 360
        self.after(20, self.radar_update)

    def analiz_thread_baslat(self):
        if not self.target_path: return
        self.is_scanning = True
        self.btn_run.configure(state="disabled", text="ANALİZ EDİLİYOR...")
        self.status_badge.configure(text="SİSTEM DURUMU: TARANIYOR", border_color=GOLDEN, text_color=GOLDEN)
        
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.radar_update()
        
        threading.Thread(target=self.analiz_execute, daemon=True).start()

    def analiz_execute(self):
        time.sleep(2)
        try:
            from analiz_motoru import pcap_analiz_et
            res = pcap_analiz_et(self.target_path)
            self.is_scanning = False
            self.after(0, lambda: self.overlay.place_forget())
            self.after(0, lambda: self.render_results(res))
        except Exception as e:
            self.is_scanning = False
            self.after(0, lambda: self.overlay.place_forget())
            self.after(0, lambda err=e: messagebox.showerror("Hata", str(err)))
        finally:
            self.after(0, lambda: self.btn_run.configure(state="normal", text="⚡ ANALİZİ BAŞLAT"))

    def render_results(self, res):
        # Grafikler
        self.ax1.clear()
        self.ax1.plot(res["zaman_ekseni"], res["sinyal"], color=ACCENT_BLUE)
        self.ax1.fill_between(res["zaman_ekseni"], res["sinyal"], color=ACCENT_BLUE, alpha=0.1)
        self.ax1.set_title("AĞ TRAFİK AKIŞI", color=TEXT_COLOR, fontsize=9)
        self.canvas1.draw()

        self.ax2.clear()
        self.ax2.plot(res["xf"], res["yf"], color=ACCENT_RED if "SALDIRI" in res["durum"] else ACCENT_GREEN)
        self.ax2.set_title("SPEKTRAL FREKANS İMZASI", color=TEXT_COLOR, fontsize=9)
        self.canvas2.draw()

        # Rapor Metni Güncelleme
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", tk.END)
        
        info = [
            f"🎯 TESPİT EDİLEN DURUM : {res.get('durum', '-')}",
            f"⚔️ SALDIRI TÜRÜ        : {res.get('attack_type', '-')}",
            f"📊 V/O ORANI          : {res.get('vo', 0):.2f}",
            f"🌀 SPEKTRAL ENTROPİ   : {res.get('entropi', 0):.2f}",
            f"⚡ ENERJİ YOĞUNLUĞU   : {res.get('enerji_orani', 0):.2f}",
            f"📡 PİK FREKANS (Hz)   : {res.get('peak_f', 0):.2f}",
            f"----------------------------------------------------------",
            f"🛡️ ÖNERİLEN AKSİYONLAR VE GÜVENLİK PROTOKOLÜ:",
            f"{res.get('action', '-')}",
            f"----------------------------------------------------------",
            f"🕒 ANALİZ ZAMANI      : {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"📂 DOSYA KAYNAĞI      : {os.path.basename(self.target_path)}"
        ]
        self.report_text.insert(tk.END, "\n".join(info))
        self.report_text.configure(state="disabled")

        # Görsel Durumlar
        if "SALDIRI" in res["durum"]:
            self.status_badge.configure(text="SİSTEM DURUMU: SALDIRI TESPİT EDİLDİ", border_color=ACCENT_RED, text_color=ACCENT_RED)
            self.stability_val.configure(text=f"%{max(10, 100-int(res['vo']*10))}", text_color=ACCENT_RED)
            self.stability_bar.set(0.3)
            for node in self.node_indicators[:6]: node.configure(text_color=ACCENT_RED)
        else:
            self.status_badge.configure(text="SİSTEM DURUMU: GÜVENLİ", border_color=ACCENT_GREEN, text_color=ACCENT_GREEN)
            self.stability_val.configure(text="99.9%", text_color=ACCENT_GREEN)
            self.stability_bar.set(0.99)
            for node in self.node_indicators: node.configure(text_color=ACCENT_GREEN)

if __name__ == "__main__":
    app = CommandCenter()
    app.mainloop()