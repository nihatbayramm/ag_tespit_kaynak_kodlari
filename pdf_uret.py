"""
12. Hafta Sunum Metinleri - PDF Üreteci
Hafta10 PDF formatıyla uyumlu, slayt bazlı düzen
UTF-8 / Türkçe karakter desteği: DejaVu Sans TTF
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

# --- UTF-8 / Türkçe karakter için TTF fontları kaydet ---
DEJAVU_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("DejaVu",     DEJAVU_N))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", DEJAVU_B))

W, H = A4
FONT_B = "DejaVu-Bold"
FONT_N = "DejaVu"

BLUE_DARK  = colors.HexColor("#1a237e")
BLUE_MID   = colors.HexColor("#283593")
BLUE_LIGHT = colors.HexColor("#3949ab")
ACCENT     = colors.HexColor("#00acc1")
BG_LIGHT   = colors.HexColor("#e8eaf6")
BG_CYAN    = colors.HexColor("#e0f7fa")
TEXT_DARK  = colors.HexColor("#212121")
TEXT_GRAY  = colors.HexColor("#555555")
WHITE      = colors.white
GREEN      = colors.HexColor("#1b5e20")

# ---------- STİLLER ----------
def S():
    s = {}
    s["ders_ust"] = ParagraphStyle("ders_ust", fontName=FONT_B, fontSize=9,
        textColor=BG_LIGHT, alignment=TA_CENTER, leading=13)
    s["kapak_baslik"] = ParagraphStyle("kapak_baslik", fontName=FONT_B, fontSize=20,
        textColor=WHITE, alignment=TA_CENTER, leading=28)
    s["kapak_alt"] = ParagraphStyle("kapak_alt", fontName=FONT_N, fontSize=11,
        textColor=BG_LIGHT, alignment=TA_CENTER, leading=17)
    s["kapak_meta"] = ParagraphStyle("kapak_meta", fontName=FONT_N, fontSize=9.5,
        textColor=WHITE, alignment=TA_CENTER, leading=15)
    s["not_kutusu"] = ParagraphStyle("not_kutusu", fontName=FONT_N, fontSize=9,
        textColor=TEXT_DARK, alignment=TA_JUSTIFY, leading=14,
        leftIndent=10, rightIndent=10)
    s["slayt_baslik_ic"] = ParagraphStyle("slayt_baslik_ic", fontName=FONT_B, fontSize=13,
        textColor=WHITE, alignment=TA_LEFT, leading=20)
    s["slayt_alt_baslik"] = ParagraphStyle("slayt_alt_baslik", fontName=FONT_N, fontSize=10,
        textColor=BG_LIGHT, alignment=TA_LEFT, leading=15)
    s["metin"] = ParagraphStyle("metin", fontName=FONT_N, fontSize=9.5,
        textColor=TEXT_DARK, alignment=TA_JUSTIFY, leading=14.5, spaceAfter=4)
    s["bullet"] = ParagraphStyle("bullet", fontName=FONT_N, fontSize=9.5,
        textColor=TEXT_DARK, alignment=TA_LEFT, leading=14, leftIndent=14,
        bulletIndent=4, spaceAfter=3)
    s["caption"] = ParagraphStyle("caption", fontName=FONT_B, fontSize=8,
        textColor=TEXT_GRAY, alignment=TA_CENTER, spaceAfter=4, leading=12)
    s["tablo_h"] = ParagraphStyle("tablo_h", fontName=FONT_B, fontSize=8.5,
        textColor=WHITE, alignment=TA_CENTER)
    s["tablo_c"] = ParagraphStyle("tablo_c", fontName=FONT_N, fontSize=8.5,
        textColor=TEXT_DARK, alignment=TA_CENTER)
    s["tablo_b"] = ParagraphStyle("tablo_b", fontName=FONT_B, fontSize=8.5,
        textColor=BLUE_DARK, alignment=TA_CENTER)
    s["sonuc"] = ParagraphStyle("sonuc", fontName=FONT_B, fontSize=9,
        textColor=GREEN, alignment=TA_LEFT, leading=14,
        leftIndent=10)
    return s

def hr(color=BLUE_LIGHT, t=0.8):
    return HRFlowable(width="100%", thickness=t, color=color, spaceAfter=5, spaceBefore=4)

def resim(path, genislik, st, aciklama=None):
    elems = []
    try:
        with PILImage.open(path) as p:
            ow, oh = p.size
        h = genislik * (oh / ow)
        img = Image(path, width=genislik, height=h)
        img.hAlign = "CENTER"
        elems.append(img)
    except Exception as e:
        elems.append(Paragraph(f"[Gorsel yuklenemedi: {path}]", st["caption"]))
    if aciklama:
        elems.append(Paragraph(aciklama, st["caption"]))
    return elems

def bullet(text, st):
    return Paragraph(f"\u2022  {text}", st["bullet"])

def slayt_baslik(no, baslik, alt, st):
    """Slayt numaralı renkli başlık kutusu"""
    inner = [
        [Paragraph(f"Slayt {no}", st["ders_ust"])],
        [Paragraph(baslik, st["slayt_baslik_ic"])],
        [Paragraph(alt, st["slayt_alt_baslik"])],
    ]
    t = Table(inner, colWidths=[16.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
    ]))
    return [Spacer(1, 0.35*cm), t, Spacer(1, 0.2*cm)]

def ml_tablosu(st):
    data = [
        [Paragraph("Model", st["tablo_h"]),
         Paragraph("Doğruluk", st["tablo_h"]),
         Paragraph("Tespit\n(TPR)", st["tablo_h"]),
         Paragraph("Yanlış Alarm\n(FPR)", st["tablo_h"])],
        [Paragraph("Lojistik Regresyon", st["tablo_c"]),
         Paragraph("%83.3", st["tablo_c"]),
         Paragraph("%100", st["tablo_c"]),
         Paragraph("%100 ❌", st["tablo_c"])],
        [Paragraph("SVM", st["tablo_c"]),
         Paragraph("%83.3", st["tablo_c"]),
         Paragraph("%100", st["tablo_c"]),
         Paragraph("%100 ❌", st["tablo_c"])],
        [Paragraph("Random Forest", st["tablo_c"]),
         Paragraph("%98.3", st["tablo_c"]),
         Paragraph("%100", st["tablo_c"]),
         Paragraph("%10", st["tablo_c"])],
        [Paragraph("FFT Modeli (Önerimiz)", st["tablo_b"]),
         Paragraph("%77.5", st["tablo_b"]),
         Paragraph("%74", st["tablo_b"]),
         Paragraph("%5 ✅", st["tablo_b"])],
    ]
    col_w = [5.5*cm, 3*cm, 3*cm, 4.7*cm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),  (-1,0),  BLUE_MID),
        ("BACKGROUND", (0,1),  (-1,1),  BG_LIGHT),
        ("BACKGROUND", (0,2),  (-1,2),  WHITE),
        ("BACKGROUND", (0,3),  (-1,3),  BG_LIGHT),
        ("BACKGROUND", (0,4),  (-1,4),  BG_CYAN),
        ("GRID",       (0,0),  (-1,-1), 0.5, colors.HexColor("#bbdefb")),
        ("FONTNAME",   (0,4),  (-1,4),  FONT_B),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t

def esik_tablosu(st):
    data = [
        [Paragraph("Özellik", st["tablo_h"]),
         Paragraph("Normal μ", st["tablo_h"]),
         Paragraph("Normal σ", st["tablo_h"]),
         Paragraph("Saldırı μ", st["tablo_h"]),
         Paragraph("Hesaplanan Eşik", st["tablo_h"])],
        [Paragraph("Spektral Entropi (H)", st["tablo_c"]),
         Paragraph("0.78", st["tablo_c"]),
         Paragraph("0.01", st["tablo_c"]),
         Paragraph("0.75", st["tablo_c"]),
         Paragraph("H_esik = 0.75", st["tablo_b"])],
        [Paragraph("Varyans/Ortalama (Vo)", st["tablo_c"]),
         Paragraph("0.23", st["tablo_c"]),
         Paragraph("0.04", st["tablo_c"]),
         Paragraph("0.08", st["tablo_c"]),
         Paragraph("Vo_esik = 0.35", st["tablo_b"])],
    ]
    col_w = [4.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4.5*cm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),  (-1,0),  BLUE_LIGHT),
        ("BACKGROUND", (0,1),  (-1,1),  BG_LIGHT),
        ("BACKGROUND", (0,2),  (-1,2),  WHITE),
        ("GRID",       (0,0),  (-1,-1), 0.5, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t

# ===================== PDF OLUŞTUR =====================
def generate():
    out = "Hafta12_Sunum_Metinleri.pdf"
    doc = SimpleDocTemplate(out, pagesize=A4,
        leftMargin=1.9*cm, rightMargin=1.9*cm,
        topMargin=1.6*cm, bottomMargin=1.6*cm,
        title="Hafta 12 Sunum Metinleri - FFT Anomali Tespiti",
        author="Nihat Bayram")

    st = S()
    story = []

    # ---------- KAPAK ----------
    kapak_data = [
        [Paragraph("SAYISAL SİNYAL İŞLEME II — 12. HAFTA", st["kapak_baslik"])],
        [Spacer(1, 0.2*cm)],
        [Paragraph("FFT Tabanlı Ağ Anomali Tespiti", st["kapak_alt"])],
        [Paragraph("Proje Sunum Metinleri", st["kapak_alt"])],
        [Spacer(1, 0.8*cm)],
        [Paragraph("Öğrenci : Nihat Bayram", st["kapak_meta"])],
        [Paragraph("Tarih   : 28 Nisan 2026", st["kapak_meta"])],
        [Spacer(1, 0.4*cm)],
    ]
    kapak_t = Table(kapak_data, colWidths=[16.2*cm])
    kapak_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(Spacer(1, 1.5*cm))
    story.append(kapak_t)
    story.append(Spacer(1, 0.5*cm))
    story.append(hr(BLUE_LIGHT, 1.2))

    # Öğrenci notu kutusu
    not_data = [[Paragraph(
        "📌 <b>Öğrenci Notu:</b> Bu hafta hocalarımızın zorunlu olarak belirlediği üç geliştirme "
        "yönlendirmesini (veri setinin genişletilmesi, farklı saldırı senaryoları, gerçek zamanlı "
        "stabilite testi) eksiksiz tamamladım. Sunumda bu üç başlığı sırasıyla, gerçek test "
        "çıktıları ve görseller eşliğinde sunacağım.", st["not_kutusu"])]]
    not_t = Table(not_data, colWidths=[16.2*cm])
    not_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_LIGHT),
        ("BOX",        (0,0), (-1,-1), 1,  BLUE_LIGHT),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
    ]))
    story.append(not_t)
    story.append(PageBreak())

    # =================== SLAYT 1 ===================
    story += slayt_baslik(1,
        "Veri Setinin Genişletilmesi ve Yeni Saldırı Senaryoları",
        "Çeşitlendirilmiş Veri Seti: 6 Farklı Trafik Sınıfı, 120 PCAP Dosyası", st)

    story.append(Paragraph(
        "Önceki haftalarda modelimizi 4 trafik tipi (Normal, UDP Flood, TCP SYN, Slowloris) "
        "ve 40 PCAP dosyasıyla test etmiştik. Hocalarımızın <b>'gerçek veri çeşitliliğini artırın'</b> "
        "yönlendirmesi doğrultusunda bu hafta iki yeni saldırı vektörü eklendi:", st["metin"]))
    story.append(bullet("<b>ICMP Flood (Ping Flood):</b> Düşük boyutlu ama yüksek frekanslı ICMP paketleriyle "
        "hedef sistemin kaynaklarını tüketen, ağ katmanında çalışan bir DDoS yöntemi. "
        "Yoğun ve düzenli paket akışı nedeniyle FFT'de belirgin yüksek frekans tepeleri oluşturur.", st))
    story.append(bullet("<b>HTTP GET Flood:</b> TCP Push-Ack (PA) bayraklı paketlerle uygulama katmanına "
        "yönelik saldırı. Bant genişliği değil; sunucu işlem kapasitesi hedef alınıyor.", st))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(
        "Her sınıftan <b>20'şer PCAP</b> üretilerek toplamda <b>120 farklı ağ senaryosu</b> "
        "test uzayına dahil edilmiştir. Bu genişleme, modelin genelleştirme kapasitesini "
        "(generalization) stres testine tabi tutmuştur.", st["metin"]))

    story.append(Spacer(1, 0.3*cm))
    story += resim("WİRESHARKSS.png", 14.5*cm, st,
                   "Şekil 1: Gerçek Wireshark yakalaması — referans ağ trafik örneği")
    story.append(PageBreak())

    # =================== SLAYT 2 ===================
    story += slayt_baslik(2,
        "Karar Mekanizması — μ ± 3σ Eşik Kalibrasyonu",
        "Genişletilmiş Veri Setinde Matematiksel Eşik Doğrulaması", st)

    story.append(Paragraph(
        "120 dosyanın istatistiksel analizi, önceki dar veri setinden elde edilen "
        "<b>μ ± 3σ eşiklerinin hâlâ geçerli olduğunu</b> doğrulamıştır. "
        "performans_testi.py çıktısından elde edilen güncel dağılım değerleri:", st["metin"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(esik_tablosu(st))
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(
        "Bu sonuçlar; algoritmamızın veri seti büyüdükçe dağılım kararlılığını koruduğunu ve "
        "eşik değerlerinin istatistiksel sağlamlığını ortaya koymaktadır. Yeni eklenen ICMP ve "
        "HTTP saldırıları için ilerleyen haftada eşik kalibrasyonu yapılması planlanmaktadır.", st["metin"]))

    story.append(Spacer(1, 0.2*cm))
    story += resim("FFTÇIKTI.png", 14.5*cm, st,
                   "Şekil 2: FFT Spektrum Çıktısı — Normal trafik (yüksek entropi) ve Saldırı (dar bant tepesi)")
    story.append(PageBreak())

    # =================== SLAYT 3 ===================
    story += slayt_baslik(3,
        "Kapsamlı Makine Öğrenmesi Karşılaştırması",
        "3 ML Algoritması ile Kıyaslamalı Analiz — Sınıf Dengesizliği Testinde", st)

    story.append(Paragraph(
        "Bu hafta tek bir ML modeli yerine <b>üç farklı makine öğrenmesi algoritması</b> "
        "aynı özellik vektörüyle [V/O, Entropi, Enerji, Peak] test edildi. "
        "Sonuçlar, sentetik ağ verilerinde sık karşılaşılan <b>Sınıf Dengesizliği (Class Imbalance)</b> "
        "probleminin ML modellerini nasıl çökertebildiğini açıkça ortaya koyuyor:", st["metin"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(ml_tablosu(st))
    story.append(Spacer(1, 0.25*cm))

    story.append(Paragraph(
        "<b>1. Sınıf Dengesizliği Etkisi:</b> Lojistik Regresyon ve SVM, her veriyi 'Saldırı' olarak "
        "işaretleyerek %100 Yanlış Alarm üretti — gerçek dünya ortamında kullanılamaz.", st["bullet"]))
    story.append(Paragraph(
        "<b>2. Random Forest:</b> Non-lineer sınırlar çizebilen yapısıyla %98.3 doğrulukla en iyi ML "
        "performansını gösterdi, ancak şeffaflık (interpretability) açısından kapalı kutu kalıyor.", st["bullet"]))
    story.append(Paragraph(
        "<b>3. FFT Modelimiz:</b> TPR'de gelişime alan bıraksa da Yanlış Alarm Oranını %5'te "
        "tutarak ve tamamen şeffaf matematik sunarak güvenilirliğini kanıtladı.", st["bullet"]))
    story.append(Spacer(1, 0.2*cm))
    story += resim("akademik kanıtYaklasımı.png", 11*cm, st,
                   "Şekil 3: Akademik Eşik Yaklaşımı ve ML Kıyaslaması")
    story.append(PageBreak())

    # =================== SLAYT 4 ===================
    story += slayt_baslik(4,
        "Gerçek Zamanlı Sistem Stabilite Testi",
        "Canlı Ağ Simülasyonu — Kesintisiz Akış Altında FFT Performansı", st)

    story.append(Paragraph(
        "Hocalarımızın <b>'gerçek zamanlı sistem stabilitesini test edin'</b> yönlendirmesi "
        "kapsamında bu hafta <b>gercek_zamanli_test.py</b> modülü yazıldı. "
        "Bu modül, bir ağ kartından akan canlı trafiği taklit ederek 500'er paketlik bloklarda "
        "kesintisiz analiz gerçekleştirmektedir.", st["metin"]))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph("15 saniye boyunca elde edilen ölçüm sonuçları:", st["metin"]))

    # Stabilite mini tablo
    stab_data = [
        [Paragraph("Metrik", st["tablo_h"]), Paragraph("Ölçülen Değer", st["tablo_h"])],
        [Paragraph("Toplam Test Süresi", st["tablo_c"]), Paragraph("15 Saniye — Kesintisiz", st["tablo_c"])],
        [Paragraph("İşlenen Akış Bloğu", st["tablo_c"]), Paragraph("29 Adet (x500 Paket/Blok)", st["tablo_c"])],
        [Paragraph("Ortalama İşlem Gecikmesi", st["tablo_c"]), Paragraph("~103 ms / Blok", st["tablo_b"])],
        [Paragraph("Maksimum Gecikme", st["tablo_c"]), Paragraph("~211 ms", st["tablo_c"])],
        [Paragraph("Bellek Sızıntısı", st["tablo_c"]), Paragraph("YOK — Stabil", st["tablo_b"])],
    ]
    stab_t = Table(stab_data, colWidths=[8.1*cm, 8.1*cm], repeatRows=1)
    stab_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0),  ACCENT),
        ("BACKGROUND", (0,1), (-1,1),  BG_LIGHT),
        ("BACKGROUND", (0,2), (-1,2),  WHITE),
        ("BACKGROUND", (0,3), (-1,3),  BG_LIGHT),
        ("BACKGROUND", (0,4), (-1,4),  WHITE),
        ("BACKGROUND", (0,5), (-1,5),  BG_CYAN),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#b2ebf2")),
        ("FONTNAME",   (0,5), (-1,5),  FONT_B),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(stab_t)
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(
        "Bu test; algoritmamızın sadece laboratuvar ortamında değil, gerçek bir "
        "Ağ Güvenliği izleme altyapısında da çalışabileceğini kanıtlar niteliktedir.", st["metin"]))
    story.append(Spacer(1, 0.15*cm))
    story += resim("spektralMetrikler.png", 13*cm, st,
                   "Şekil 4: Gerçek Zamanlı Spektral Metrik Raporlaması")
    story.append(PageBreak())

    # =================== SLAYT 5 ===================
    story += slayt_baslik(5,
        "Genel Değerlendirme ve 13. Hafta Vizyonu",
        "Projenin Olgunluk Seviyesi ve Final Sunumuna Hazırlık", st)

    story.append(Paragraph(
        "Bu hafta itibarıyla projemiz tüm akademik doğrulama kriterlerini karşılamış durumdadır:",
        st["metin"]))
    story.append(Spacer(1, 0.1*cm))

    for satir in [
        "✅  Karar mekanizması matematiksel olarak modellenmiştir (μ ± 3σ).",
        "✅  Veri seti 120 senaryoya genişletilmiş, 6 trafik sınıfı kapsanmıştır.",
        "✅  3 farklı ML algoritmasıyla kıyaslamalı analiz yapılmıştır.",
        "✅  Gerçek zamanlı stabilite testi tamamlanmış, sistem kararlı çalışmıştır.",
    ]:
        story.append(Paragraph(satir, st["sonuc"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>Önümüzdeki 13. Haftanın Adımları:</b>", st["metin"]))
    story.append(bullet("GUI'nin final sunum moduna alınması ve grafik dışa aktarım (export) özelliğinin eklenmesi.", st))
    story.append(bullet("Eşik kalibrasyonunun yeni saldırı türlerini (ICMP, HTTP) kapsayacak şekilde güncellenmesi.", st))
    story.append(bullet("Demo videosu ve GitHub README'nin hazırlanması.", st))
    story.append(Spacer(1, 0.5*cm))
    story.append(hr(BLUE_DARK, 1.5))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<b>Sunumumuz bu kadardı, teşekkürler.</b>", 
        ParagraphStyle("tesekkur", fontName=FONT_B, fontSize=11,
            textColor=BLUE_DARK, alignment=TA_CENTER, leading=16)))

    doc.build(story)
    print(f"PDF olusturuldu: {out}")

if __name__ == "__main__":
    generate()
