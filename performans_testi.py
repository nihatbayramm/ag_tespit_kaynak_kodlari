import os
import numpy as np
import time
from scapy.all import IP, TCP, UDP, ICMP, wrpcap
import random
from analiz_motoru import pcap_analiz_et
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score, confusion_matrix
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# --- VERİ ÜRETECİ (Genişletilmiş Veri Seti & Farklı Saldırı Senaryoları) ---
def uret_ve_kaydet(dosya, tip):
    paketler = []
    su_an = 0.0
    paket_sayisi = 2000
    if tip == 0: # Normal Trafik
        for i in range(paket_sayisi):
            aralik = random.uniform(0.01, 0.1)
            su_an += aralik
            p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=80)
            p.time = su_an
            paketler.append(p)
    elif tip == 1: # UDP Flood
        for i in range(paket_sayisi):
            aralik = random.uniform(0.001, 0.005) 
            su_an += aralik
            p = IP(dst="192.168.1.1")/UDP(sport=random.randint(1024,65535), dport=53)
            p.time = su_an
            paketler.append(p)
    elif tip == 2: # TCP SYN Flood
        for i in range(paket_sayisi):
            aralik = 0.008
            su_an += aralik
            p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=443, flags="S")
            p.time = su_an
            paketler.append(p)
    elif tip == 3: # Slowloris
        for i in range(500): 
            aralik = 0.8 
            su_an += aralik
            p = IP(dst="192.168.1.1")/TCP(sport=1234, dport=80)
            p.time = su_an
            paketler.append(p)
    elif tip == 4: # ICMP Flood (YENİ)
        for i in range(paket_sayisi):
            aralik = random.uniform(0.002, 0.006)
            su_an += aralik
            p = IP(dst="192.168.1.1")/ICMP()
            p.time = su_an
            paketler.append(p)
    elif tip == 5: # HTTP Flood (YENİ)
        for i in range(paket_sayisi):
            aralik = random.uniform(0.005, 0.01)
            su_an += aralik
            p = IP(dst="192.168.1.1")/TCP(sport=random.randint(1024,65535), dport=80, flags="PA")
            p.time = su_an
            paketler.append(p)
    
    wrpcap(dosya, paketler)

print("1. Genişletilmiş Veriseti Üretiliyor (Toplam 120 .pcap)...")
veri_klasor = "test_veri"
if not os.path.exists(veri_klasor):
    os.makedirs(veri_klasor)

dosyalar = []
etiketler = []
tur_sayisi = 20 # Her türden 20 adet üreteceğiz, toplam 120

for i in range(tur_sayisi):  # Normal
    k = f"{veri_klasor}/normal_{i}.pcap"
    uret_ve_kaydet(k, 0)
    dosyalar.append(k)
    etiketler.append(0)
for i in range(tur_sayisi): # UDP Flood
    k = f"{veri_klasor}/udp_{i}.pcap"
    uret_ve_kaydet(k, 1)
    dosyalar.append(k)
    etiketler.append(1)
for i in range(tur_sayisi): # TCP SYN
    k = f"{veri_klasor}/syn_{i}.pcap"
    uret_ve_kaydet(k, 2)
    dosyalar.append(k)
    etiketler.append(1)
for i in range(tur_sayisi): # Slowloris
    k = f"{veri_klasor}/slow_{i}.pcap"
    uret_ve_kaydet(k, 3)
    dosyalar.append(k)
    etiketler.append(1)
for i in range(tur_sayisi): # ICMP Flood
    k = f"{veri_klasor}/icmp_{i}.pcap"
    uret_ve_kaydet(k, 4)
    dosyalar.append(k)
    etiketler.append(1)
for i in range(tur_sayisi): # HTTP Flood
    k = f"{veri_klasor}/http_{i}.pcap"
    uret_ve_kaydet(k, 5)
    dosyalar.append(k)
    etiketler.append(1)

print("2. Özellik Çıkarımı (Feature Extraction) Başlıyor...")
X = []
y = []
preds_heuristic = []
islem_sureleri = []

