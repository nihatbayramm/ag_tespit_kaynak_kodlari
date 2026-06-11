import os
import time
from veri_ureteci import pcap_olustur
from analiz_motoru import pcap_analiz_et

def coklu_saldiri_test_et():
    profiller = [
        "normal",
        "udp_flood",
        "dns_amp",
        "syn_flood",
        "port_scan",
        "http_get",
        "slowloris"
    ]
    
    paket_sayisi = 1000
    dosya_dizini = "test_veri"
    
    if not os.path.exists(dosya_dizini):
        os.makedirs(dosya_dizini)
        
    sonuclar = []
    
    print("--- 🛡️ ÇOKLU SALDIRI VALİDASYON TESTİ BAŞLIYOR ---")
    
    for profil in profiller:
        dosya_adi = os.path.join(dosya_dizini, f"{profil}.pcap")
        pcap_olustur(dosya_adi, paket_sayisi, profil)
        
        # Analiz Motoruna gönder
        res = pcap_analiz_et(dosya_adi)
        if res is None:
            print(f"HATA: {profil} analiz edilemedi.")
            continue
            
        durum = res["durum"]
        tespit = res["attack_type"]
        vo = res["vo"]
        peak_f = res["peak_f"]
        entropi = res["entropi"]
        enerji = res["enerji_orani"]
        
        # Doğruluk kontrolü (Basit metin kontrolü)
        beklenen = ""
        if profil == "normal": beklenen = "YOK (TEMİZ TRAFİK)"
        elif profil == "udp_flood": beklenen = "YÜKSEK YOĞUNLUKLU UDP/ICMP FLOOD"
        elif profil == "dns_amp": beklenen = "DNS AMPLIFICATION (YANSITMA) SALDIRISI"
        elif profil == "syn_flood": beklenen = "TCP SYN FLOOD (BOTNET)"
        elif profil == "port_scan": beklenen = "PORT SCANNING (TARAMA) TESPİTİ"
        elif profil == "http_get": beklenen = "APP LAYER (HTTP GET FLOOD) SALDIRISI"
        elif profil == "slowloris": beklenen = "YAVAŞ HTTP (SLOWLORIS) SALDIRISI"
        
        basarili = (tespit == beklenen)
        
        sonuclar.append({
            "profil": profil,
            "tespit": tespit,
            "basarili": basarili,
            "vo": vo,
            "peak_f": peak_f,
            "entropi": entropi
        })
        
        print(f"\n[{profil.upper()}] Testi:")
        print(f"  Beklenen: {beklenen}")
        print(f"  Bulunan:  {tespit}")
        print(f"  Peak F:   {peak_f:.2f} Hz | Vo: {vo:.2f} | Entropi: {entropi:.2f}")
        print(f"  Sonuç:    {'✅ BAŞARILI' if basarili else '❌ BAŞARISIZ'}")
        
    print("\n--- 📊 TEST ÖZETİ ---")
    basarili_sayisi = sum(1 for s in sonuclar if s["basarili"])
    print(f"Toplam Test: {len(profiller)} | Başarılı: {basarili_sayisi} | Doğruluk: %{(basarili_sayisi/len(profiller))*100:.1f}")

if __name__ == "__main__":
    coklu_saldiri_test_et()
