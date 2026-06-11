"""
Analiz Motoru - PCAP Sinyal İşleme Çekirdeği
Yazar: Nihat Bayram
Amaç: PCAP okur, zaman-seri histogram → FFT → Saldırı tespiti (Vo + spektral peak)
Kütüphaneler: scapy (PCAP), scipy (FFT/Poisson), numpy
"""

import numpy as np
from scapy.all import PcapReader
from scipy.fft import fft, fftfreq
from scipy.stats import poisson

def pcap_analiz_et(dosya_yolu):
    """
    Ana analiz fonksiyonu:
    1. PCAP'den timestamp çıkar (max 25k paket, large file sampling)
    2. Histogram → sinyal dizisi
    3. İstatistik (mean/var/Vo)
    4. FFT spektral analiz
    5. Saldırı tespiti kuralları (Vo>3 + peak freq)
    6. Poisson beklenen dağılım
    7. Rapor dict döner (GUI için)
    """
    zamanlar = []
    try:
        # Performans optimizasyonu: Büyük PCAP'ler için akıllı sampling (Smart Sampling)
        max_packets = 50000 # Üst sınır artırıldı
        over_limit = 250000 # Tarama limiti artırıldı
        packet_count = 0
        with PcapReader(dosya_yolu) as reader:
            for paket in reader:
                packet_count += 1
                if packet_count > over_limit:
                    break

                if packet_count <= max_packets:
                    zamanlar.append(float(paket.time))
                else:
                    # Büyük dosya için dinamik sampling rate
                    sample_rate = int(packet_count / 10000) + 1
                    if packet_count % sample_rate == 0:
                        zamanlar.append(float(paket.time))

        if len(zamanlar) == 0:
            return None

    except Exception as e:
        print(f"pcap_analiz_et hata: {e}")
        return None

    if len(zamanlar) < 5: return None

    # Zaman normalize + histogram → sinyal dizisi (Daha yüksek çözünürlük: 100 bin)
    zamanlar = np.array(zamanlar) - zamanlar[0]
    toplam_sure = zamanlar[-1]
    bin_sayisi = 100 # Çözünürlük 50'den 100'e çıkarıldı
    sinyal, _ = np.histogram(zamanlar, bins=bin_sayisi)
    
    # Temel istatistikler
    avg = np.mean(sinyal)
    var = np.var(sinyal)
    vo_ratio = var / (avg + 1e-9)
    
    # FFT Spektral Analiz
    N = len(sinyal)
    hanning_window = np.hanning(N)
    windowed_sinyal = sinyal * hanning_window
    
    yf_raw = fft(windowed_sinyal)
    xf = fftfreq(N, toplam_sure/bin_sayisi)[:N//2]
    yf = 2.0/N * np.abs(yf_raw[0:N//2])
    
    # Spektral Özellikler
    peak_f = xf[np.argmax(yf[1:]) + 1] if len(yf) > 1 else 0.0
    peak_power = float(np.max(yf))
    
    enerji = float(np.sum(yf**2))
    
    # Spektral Entropi
    psd = yf**2
    psd_norm = psd / (np.sum(psd) + 1e-9)
    psd_non_zero = psd_norm[psd_norm > 0]
    entropi = float(-np.sum(psd_non_zero * np.log2(psd_non_zero)))
    
    # Enerji Oranı
    enerji_orani = enerji / (avg + 1e-9)

    # Özellik Vektörü
    feature_vector = np.array([vo_ratio, entropi, enerji_orani, peak_power])
    
    # --- GELİŞTİRİLMİŞ KARAR MANTIĞI (WEEK 14) ---
    saldiri_turu = "YOK (TEMİZ TRAFİK)"
    onlem = "Sistem normal. İzlemeye devam ediliyor."
    durum = "NORMAL TRAFİK ✅"

    # Eşik değerler Week 14 yük testlerine göre optimize edildi.
    # Normal trafik entropisi genellikle 0.80+ üzerindedir.
    is_attack = vo_ratio > 1.8 or (entropi < 0.72 and enerji_orani > 1.2)

    if is_attack:
        durum = "SALDIRI TESPİT EDİLDİ ⚠️"
        if peak_f > 20:
            saldiri_turu = "YÜKSEK YOĞUNLUKLU UDP/ICMP FLOOD"
            onlem = "1. Rate Limiting aktif et.\n2. Kaynak IP'leri Firewall üzerinden drop et.\n3. ISP ile iletişime geç."
        elif 10 < peak_f <= 20:
            saldiri_turu = "DNS AMPLIFICATION (YANSITMA) SALDIRISI"
            onlem = "1. Open Resolver'ları kısıtla.\n2. Yanıt boyutu filtreleme uygula.\n3. Any sorgularını engelle."
        elif 2 < peak_f <= 10:
            saldiri_turu = "TCP SYN FLOOD (BOTNET)"
            onlem = "1. SYN Proxy aktif et.\n2. Yarı-açık bağlantı zaman aşımını düşür.\n3. Anormal paket boylarını engelle."
        elif 0.5 < peak_f <= 2:
            saldiri_turu = "PORT SCANNING (TARAMA) TESPİTİ"
            onlem = "1. Port knocking yapılandır.\n2. Kaynak IP'yi geçici olarak blokla.\n3. IDS kurallarını güncelle."
        elif 0.1 < peak_f <= 0.5:
            saldiri_turu = "APP LAYER (HTTP GET FLOOD) SALDIRISI"
            onlem = "1. WAF kurallarını aktifleştir.\n2. Captcha doğrulaması ekle.\n3. User-Agent bazlı filtreleme yap."
        else:
            saldiri_turu = "YAVAŞ HTTP (SLOWLORIS) SALDIRISI"
            onlem = "1. Minimum veri hızını kontrol et.\n2. Bağlantı ömrünü (Timeout) kısıtla.\n3. Load Balancer eşiklerini güncelle."

    # Rapor Metni
    rapor = (f"> [DURUM]      : {durum}\n"
             f"> [TÜR]        : {saldiri_turu}\n"
             f"> [ETKİ]       : %{min(100, int(vo_ratio*12))} Yoğunluk\n"
             f"------------------------------------\n"
             f"🛡️ ÖNERİLEN AKSİYONLAR:\n"
             f"{onlem}")

    return {
        "sinyal": sinyal,
        "zaman_ekseni": np.linspace(0, toplam_sure, bin_sayisi),
        "xf": xf,
        "yf": yf,
        "x_pois": np.arange(0, np.max(sinyal)+5),
        "y_pois": poisson.pmf(np.arange(0, np.max(sinyal)+5), avg)*len(sinyal),
        "avg": avg,
        "var": var,
        "vo": vo_ratio,
        "entropi": entropi,
        "enerji": enerji,
        "enerji_orani": enerji_orani,
        "bilgi_vektoru": feature_vector.tolist(),
        "peak_f": peak_f,
        "peak_power": peak_power,
        "duration": toplam_sure,
        "packets": len(zamanlar),
        "attack_type": saldiri_turu,
        "action": onlem,
        "durum": durum,
        "bilgi": rapor
    }