vo_n, ent_n, en_n = [], [], []
vo_a, ent_a, en_a = [], [], []

for idx, f in enumerate(dosyalar):
    basla = time.time()
    res = pcap_analiz_et(f)
    bitis = time.time()
    islem_sureleri.append(bitis - basla)

    if not res: continue
    lbl = etiketler[idx]
    
    vec = res["bilgi_vektoru"] 
    X.append(vec)
    y.append(lbl)
    
    if lbl == 0:
        vo_n.append(vec[0])
        ent_n.append(vec[1])
        en_n.append(vec[2])
    else:
        vo_a.append(vec[0])
        ent_a.append(vec[1])
        en_a.append(vec[2])
    
    is_attack = "SALDIRI" in res["durum"]
    preds_heuristic.append(1 if is_attack else 0)

X = np.array(X)
y = np.array(y)
preds_heuristic = np.array(preds_heuristic)

print("\n--- İSTATİSTİKSEL ANALİZ (Eşiklerin Matematiksel Gerekçesi) ---")
print(f"Normal Trafik -> Vo Ortalama: min={np.min(vo_n):.2f}, ort={np.mean(vo_n):.2f}, max={np.max(vo_n):.2f}")
print(f"Saldırı Trafiği-> Vo Ortalama: min={np.min(vo_a):.2f}, ort={np.mean(vo_a):.2f}, max={np.max(vo_a):.2f}")
print(f"Normal Trafik -> Entropi Ort: {np.mean(ent_n):.2f} (Std: {np.std(ent_n):.2f})")
print(f"Saldırı Trafiği-> Entropi Ort: {np.mean(ent_a):.2f} (Std: {np.std(ent_a):.2f})")

esik_ent = np.mean(ent_n) - 3*np.std(ent_n)
print(f"Matematiksel Entropi Eşiği (Mean - 3*Std): {esik_ent:.2f}")

esik_vo = np.mean(vo_n) + 3*np.std(vo_n)
print(f"Matematiksel Vo Eşiği (Mean + 3*Std): {esik_vo:.2f}")

print(f"\nOrtalama PCAP İşleme Süresi (Gerçek Zamanlı Stabilite Göstergesi): {np.mean(islem_sureleri)*1000:.2f} ms")

def calc_metrics(y_true, y_pred):
    tn = np.sum((y_true == 0) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    acc = (tp + tn) / len(y_true)
    tpr = tp / (tp + fn) if (tp+fn)>0 else 0 
    fpr = fp / (fp + tn) if (fp+tn)>0 else 0 
    return acc, tpr, fpr

acc_h, tpr_h, fpr_h = calc_metrics(y, preds_heuristic)

print("\n--- ÖNERİLEN HEURİSTİK MODEL (Eşik Tabanlı) MÜHENDİSLİK BAŞARIMI ---")
print(f"Doğruluk (Accuracy)  : %{acc_h * 100:.1f}")
print(f"Tespit Oranı (TPR)   : %{tpr_h * 100:.1f}")
print(f"Yalancı Alarm (FPR)  : %{fpr_h * 100:.1f}")

if SKLEARN_AVAILABLE:
    print("\n--- GENİŞLETİLMİŞ KARŞILAŞTIRMALI ANALİZ (Makine Öğrenmesi Modelleri) ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
    
    modeller = {
        "Lojistik Regresyon": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42),
        "Destek Vektör Makineleri (SVM)": SVC(kernel='linear')
    }
    
    for isim, model in modeller.items():
        model.fit(X_train, y_train)
        preds_ml = model.predict(X)
        acc_ml, tpr_ml, fpr_ml = calc_metrics(y, preds_ml)
        print(f"\n[{isim}]")
        print(f"Doğruluk (Accuracy)  : %{acc_ml * 100:.1f}")
        print(f"Tespit Oranı (TPR)   : %{tpr_ml * 100:.1f}")
        print(f"Yalancı Alarm (FPR)  : %{fpr_ml * 100:.1f}")
else:
    print("\n[UYARI] scikit-learn yüklü olmadığı için ML karşılaştırması atlandı. 'pip install scikit-learn' çalıştırın.")
