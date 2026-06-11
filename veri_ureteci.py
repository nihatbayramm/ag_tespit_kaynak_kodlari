from scapy.all import IP, TCP, UDP, wrpcap
import random
import os

def pcap_olustur(dosya_adi, paket_sayisi, profil="normal"):
    paketler = []
    su_an = 0.0
    
    # Hedef frekans ve toplam süre ayarlamaları:
    # N=100 bin analiz motorunda sabittir. 
    # Max Frequency (Nyquist) = 50 / toplam_sure.
    # Çözünürlük (Resolution) = 1 / toplam_sure.
    
    if profil == "normal":
        # Temiz trafik: Düşük varyans (Vo < 1.8), rastgele
        toplam_sure = 10.0
        aralik = toplam_sure / paket_sayisi
        for i in range(paket_sayisi):
            su_an += random.uniform(aralik*0.5, aralik*1.5)
            p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=80)
            p.time = su_an
            paketler.append(p)
    else:
        # Saldırı profilleri: Yüksek Vo (Burst) ve Belirli Frekans
        if profil == "udp_flood": 
            f_hedef = 25.0; toplam_sure = 1.8
        elif profil == "dns_amp": 
            f_hedef = 15.0; toplam_sure = 3.0
        elif profil == "syn_flood": 
            f_hedef = 6.0; toplam_sure = 8.0
        elif profil == "port_scan": 
            f_hedef = 1.5; toplam_sure = 30.0
        elif profil == "http_get": 
            f_hedef = 0.3; toplam_sure = 120.0
        elif profil == "slowloris": 
            f_hedef = 0.08; toplam_sure = 500.0
        
        # Toplam burst sayısı
        burst_sayisi = int(f_hedef * toplam_sure)
        paket_per_burst = max(1, paket_sayisi // burst_sayisi)
        burst_araligi = toplam_sure / burst_sayisi
        
        for b in range(burst_sayisi):
            burst_zamani = b * burst_araligi
            for p_idx in range(paket_per_burst):
                # Burst içi paketler çok yakın zamanda gönderilir
                su_an = burst_zamani + random.uniform(0, 0.001)
                
                if profil == "udp_flood":
                    p = IP(dst="192.168.1.1")/UDP(sport=random.randint(1024,65535), dport=80)
                elif profil == "dns_amp":
                    p = IP(dst="192.168.1.1")/UDP(sport=53, dport=random.randint(1024,65535))
                elif profil == "syn_flood":
                    p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=80, flags="S")
                elif profil == "port_scan":
                    p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=p_idx%65535+1, flags="S")
                elif profil == "http_get":
                    p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=80, flags="PA")
                elif profil == "slowloris":
                    p = IP(dst="192.168.1.1")/TCP(sport=1234, dport=80, flags="A")
                
                p.time = su_an
                paketler.append(p)

    klasor = os.path.dirname(dosya_adi)
    if klasor and not os.path.exists(klasor):
        os.makedirs(klasor)
        
    # Paketleri zamana göre sırala (scapy düzgün çalışması için)
    paketler.sort(key=lambda pkt: pkt.time)
    wrpcap(dosya_adi, paketler)
    print(f"--- [{profil.upper()}] {dosya_adi} oluşturuldu! ({len(paketler)} pkt) ---")

if __name__ == "__main__":
    pcap_olustur("test_veri/normal_test.pcap", 1000, profil="normal")
    pcap_olustur("test_veri/udp_test.pcap", 1000, profil="udp_flood")