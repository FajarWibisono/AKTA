import streamlit as st
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)

# Konfigurasi halaman
st.set_page_config(
    page_title="AKTA - Anggaran Keuangan Tahunan",
    page_icon="💰",
    layout="wide"
)

# Fungsi untuk format rupiah
def format_idr(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

# Fungsi untuk menghitung alokasi anggaran
def calculate_budget(total_income):
    allocations = {}
    
    # Perhitungan berdasarkan persentase
    allocations['zakat'] = total_income * 0.025  # 2.5%
    allocations['iswaf'] = total_income * 0.075  # Max 7.5%
    
    # Pos Utang (Max 35% dari total)
    total_utang_max = total_income * 0.35
    allocations['utang_produktif'] = total_utang_max * (20/35)  # 20% dari total
    allocations['utang_konsumtif'] = total_utang_max * (15/35)  # 15% dari total
    allocations['utang_total'] = total_utang_max
    
    # Pos lainnya
    allocations['kontribusi_asuransi'] = total_income * 0.10  # min 10%
    allocations['dana_masa_depan'] = total_income * 0.10  # min 10%
    
    # Total pengeluaran tetap
    total_tetap = (allocations['zakat'] + allocations['iswaf'] + 
                   allocations['utang_total'] + allocations['kontribusi_asuransi'] + 
                   allocations['dana_masa_depan'])
    
    # Sisa untuk belanja sekarang
    allocations['belanja_sekarang'] = total_income - total_tetap
    allocations['total_anggaran'] = total_tetap + allocations['belanja_sekarang']
    allocations['surplus_defisit'] = total_income - allocations['total_anggaran']
    
    return allocations

# Warna tema
_C_GREEN_DARK  = colors.HexColor('#1B5E20')
_C_GREEN_MED   = colors.HexColor('#2E7D32')
_C_GREEN_LIGHT = colors.HexColor('#C8E6C9')
_C_GREEN_PALE  = colors.HexColor('#E8F5E9')
_C_STRIPE      = colors.HexColor('#F5F5F5')
_C_RED_DARK    = colors.HexColor('#C62828')
_C_RED_LIGHT   = colors.HexColor('#FFCDD2')
_C_GRAY        = colors.HexColor('#757575')


def _pdf_styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('title', parent=base['Normal'],
            fontSize=18, fontName='Helvetica-Bold',
            textColor=_C_GREEN_MED, alignment=TA_CENTER, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', parent=base['Normal'],
            fontSize=10, textColor=_C_GRAY, alignment=TA_CENTER, spaceAfter=6),
        'section': ParagraphStyle('section', parent=base['Normal'],
            fontSize=12, fontName='Helvetica-Bold',
            textColor=_C_GREEN_DARK, spaceBefore=10, spaceAfter=4),
        'caption': ParagraphStyle('caption', parent=base['Normal'],
            fontSize=8, fontName='Helvetica-Oblique',
            textColor=_C_GRAY, spaceAfter=4),
        'normal': ParagraphStyle('normal', parent=base['Normal'], fontSize=10),
        'right': ParagraphStyle('right', parent=base['Normal'],
            fontSize=10, alignment=TA_RIGHT),
        'center': ParagraphStyle('center', parent=base['Normal'],
            fontSize=9, alignment=TA_CENTER),
        'footer': ParagraphStyle('footer', parent=base['Normal'],
            fontSize=8, fontName='Helvetica-Oblique',
            textColor=_C_GRAY, alignment=TA_CENTER),
        'rec_surplus': ParagraphStyle('rec_surplus', parent=base['Normal'],
            fontSize=9, textColor=_C_GREEN_DARK, leading=14,
            leftIndent=6, rightIndent=6),
        'rec_defisit': ParagraphStyle('rec_defisit', parent=base['Normal'],
            fontSize=9, textColor=_C_RED_DARK, leading=14,
            leftIndent=6, rightIndent=6),
    }


