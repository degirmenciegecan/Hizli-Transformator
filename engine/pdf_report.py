"""
Professional PDF Engineering Report Generator for Power Transformers.
Built with ReportLab and TrueType UTF-8 font support (Türkçe karakter ve sembol desteği).
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Register TrueType Turkish Font ---
FONT_REGULAR_NAME = "Helvetica"
FONT_BOLD_NAME = "Helvetica-Bold"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
font_reg_path = os.path.join(BASE_DIR, "fonts", "Arial.ttf")
font_bold_path = os.path.join(BASE_DIR, "fonts", "Arial-Bold.ttf")

# Check fallback locations if needed
if not os.path.exists(font_reg_path):
    if os.path.exists("C:/Windows/Fonts/arial.ttf"):
        font_reg_path = "C:/Windows/Fonts/arial.ttf"
        font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    elif os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        font_reg_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if os.path.exists(font_reg_path) and os.path.exists(font_bold_path):
    try:
        pdfmetrics.registerFont(TTFont("TurkishFont", font_reg_path))
        pdfmetrics.registerFont(TTFont("TurkishFont-Bold", font_bold_path))
        pdfmetrics.registerFontFamily("TurkishFont", normal="TurkishFont", bold="TurkishFont-Bold")
        FONT_REGULAR_NAME = "TurkishFont"
        FONT_BOLD_NAME = "TurkishFont-Bold"
    except Exception as e:
        print("Font registration warning:", e)


def clean_text(val):
    """Safely cleans text to avoid missing glyphs like currency boxes."""
    if val is None:
        return "—"
    s = str(val)
    # Replace Turkish Lira symbol with TL for standard PDF rendering compatibility
    s = s.replace("₺", " TL").replace("CO₂", "CO2").replace("•", "&bull;")
    return s


def build_pdf_report(calc_results, input_params=None):
    """
    Generates a high-quality multi-page engineering test/design PDF report with 100% Turkish UTF-8 support.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles with UTF-8 Font
    title_style = ParagraphStyle(
        'DocTitle',
        fontName=FONT_BOLD_NAME,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName=FONT_REGULAR_NAME,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        alignment=1,
        spaceAfter=10
    )

    cat_title_style = ParagraphStyle(
        'CatTitle',
        fontName=FONT_BOLD_NAME,
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E40AF'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        fontName=FONT_BOLD_NAME,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        fontName=FONT_REGULAR_NAME,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )

    cell_header = ParagraphStyle(
        'CellHeader',
        fontName=FONT_BOLD_NAME,
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1
    )

    story = []

    # --- HEADER ---
    story.append(Paragraph("HIZLI TRANSFORMATÖR — AR-GE MÜHENDİSLİK HESAP RAPORU", title_style))
    date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    story.append(Paragraph(f"Standart: IEC 60076-1 / 60076-2 / 60076-3 / 60076-5 &bull; Rapor Tarihi: {date_str}", subtitle_style))

    el = calc_results.get('electrical', {})
    cd = calc_results.get('core_design', {})
    wd = calc_results.get('winding', {})
    ls = calc_results.get('losses', {})
    vr = calc_results.get('voltage_regulation', {})
    sc = calc_results.get('short_circuit', {})
    th = calc_results.get('thermal', {})
    ins = calc_results.get('insulation', {})
    mag = calc_results.get('magnetization', {})
    eco = calc_results.get('economic', {})
    cost = calc_results.get('cost', {})

    col_widths_4 = [46 * mm, 46 * mm, 46 * mm, 46 * mm]

    table_base_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])

    header_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    # --- 1. ELEKTRİKSEL ANALİZ ---
    story.append(Paragraph("1. Temel Elektriksel & Eşdeğer Devre Parametreleri (IEC 60076-1)", cat_title_style))
    el_data = [
        [Paragraph("Görünür Güç (S) / Frekans:", cell_normal), Paragraph(f"<b>{clean_text(el.get('S_kVA', '—'))} kVA</b> ({input_params.get('frequency', 50) if input_params else 50} Hz)", cell_bold),
         Paragraph("Sarım Oranı (a = V1/V2):", cell_normal), Paragraph(f"<b>{clean_text(el.get('a', '—'))}</b>", cell_bold)],
        [Paragraph("Primer Anma Gerilimi (V1):", cell_normal), Paragraph(f"<b>{clean_text(input_params.get('V1', '—') if input_params else '—')} V</b>", cell_bold),
         Paragraph("Sekonder Anma Gerilimi (V2):", cell_normal), Paragraph(f"<b>{clean_text(input_params.get('V2', '—') if input_params else '—')} V</b>", cell_bold)],
        [Paragraph("Primer Anma Akımı (I1):", cell_normal), Paragraph(f"<b>{clean_text(el.get('I1', '—'))} A</b>", cell_bold),
         Paragraph("Sekonder Anma Akımı (I2):", cell_normal), Paragraph(f"<b>{clean_text(el.get('I2', '—'))} A</b>", cell_bold)],
        [Paragraph("Kısa Devre Empedansı (uk%):", cell_normal), Paragraph(f"<b>%{clean_text(el.get('uk_pct', input_params.get('uk', '—') if input_params else '—'))}</b>", cell_bold),
         Paragraph("Kısa Devre Gerilimi (Vk):", cell_normal), Paragraph(f"<b>{clean_text(el.get('Vk', '—'))} V</b>", cell_bold)],
        [Paragraph("Eşdeğer Empedans (Zk):", cell_normal), Paragraph(f"<b>{clean_text(el.get('Zk', '—'))} Ω/faz</b>", cell_bold),
         Paragraph("Eşdeğer Direnç (Rk):", cell_normal), Paragraph(f"<b>{clean_text(el.get('Rk', '—'))} Ω/faz</b>", cell_bold)],
        [Paragraph("Eşdeğer Reaktans (Xk):", cell_normal), Paragraph(f"<b>{clean_text(el.get('Xk', '—'))} Ω/faz</b>", cell_bold),
         Paragraph("Kaçak Endüktans (Lk):", cell_normal), Paragraph(f"<b>{clean_text(el.get('Lk_mH', '—'))} mH</b>", cell_bold)],
        [Paragraph("Direnç / Reaktans Payı (ur / ux):", cell_normal), Paragraph(f"<b>%{clean_text(el.get('ur_pct', '—'))} / %{clean_text(el.get('ux_pct', '—'))}</b>", cell_bold),
         Paragraph("Tam Yük Verimi (cosφ=1):", cell_normal), Paragraph(f"<font color='#16A34A'><b>%{clean_text(el.get('efficiency', '—'))}</b></font>", cell_bold)],
    ]
    t1 = Table(el_data, colWidths=col_widths_4)
    t1.setStyle(table_base_style)
    story.append(t1)
    story.append(Spacer(1, 3 * mm))

    # --- 2. NÜVE & MANYETİK TASARIM ---
    story.append(Paragraph("2. Nüve (Çekirdek) Manyetik Tasarım Analizi (Faraday EMF)", cat_title_style))
    cd_data = [
        [Paragraph("Nüve Malzemesi:", cell_normal), Paragraph(f"<b>{clean_text(cd.get('core_label', '—'))}</b>", cell_bold),
         Paragraph("Çalışma Akı Yoğunluğu (Bm):", cell_normal), Paragraph(f"<b>{clean_text(cd.get('Bm', '—'))} Tesla</b>", cell_bold)],
        [Paragraph("Net Nüve Kesiti (Ai):", cell_normal), Paragraph(f"<b>{clean_text(cd.get('Ai_cm2', '—'))} cm²</b>", cell_bold),
         Paragraph("Brüt Nüve Kesiti (Ag):", cell_normal), Paragraph(f"<b>{clean_text(cd.get('Ag_cm2', '—'))} cm²</b>", cell_bold)],
        [Paragraph("Kademeli Nüve Çapı (d):", cell_normal), Paragraph(f"<b>{clean_text(cd.get('core_diameter_mm', '—'))} mm</b>", cell_bold),
         Paragraph("Hesapsal Nüve Ağırlığı (Gc):", cell_normal), Paragraph(f"<b>{clean_text(cd.get('core_weight_kg', '—'))} kg</b>", cell_bold)],
        [Paragraph("Hesapsal Boşta Kayıp (P0):", cell_normal), Paragraph(f"<b>{clean_text(cd.get('P0_estimated_W', '—'))} W</b>", cell_bold),
         Paragraph("Histerezis / Foucault Ayrışımı:", cell_normal), Paragraph(f"<b>{clean_text(cd.get('P_hysteresis_W', '—'))} W / {clean_text(cd.get('P_eddy_W', '—'))} W</b>", cell_bold)],
    ]
    t2 = Table(cd_data, colWidths=col_widths_4)
    t2.setStyle(table_base_style)
    story.append(t2)
    story.append(Spacer(1, 3 * mm))

    # --- 3. SARGI & İMALAT ANALİZİ ---
    story.append(Paragraph("3. Sargı, İletken Boyutlandırma & Yalıtım (IEC 60076-3)", cat_title_style))
    wd_data = [
        [Paragraph("Spesifik Gerilim (Et):", cell_normal), Paragraph(f"<b>{clean_text(el.get('Et', '—'))} V/Tur</b>", cell_bold),
         Paragraph("Ortalama Sarım Boyu (MLT):", cell_normal), Paragraph(f"HV: <b>{clean_text(wd.get('MLT_hv_mm', '—'))} mm</b> | LV: <b>{clean_text(wd.get('MLT_lv_mm', '—'))} mm</b>", cell_bold)],
        [Paragraph("Primer Sarım (N1) / Kesit:", cell_normal), Paragraph(f"<b>{clean_text(el.get('N1', '—'))} Tur</b> ({clean_text(el.get('A1', '—'))} mm² / Ø{clean_text(wd.get('d_conductor_hv_mm', '—'))}mm)", cell_bold),
         Paragraph("Sekonder Sarım (N2) / Kesit:", cell_normal), Paragraph(f"<b>{clean_text(el.get('N2', '—'))} Tur</b> ({clean_text(el.get('A2', '—'))} mm² / Ø{clean_text(wd.get('d_conductor_lv_mm', '—'))}mm)", cell_bold)],
        [Paragraph("Paralel Tel Sayısı (HV / LV):", cell_normal), Paragraph(f"<b>{wd.get('n_parallel_hv', 1)} / {wd.get('n_parallel_lv', 1)}</b>", cell_bold),
         Paragraph("75°C Referans Direnci:", cell_normal), Paragraph(f"HV: <b>{clean_text(wd.get('R_hv_75', '—'))} Ω</b> | LV: <b>{clean_text(wd.get('R_lv_75', '—'))} Ω</b>", cell_bold)],
        [Paragraph("Yalıtım Seviyesi (BIL - HV):", cell_normal), Paragraph(f"<b>{clean_text(ins.get('hv_BIL_kVp', '—'))} kVp</b> (AC: {clean_text(ins.get('hv_AC_test_kV', '—'))} kV)", cell_bold),
         Paragraph("Min. Kaçak / Yağ Açıklığı:", cell_normal), Paragraph(f"<b>{clean_text(ins.get('hv_creepage_mm', '—'))} mm / {clean_text(ins.get('oil_clearance_hv_mm', '—'))} mm</b>", cell_bold)],
    ]
    t3 = Table(wd_data, colWidths=col_widths_4)
    t3.setStyle(table_base_style)
    story.append(t3)
    story.append(Spacer(1, 3 * mm))

    # --- 4. VERİM & YÜK KAYIP TABLOSU ---
    story.append(Paragraph("4. Gelişmiş Verim & Yük Matrisi (Yıllık Enerji & Karbon Salımı)", cat_title_style))
    eff_matrix = [
        [Paragraph("Yük Seviyesi", cell_header), Paragraph("cosφ = 1.00", cell_header), Paragraph("cosφ = 0.90 (Endüktif)", cell_header), Paragraph("cosφ = 0.80 (Endüstriyel)", cell_header)]
    ]
    if ls.get('efficiency_table'):
        for row in ls['efficiency_table']:
            load_pct = int(round(float(row.get('load', 0)) * 100))
            s_val = float(input_params.get('S', 50000)) / 1000.0 if input_params else 50.0
            eff_matrix.append([
                Paragraph(f"<b>%{load_pct} Yük ({(float(row.get('load',0))*s_val):.1f} kVA)</b>", cell_normal),
                Paragraph(f"<b>%{clean_text(row.get('cos_1.0', '—'))}</b>", cell_normal),
                Paragraph(f"%{clean_text(row.get('cos_0.9', '—'))}", cell_normal),
                Paragraph(f"%{clean_text(row.get('cos_0.8', '—'))}", cell_normal)
            ])
    t4 = Table(eff_matrix, colWidths=col_widths_4)
    t4.setStyle(header_table_style)
    story.append(t4)
    story.append(Spacer(1, 3 * mm))

    # --- 5. TERMAL, GÜVENLİK & KISA DEVRE ---
    story.append(Paragraph("5. Termodinamik, Kısa Devre & Mekanik Güvenlik (IEC 60076-2 / 60076-5)", cat_title_style))
    th_sc_data = [
        [Paragraph("Toplam Isı Kaybı / Soğutma Alanı:", cell_normal), Paragraph(f"<b>{clean_text(th.get('total_heat_loss_W', '—'))} W</b> ({clean_text(th.get('cooling_area_m2', '—'))} m²)", cell_bold),
         Paragraph("Kullanılacak Yağ / Genleşme:", cell_normal), Paragraph(f"<b>{clean_text(th.get('oil_volume_L', '—'))} L</b> (+{clean_text(th.get('expansion_volume_L', '—'))} L)", cell_bold)],
        [Paragraph("Üst Yağ / Hot-Spot Sıcaklığı:", cell_normal), Paragraph(f"<b>{clean_text(th.get('top_oil_rise_C', '—'))} °C</b> / <b>{clean_text(th.get('hot_spot_temp_C', '—'))} °C</b>", cell_bold),
         Paragraph("Termal Zaman Sabiti / Soğutma:", cell_normal), Paragraph(f"<b>{clean_text(th.get('thermal_time_constant_h', '—'))} Saat</b> ({clean_text(th.get('recommended_cooling', 'ONAN'))})", cell_bold)],
        [Paragraph("Simetrik Kısa Devre (Isc):", cell_normal), Paragraph(f"HV: <b>{clean_text(sc.get('Isc_A', '—'))} A</b> | LV: <b>{clean_text(sc.get('Isc2_A', '—'))} A</b>", cell_bold),
         Paragraph("Asimetrik Tepe Akımı (Ipeak):", cell_normal), Paragraph(f"HV: <b>{clean_text(sc.get('Ipeak_A', '—'))} A</b> (X/R={clean_text(sc.get('xr_ratio', '—'))})", cell_bold)],
        [Paragraph("Dinamik Mekanik Kuvvetler:", cell_normal), Paragraph(f"Eksenel: <b>{clean_text(sc.get('F_axial_N', '—'))} N</b> | Radyal: <b>{clean_text(sc.get('F_radial_N', '—'))} N</b>", cell_bold),
         Paragraph("IEC Termal Kısa Devre Dayanımı:", cell_normal), Paragraph("<b>2.0 Saniye</b> (Standart)", cell_bold)],
    ]
    t5 = Table(th_sc_data, colWidths=col_widths_4)
    t5.setStyle(table_base_style)
    story.append(t5)
    story.append(Spacer(1, 3 * mm))

    # --- 6. EKONOMİK ANALİZ & TOC / LCC ---
    story.append(Paragraph("6. Finansal İhale, TOC & Yaşam Döngüsü Maliyeti (LCC)", cat_title_style))
    usd_try = float(calc_results.get('prices', {}).get('usd_try', 34.0))
    total_cost_usd = float(cost.get('total', {}).get('total_cost', 0))
    loss_cost_usd = float(eco.get('loss_cost_usd', 0))
    toc_usd = float(eco.get('toc_usd', 0))
    lcc_usd = float(eco.get('lcc_usd', 0))

    eco_data = [
        [Paragraph("İletken Sargı Maliyeti:", cell_normal), Paragraph(f"<b>${total_cost_usd:,.2f}</b> ({total_cost_usd*usd_try:,.2f} TL)", cell_bold),
         Paragraph("Kayıp Kapitalizasyon Bedeli:", cell_normal), Paragraph(f"<b>${loss_cost_usd:,.2f}</b> ({loss_cost_usd*usd_try:,.2f} TL)", cell_bold)],
        [Paragraph("Toplam Sahip Olma (TOC):", cell_normal), Paragraph(f"<font color='#EA580C'><b>${toc_usd:,.2f}</b></font> ({toc_usd*usd_try:,.2f} TL)", cell_bold),
         Paragraph("25 Yıllık Yaşam Döngüsü (LCC):", cell_normal), Paragraph(f"<font color='#2563EB'><b>${lcc_usd:,.2f}</b></font>", cell_bold)],
        [Paragraph("Yıllık Enerji Kaybı & CO2:", cell_normal), Paragraph(f"<b>{clean_text(ls.get('annual_loss_kWh', '—'))} kWh/yıl</b> ({clean_text(ls.get('co2_kg_year', '—'))} kg CO2)", cell_bold),
         Paragraph("Toplam Ağırlık (Kuru / Islak):", cell_normal), Paragraph(f"<b>{clean_text(cost.get('weights', {}).get('dry', '—'))} kg / {clean_text(cost.get('weights', {}).get('wet', '—'))} kg</b>", cell_bold)],
    ]
    t6 = Table(eco_data, colWidths=col_widths_4)
    t6.setStyle(table_base_style)
    story.append(t6)

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
