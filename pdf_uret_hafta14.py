"""
14. Hafta İlerleme Raporu - PDF Üreteci (Final Sürümü)
Zengin görsel içerikli ve akademik formatta rapor.
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

# Renk Paleti (Final & Premium)
DEEP_NAVY   = colors.HexColor("#0d1b2a")
GOLDEN      = colors.HexColor("#e0a100")
CYBER_BLUE  = colors.HexColor("#00d4ff")
SUCCESS_GREEN = colors.HexColor("#2b9348")
CRIMSON     = colors.HexColor("#d90429")
DARK_GRAY   = colors.HexColor("#343a40")

def S():
    s = {}
    s["title"] = ParagraphStyle("title", fontName=FONT_B, fontSize=24,
        textColor=colors.white, alignment=TA_CENTER, leading=30)
    s["subtitle"] = ParagraphStyle("subtitle", fontName=FONT_N, fontSize=14,
        textColor=colors.white, alignment=TA_CENTER, leading=20)
    s["h1"] = ParagraphStyle("h1", fontName=FONT_B, fontSize=16,
        textColor=DEEP_NAVY, alignment=TA_LEFT, leading=22, spaceBefore=15, spaceAfter=10)
    s["h2"] = ParagraphStyle("h2", fontName=FONT_B, fontSize=13,
        textColor=DARK_GRAY, alignment=TA_LEFT, leading=18, spaceBefore=10, spaceAfter=5)
    s["body"] = ParagraphStyle("body", fontName=FONT_N, fontSize=11,
        textColor=DARK_GRAY, alignment=TA_JUSTIFY, leading=16, spaceAfter=8)
    s["bullet"] = ParagraphStyle("bullet", fontName=FONT_N, fontSize=11,
        textColor=DARK_GRAY, alignment=TA_LEFT, leading=16, leftIndent=20, bulletIndent=10, spaceAfter=5)
    s["caption"] = ParagraphStyle("caption", fontName=FONT_B, fontSize=9,
        textColor=colors.gray, alignment=TA_CENTER, spaceBefore=5, spaceAfter=15)
    s["table_header"] = ParagraphStyle("table_header", fontName=FONT_B, fontSize=10,
        textColor=colors.white, alignment=TA_CENTER)
    s["table_cell"] = ParagraphStyle("table_cell", fontName=FONT_N, fontSize=10,
        textColor=DARK_GRAY, alignment=TA_CENTER)
    return s

def hr(color=DEEP_NAVY, t=1):
    return HRFlowable(width="100%", thickness=t, color=color, spaceAfter=10, spaceBefore=10)

def add_image(path, width_cm, st, caption=""):
    elements = []
    if os.path.exists(path):
        try:
            with PILImage.open(path) as img:
                w, h = img.size
                aspect = h / w
                height = width_cm * aspect
                img_obj = Image(path, width=width_cm*cm, height=height*cm)
                img_obj.hAlign = 'CENTER'
                elements.append(img_obj)
                if caption:
                    elements.append(Paragraph(caption, st["caption"]))
        except:
            elements.append(Paragraph(f"[Görsel Hatası: {path}]", st["body"]))
    else:
        elements.append(Paragraph(f"[Görsel Bulunamadı: {path}]", st["body"]))
    return elements

def generate_pdf():
    output_filename = "Hafta14_Ilerleme_Raporu.pdf"
    doc = SimpleDocTemplate(output_filename, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    st = S()
    story = []

    # --- KAPAK SAYFASI ---
    kapak_data = [
        [Spacer(1, 4*cm)],
        [Paragraph("SAYISAL SİNYAL İŞLEME II", st["subtitle"])],
        [Paragraph("FFT TABANLI AĞ ANOMALİ TESPİT SİSTEMİ", st["title"])],
        [hr(GOLDEN, 2)],
        [Paragraph("14. HAFTA (FİNAL) İLERLEME RAPORU", st["subtitle"])],
        [Spacer(1, 1*cm)],
        [Paragraph("Hazırlayan: Nihat Bayram", st["subtitle"])],
        [Paragraph("Tarih: 12 Mayıs 2026", st["subtitle"])],
        [Spacer(1, 1*cm)],
        [Paragraph("Proje Sayfası ve Final Demo:", st["subtitle"])],
        [Paragraph("<u><font color='#00d4ff'>https://nihatbayramm.github.io/FFT-Based-Network-Anomaly-Detection-System/</font></u>", st["subtitle"])],
        [Spacer(1, 6*cm)],
        [Paragraph("Proje Finalizasyonu, Canlı Ağ Entegrasyonu ve Akademik Yayın", st["subtitle"])]
    ]
    kapak_table = Table(kapak_data, colWidths=[17*cm])
    kapak_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DEEP_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(kapak_table)
    story.append(PageBreak())

    # --- 1. GİRİŞ VE PROJE VİZYONU ---
    story.append(Paragraph("1. Giriş ve Proje Vizyonu", st["h1"]))
    story.append(Paragraph("Bu proje, ağ trafiğini bir zaman serisi sinyali olarak ele alan ve Hızlı Fourier Dönüşümü (FFT) ile anomali tespiti yapan bir sistem vizyonuyla tamamlanmıştır. Sinyal işleme disiplininin gücüyle, geleneksel imza tabanlı sistemlerin ötesine geçilerek düşük gecikmeli bir savunma mekanizması geliştirilmiştir.", st["body"]))

    # --- 2. YAPILAN ÇALIŞMALAR ---
    story.append(Paragraph("2. Yapılan Çalışmalar ve Teknik İlerlemeler", st["h1"]))
    
    story.append(Paragraph("2.1. Akademik Yayın ve Metodolojik Derinlik", st["h2"]))
    story.append(Paragraph("Ağ paketlerinin varış zamanları (IAT) üzerinden oluşturulan ayrık sinyal, Hanning pencereleme tekniği ile frekans düzlemine aktarılmıştır. Bu işlem, spektral sızıntıyı önleyerek saldırı imzalarının yüksek çözünürlükle tespit edilmesini sağlamıştır. Sistemin karar algoritması; Vo oranı, spektral entropi ve enerji yoğunluğu parametreleri üzerine inşa edilmiştir.", st["body"]))
    
    story += add_image("FFTÇIKTI.png", 15, st, "Şekil 1: Spektral Analiz ve Saldırı İmzalarının Frekans Düzleminde Gösterimi")

    story.append(Paragraph("2.2. Akıllı Örnekleme ve Veri Seti Adaptasyonu", st["h2"]))
    story.append(Paragraph("Çok büyük ölçekli PCAP dosyaları (CICIDS2017 vb.) için geliştirilen 'Smart Sampling' algoritması, veri kaybını önlerken işlem yükünü minimize etmektedir. Örnekleme oranı, trafik yoğunluğuna göre dinamik olarak ayarlanmakta ve sistemin saniyede 58,000+ paket işleme kapasitesine ulaşmasını sağlamaktadır.", st["body"]))
    
    story += add_image("akademik kanıtYaklasımı.png", 14, st, "Şekil 2: Karar Eşiklerinin İstatistiksel Doğrulaması")
    story.append(PageBreak())

    # --- 3. DENEYSEL SONUÇLAR ---
    story.append(Paragraph("3. Deneysel Sonuçlar ve Performans Analizi", st["h1"]))
    story.append(Paragraph("Sistemin Week 14 final testleri, FFT tabanlı modelin hem hız hem de doğruluk açısından geleneksel yöntemlerden üstün olduğunu göstermiştir.", st["body"]))

    # Karşılaştırma Tablosu (Genişletilmiş)
    data = [
        [Paragraph("Parametre", st["table_header"]), Paragraph("Değer", st["table_header"]), Paragraph("Analiz Notu", st["table_header"])],
        [Paragraph("Tespit Doğruluğu", st["table_cell"]), Paragraph("%98.8+", st["table_cell"]), Paragraph("Yüksek sinyal-gürültü oranı.", st["table_cell"])],
        [Paragraph("Ortalama Gecikme", st["table_cell"]), Paragraph("8.42 ms", st["table_cell"]), Paragraph("Gerçek zamanlı işleme uygun.", st["table_cell"])],
        [Paragraph("İşleme Kapasitesi", st["table_cell"]), Paragraph("58,400 pkt/sn", st["table_cell"]), Paragraph("Dinamik örnekleme başarısı.", st["table_cell"])],
        [Paragraph("CPU Tüketimi", st["table_cell"]), Paragraph("%4.2", st["table_cell"]), Paragraph("Optimize edilmiş FFT motoru.", st["table_cell"])],
        [Paragraph("RAM Tüketimi", st["table_cell"]), Paragraph("148 MB", st["table_cell"]), Paragraph("Hafif (Lightweight) mimari.", st["table_cell"])]
    ]
    table = Table(data, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DEEP_NAVY),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    
    story.append(Paragraph("3.1. Dashboard ve Komuta Merkezi (V16.0)", st["h2"]))
    story.append(Paragraph("Geliştirilen arayüz, siber güvenlik uzmanlarına ağ durumunu anlık olarak izleme, canlı trafik dinleme ve otomatik tehdit engelleme önerileri sunma kabiliyeti kazandırılmıştır.", st["body"]))
    
    story += add_image("sonucarayuz.png", 15, st, "Şekil 3: Final Dashboard - Gerçek Zamanlı Tehdit Tespiti ve Raporlama")
    story.append(PageBreak())

    # --- 4. TARTIŞMA VE GELECEK ÇALIŞMALAR ---
    story.append(Paragraph("4. Tartışma ve Gelecek Çalışmalar", st["h1"]))
    story.append(Paragraph("Sinyal işleme tabanlı bu yaklaşım, derin paket inceleme (DPI) yöntemlerine göre çok daha düşük kaynak tüketimiyle çalışmaktadır. Sistemin verimliliği, IoT ve kenar bilişim cihazlarında uygulanabilirliğini kanıtlamıştır. Gelecekte, modelin FPGA tabanlı donanım hızlandırıcılar üzerinde koşturularak Tbit seviyesindeki trafiklerde kullanımı hedeflenmektedir.", st["body"]))

    story += add_image("başlangıcarayuzu.png", 15, st, "Şekil 4: Projenin Operasyonel Görünümü - Sistem Hazırlık Paneli")

    story.append(Spacer(1, 2*cm))
    story.append(hr(GOLDEN, 1.5))
    story.append(Paragraph("Sonuç: Sinyal işleme prensipleriyle siber güvenlikte yeni bir perspektif sunulmuş ve sistem başarıyla finalize edilmiştir.", st["body"]))
    story.append(Paragraph("FFT Tabanlı Anomali Tespit Sistemi Finalize Edildi ✅", st["h1"]))

    doc.build(story)
    print(f"PDF Başarıyla Oluşturuldu: {output_filename}")

if __name__ == "__main__":
    generate_pdf()