# Fungsi untuk generate PDF dengan ReportLab
def generate_pdf(name, age, tetap, tidak_tetap, total_pemasukan, harga_emas, allocations):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )

    S = _pdf_styles()
    story = []
    page_w = A4[0] - 3.6 * cm

    # ── JUDUL ──────────────────────────────────────────────────────────────
    story.append(Paragraph("ANGGARAN KEUANGAN TAHUNAN (AKTA)", S['title']))
    story.append(Paragraph("Laporan Perencanaan Keuangan Pribadi", S['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=_C_GREEN_MED, spaceAfter=8))

    # ── DATA DIRI ──────────────────────────────────────────────────────────
    story.append(Paragraph("DATA DIRI", S['section']))

    info_data = [
        [Paragraph("<b>Nama</b>", S['normal']),
         Paragraph(name, S['normal'])],
        [Paragraph("<b>Usia</b>", S['normal']),
         Paragraph(f"{age} tahun", S['normal'])],
        [Paragraph("<b>Tanggal Dibuat</b>", S['normal']),
         Paragraph(datetime.now().strftime("%d %B %Y"), S['normal'])],
    ]
    info_tbl = Table(info_data, colWidths=[4 * cm, page_w - 4 * cm])
    info_tbl.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [_C_STRIPE, colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#E0E0E0')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 8))

    # ── PEMASUKAN TAHUNAN ──────────────────────────────────────────────────
    story.append(Paragraph("PEMASUKAN TAHUNAN", S['section']))

    def _rp(v, bold=False):
        txt = f"<b>{format_idr(v)}</b>" if bold else format_idr(v)
        return Paragraph(txt, S['right'])

    masuk_data = [
        [Paragraph("<b>Keterangan</b>", S['normal']),
         Paragraph("<b>Jumlah</b>", S['normal'])],
        [Paragraph("Pemasukan Tetap", S['normal']),         _rp(tetap)],
        [Paragraph("Pemasukan Tidak Tetap", S['normal']),   _rp(tidak_tetap)],
        [Paragraph("<b>Total Pemasukan</b>", S['normal']),  _rp(total_pemasukan, bold=True)],
        [Paragraph("Harga Per Gram Emas", S['normal']),     _rp(harga_emas)],
    ]
    masuk_tbl = Table(masuk_data, colWidths=[page_w * 0.55, page_w * 0.45])
    masuk_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), _C_GREEN_MED),
        ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [_C_STRIPE, colors.white]),
        ('BACKGROUND',    (0, 3), (-1, 3), _C_GREEN_LIGHT),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#BDBDBD')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(masuk_tbl)
    story.append(Spacer(1, 10))

    # ── PENGELUARAN TAHUNAN ────────────────────────────────────────────────
    story.append(Paragraph("PENGELUARAN TAHUNAN", S['section']))
    story.append(Paragraph(
        "Pengeluaran tahunan ini merupakan pengeluaran yang dibagi pos sesuai "
        "prioritas pengeluaran keuangan.", S['caption']))

    def _pct(t): return Paragraph(t, S['center'])
    def _rpb(v): return Paragraph(f"<b>{format_idr(v)}</b>", S['right'])

    keluar_header = [
        Paragraph("<b>Pos Pengeluaran</b>", S['normal']),
        Paragraph("<b>Persentase</b>", S['normal']),
        Paragraph("<b>Jumlah Tahunan</b>", S['normal']),
        Paragraph("<b>Jumlah Bulanan</b>", S['normal']),
    ]
    keluar_rows = [
        [Paragraph("Pos Zakat", S['normal']),
         _pct("2,5%"), _rp(allocations['zakat']), _rp(allocations['zakat'] / 12)],
        [Paragraph("Pos ISWAF", S['normal']),
         _pct("Maks 7,5%"), _rp(allocations['iswaf']), _rp(allocations['iswaf'] / 12)],
        [Paragraph("<b>Pos Utang</b>", S['normal']),
         _pct("Maks 35%"), _rpb(allocations['utang_total']), _rpb(allocations['utang_total'] / 12)],
        [Paragraph("   \u2514\u2500 a. Utang Produktif", S['normal']),
         _pct("Maks 20%"), _rp(allocations['utang_produktif']), _rp(allocations['utang_produktif'] / 12)],
        [Paragraph("   \u2514\u2500 b. Utang Konsumtif", S['normal']),
         _pct("Maks 15%"), _rp(allocations['utang_konsumtif']), _rp(allocations['utang_konsumtif'] / 12)],
        [Paragraph("Pos Kontribusi Asuransi Syariah", S['normal']),
         _pct("Min 10%"), _rp(allocations['kontribusi_asuransi']), _rp(allocations['kontribusi_asuransi'] / 12)],
        [Paragraph("Pos Dana Masa Depan", S['normal']),
         _pct("Min 10%"), _rp(allocations['dana_masa_depan']), _rp(allocations['dana_masa_depan'] / 12)],
        [Paragraph("Pos Belanja Sekarang", S['normal']),
         _pct("Sisa"), _rp(allocations['belanja_sekarang']), _rp(allocations['belanja_sekarang'] / 12)],
    ]

    cw = [page_w * 0.38, page_w * 0.14, page_w * 0.24, page_w * 0.24]
    keluar_tbl = Table([keluar_header] + keluar_rows, colWidths=cw, repeatRows=1)
    keluar_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), _C_GREEN_MED),
        ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
        ('LINEBELOW',     (0, 0), (-1, 0), 1.5, _C_GREEN_DARK),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [_C_STRIPE, colors.white]),
        # Highlight Pos Utang dan sub-baris
        ('BACKGROUND',    (0, 3), (-1, 3), _C_GREEN_PALE),
        ('BACKGROUND',    (0, 4), (-1, 5), _C_GREEN_PALE),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#BDBDBD')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(keluar_tbl)
    story.append(Spacer(1, 6))

    # ── TOTAL & STATUS ─────────────────────────────────────────────────────
    surplus_defisit = allocations['surplus_defisit']
    status_label = "SURPLUS" if surplus_defisit >= 0 else "DEFISIT"
    status_bg    = _C_GREEN_MED if surplus_defisit >= 0 else _C_RED_DARK

    def _white_bold(t):
        return Paragraph(f"<font color='white'><b>{t}</b></font>", S['right'])

    total_data = [
        [Paragraph("<b>Total Anggaran</b>", S['normal']),
         _rpb(allocations['total_anggaran']),
         _rpb(allocations['total_anggaran'] / 12)],
        [Paragraph(f"<font color='white'><b>Status: {status_label}</b></font>", S['normal']),
         _white_bold(format_idr(abs(surplus_defisit))),
         _white_bold(format_idr(abs(surplus_defisit) / 12))],
    ]
    total_tbl = Table(total_data, colWidths=[page_w * 0.52, page_w * 0.24, page_w * 0.24])
    total_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), _C_GREEN_LIGHT),
        ('BACKGROUND',    (0, 1), (-1, 1), status_bg),
        ('LINEABOVE',     (0, 0), (-1, 0), 1.5, _C_GREEN_DARK),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(total_tbl)
    story.append(Spacer(1, 10))

    # ── REKOMENDASI ────────────────────────────────────────────────────────
    if surplus_defisit < 0:
        rec_text = (
            "<b>PERINGATAN:</b> Anggaran Anda mengalami <b>DEFISIT</b>. "
            "Silakan tinjau kembali pos-pos pengeluaran yang mungkin melebihi persentase "
            "yang disarankan. Pertimbangkan untuk mengurangi pos Belanja Sekarang atau "
            "meningkatkan pemasukan."
        )
        rec_style, rec_bg, rec_border = S['rec_defisit'], _C_RED_LIGHT, _C_RED_DARK
    else:
        rec_text = (
            "<b>SELAMAT:</b> Anggaran Anda mengalami <b>SURPLUS</b>! "
            "Disarankan untuk menambah alokasi pada Pos Dana Masa Depan dalam bentuk "
            "investasi yang <b>AMAN dan MENGUNTUNGKAN</b>. Hindari hanya menabung; "
            "gunakan instrumen investasi seperti reksa dana, obligasi, atau emas untuk "
            "mengoptimalkan dana surplus Anda."
        )
        rec_style, rec_bg, rec_border = S['rec_surplus'], _C_GREEN_LIGHT, _C_GREEN_MED

    rec_tbl = Table([[Paragraph(rec_text, rec_style)]], colWidths=[page_w])
    rec_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), rec_bg),
        ('BOX',           (0, 0), (-1, -1), 1.2, rec_border),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(rec_tbl)
    story.append(Spacer(1, 14))

    # ── FOOTER ─────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=_C_GREEN_MED, spaceAfter=4))
    story.append(Paragraph(
        "AKTA - Anggaran Keuangan Tahunan | "
        "Membantu Anda merencanakan keuangan dengan lebih baik | HumanisGroup",
        S['footer']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Header aplikasi
st.title("💰 AKTA")
st.subheader("Anggaran Keuangan Tahunan")
st.markdown("---")

# Tujuan Aplikasi
st.markdown("### 🎯 Tujuan Aplikasi")
st.write("""
Aplikasi **AKTA (Anggaran Keuangan Tahunan)** dirancang untuk membantu Anda menyusun anggaran keuangan 
pribadi/rumah tangga secara tahunan dengan pendekatan yang sistematis dan berdasarkan prinsip keuangan yang sehat. 
Dengan aplikasi ini, Anda dapat:
- ✅ Mengalokasikan pendapatan secara proporsional sesuai prioritas kebutuhan
- ✅ Mengelola utang dengan bijak (maksimal 35% dari total pemasukan)
- ✅ Membangun dana masa depan melalui investasi
- ✅ Memastikan kewajiban zakat dan sedekah terpenuhi
- ✅ Mendapatkan gambaran jelas pengeluaran bulanan dan tahunan
""")

# Petunjuk Pengisian
with st.expander("📖 **Petunjuk Pengisian** - Klik untuk membaca", expanded=False):
    st.markdown("""
    #### Cara Menggunakan Aplikasi AKTA:
    
    **1. Data Diri**
    - Masukkan **Nama** Anda (akan muncul di laporan PDF)
    - Masukkan **Usia** Anda
    
    **2. Pemasukan Tahunan**
    - **Tetap**: Masukkan total pendapatan tetap per tahun (gaji, tunjangan, dll.)
    - **Tidak Tetap**: Masukkan estimasi pendapatan tidak tetap per tahun (bonus, komisi, freelance, dll.)
    - **Harga Emas**: Masukkan harga per gram emas saat ini (untuk perhitungan nisab zakat)
    
    **3. Klik Tombol "🧮 Hitung Anggaran"**
    
    **4. Hasil Perhitungan**
    
    Aplikasi akan menghitung alokasi anggaran berdasarkan persentase yang disarankan:
    
    | Pos Pengeluaran | Persentase | Keterangan |
    |----------------|------------|------------|
    | **Pos Zakat** | 2.5% | Kewajiban zakat dari total pemasukan |
    | **Pos ISWAF** (Infaq, Sedekah, Wakaf) | Max 7.5% | Kontribusi sosial dan keagamaan |
    | **Pos Utang** | Max 35% | Total cicilan/angsuran (Produktif + Konsumtif) |
    | - Utang Produktif | Max 20% | Utang untuk aset produktif (usaha, properti) |
    | - Utang Konsumtif | Max 15% | Utang untuk konsumsi (KPR, kendaraan) |
    | **Pos Kontribusi Asuransi** | Min 10% | Proteksi kesehatan & jiwa (asuransi syariah) |
    | **Pos Dana Masa Depan** | Min 10% | Investasi & tabungan jangka panjang |
    | **Pos Belanja Sekarang** | Sisa | Kebutuhan sehari-hari & gaya hidup |
    
    **5. Status Anggaran**
    - **SURPLUS**: Anggaran sehat, sisihkan lebih banyak untuk investasi
    - **DEFISIT**: Perlu evaluasi ulang pengeluaran atau tingkatkan pemasukan
    
    **6. Download PDF**
    - Klik tombol "📥 Download PDF" untuk menyimpan laporan lengkap
    
    ---
    
    💡 **Tips**: Pastikan pos utang tidak melebihi 35% agar keuangan tetap sehat dan tidak terbebani cicilan berlebihan.
    """)

st.markdown("---")

# Form input
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 Data Diri")
    name = st.text_input("Nama", placeholder="Masukkan nama Anda")
    age = st.number_input("Usia", min_value=17, max_value=100, value=25, step=1)

with col2:
    st.markdown("### 💵 Pemasukan Tahunan")
    st.caption("Pemasukan lama, apabila ada permasalahan yang tetap dan tidak tetap untuk menjadi acuan "
               "pengeluaran yang ideal")
    
    tetap = st.number_input("Tetap (Rp)", min_value=0, value=250000000, step=1000000, 
                            help="Pemasukan tetap per tahun")
    tidak_tetap = st.number_input("Tidak Tetap (Rp)", min_value=0, value=150000000, step=1000000,
                                  help="Pemasukan tidak tetap per tahun")
    
    total_pemasukan = tetap + tidak_tetap
    st.metric("Total Pemasukan", format_idr(total_pemasukan))
    
    harga_emas = st.number_input("Harga Per Gram Emas Saat Ini (Rp)", min_value=0, value=2800000, 
                                 step=10000, help="Untuk perhitungan zakat")

st.markdown("---")

# Tombol hitung
if st.button("🧮 Hitung Anggaran", type="primary", use_container_width=True):
    if not name:
        st.error("⚠️ Mohon isi nama Anda terlebih dahulu!")
    elif total_pemasukan == 0:
        st.error("⚠️ Total pemasukan tidak boleh nol!")
    else:
        # Hitung alokasi
        allocations = calculate_budget(total_pemasukan)
        
        # Simpan ke session state
        st.session_state['calculated'] = True
        st.session_state['name'] = name
        st.session_state['age'] = age
        st.session_state['tetap'] = tetap
        st.session_state['tidak_tetap'] = tidak_tetap
        st.session_state['total_pemasukan'] = total_pemasukan
        st.session_state['harga_emas'] = harga_emas
        st.session_state['allocations'] = allocations

# Tampilkan hasil jika sudah dihitung
if st.session_state.get('calculated', False):
    allocations = st.session_state['allocations']
    
    st.success("✅ Perhitungan anggaran berhasil!")
    st.markdown("---")
    
    # Hasil perhitungan
    st.markdown("### 📊 Pengeluaran Tahunan")
    st.caption("Pengeluaran tahunan ini merupakan pengeluaran yang dibagi pos sesuai prioritas "
               "pengeluaran keuangan")
    
    # Tabel hasil
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Data untuk tabel
        data = {
            "Pos Pengeluaran": [
                "Pos Zakat",
                "Pos ISWAF",
                "Pos Utang",
                "  └─ a. Utang Produktif",
                "  └─ b. Utang Konsumtif",
                "Pos Kontribusi Asuransi Syariah",
                "Pos Dana Masa Depan",
                "Pos Belanja Sekarang"
            ],
            "Persentase": [
                "(2.5% dari Total Pemasukan)",
                "(Max 7.5% dari Total Pemasukan)",
                "(Max 35% dari Total Pemasukan)",
                "Max (20%)",
                "Max (15%)",
                "min (10%)",
                "min (10%)",
                ""
            ],
            "Jumlah Tahunan": [
                format_idr(allocations['zakat']),
                format_idr(allocations['iswaf']),
                format_idr(allocations['utang_total']),
                format_idr(allocations['utang_produktif']),
                format_idr(allocations['utang_konsumtif']),
                format_idr(allocations['kontribusi_asuransi']),
                format_idr(allocations['dana_masa_depan']),
                format_idr(allocations['belanja_sekarang'])
            ],
            "Jumlah Bulanan": [
                format_idr(allocations['zakat'] / 12),
                format_idr(allocations['iswaf'] / 12),
                format_idr(allocations['utang_total'] / 12),
                format_idr(allocations['utang_produktif'] / 12),
                format_idr(allocations['utang_konsumtif'] / 12),
                format_idr(allocations['kontribusi_asuransi'] / 12),
                format_idr(allocations['dana_masa_depan'] / 12),
                format_idr(allocations['belanja_sekarang'] / 12)
            ]
        }
        
        st.dataframe(data, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 💼 Ringkasan")
        
        # Metrics dalam 2 kolom
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric("Total Tahunan", format_idr(allocations['total_anggaran']))
        
        with metric_col2:
            st.metric("Total Bulanan", format_idr(allocations['total_anggaran'] / 12))
        
        surplus_defisit = allocations['surplus_defisit']
        if surplus_defisit >= 0:
            st.metric("Status", "Surplus", delta=format_idr(surplus_defisit))
        else:
            st.metric("Status", "Defisit", delta=format_idr(surplus_defisit), delta_color="inverse")
    
    st.markdown("---")
    
    # Rekomendasi
    if surplus_defisit < 0:
        st.error(
            "⚠️ **PERINGATAN:** Anggaran Anda mengalami **DEFISIT**. "
            "Silakan tinjau kembali pos-pos pengeluaran yang mungkin melebihi persentase yang disarankan. "
            "Pertimbangkan untuk mengurangi pos Belanja Sekarang atau meningkatkan pemasukan."
        )
    else:
        st.success(
            "✅ **SELAMAT:** Anggaran Anda mengalami **SURPLUS**! "
            "Disarankan untuk menambah alokasi pada Pos Dana Masa Depan dalam bentuk investasi yang "
            "**AMAN dan MENGUNTUNGKAN**. Hindari hanya menabung, gunakan instrumen investasi seperti "
            "reksa dana, obligasi, atau emas untuk mengoptimalkan dana surplus Anda."
        )
    
    st.markdown("---")
    
    # Tombol download PDF
    st.markdown("### 📄 Download Hasil")
    
    pdf_buffer = generate_pdf(
        st.session_state['name'],
        st.session_state['age'],
        st.session_state['tetap'],
        st.session_state['tidak_tetap'],
        st.session_state['total_pemasukan'],
        st.session_state['harga_emas'],
        allocations
    )
    
    st.download_button(
        label="📥 Download PDF",
        data=pdf_buffer,
        file_name=f"AKTA_{st.session_state['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )

# Footer
st.markdown("---")
st.caption("💡 AKTA - Anggaran Keuangan Tahunan | Membantu Anda merencanakan keuangan dengan lebih baik |  HumanisGroup")
