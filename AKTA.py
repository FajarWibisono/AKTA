import streamlit as st
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

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

# Fungsi untuk generate PDF dengan matplotlib
def generate_pdf(name, age, tetap, tidak_tetap, total_pemasukan, harga_emas, allocations):
    buffer = BytesIO()
    
    # Create PDF
    with PdfPages(buffer) as pdf:
        # Page 1
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 size
        fig.patch.set_facecolor('white')
        
        # Title
        plt.text(0.5, 0.95, 'ANGGARAN KEUANGAN TAHUNAN (AKTA)', 
                ha='center', va='top', fontsize=20, fontweight='bold',
                color='#2E7D32')
        
        plt.text(0.5, 0.92, '━' * 50, ha='center', va='top', fontsize=8, color='#2E7D32')
        
        # Data Diri Section
        y_pos = 0.87
        plt.text(0.1, y_pos, 'DATA DIRI', fontsize=14, fontweight='bold', color='#1B5E20')
        y_pos -= 0.03
        
        plt.text(0.12, y_pos, f'Nama:', fontsize=11, fontweight='bold')
        plt.text(0.35, y_pos, name, fontsize=11)
        y_pos -= 0.025
        
        plt.text(0.12, y_pos, f'Usia:', fontsize=11, fontweight='bold')
        plt.text(0.35, y_pos, f'{age} tahun', fontsize=11)
        y_pos -= 0.025
        
        plt.text(0.12, y_pos, f'Tanggal Dibuat:', fontsize=11, fontweight='bold')
        plt.text(0.35, y_pos, datetime.now().strftime("%d %B %Y"), fontsize=11)
        y_pos -= 0.05
        
        # Pemasukan Tahunan Section
        plt.text(0.1, y_pos, 'PEMASUKAN TAHUNAN', fontsize=14, fontweight='bold', color='#1B5E20')
        y_pos -= 0.03
        
        plt.text(0.12, y_pos, 'Tetap:', fontsize=11, fontweight='bold')
        plt.text(0.5, y_pos, format_idr(tetap), fontsize=11, ha='right')
        y_pos -= 0.025
        
        plt.text(0.12, y_pos, 'Tidak Tetap:', fontsize=11, fontweight='bold')
        plt.text(0.5, y_pos, format_idr(tidak_tetap), fontsize=11, ha='right')
        y_pos -= 0.025
        
        plt.text(0.12, y_pos, 'Total Pemasukan:', fontsize=11, fontweight='bold')
        plt.text(0.5, y_pos, format_idr(total_pemasukan), fontsize=11, ha='right', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#C8E6C9', edgecolor='#2E7D32'))
        y_pos -= 0.025
        
        plt.text(0.12, y_pos, 'Harga Per Gram Emas:', fontsize=11, fontweight='bold')
        plt.text(0.5, y_pos, format_idr(harga_emas), fontsize=11, ha='right')
        y_pos -= 0.05
        
        # Pengeluaran Tahunan Section
        plt.text(0.1, y_pos, 'PENGELUARAN TAHUNAN', fontsize=14, fontweight='bold', color='#1B5E20')
        y_pos -= 0.025
        plt.text(0.1, y_pos, 'Pengeluaran tahunan ini merupakan pengeluaran yang dibagi pos sesuai', 
                fontsize=9, style='italic', color='gray')
        y_pos -= 0.02
        plt.text(0.1, y_pos, 'prioritas pengeluaran keuangan', fontsize=9, style='italic', color='gray')
        y_pos -= 0.03
        
        # Header tabel
        rect = mpatches.Rectangle((0.1, y_pos-0.025), 0.8, 0.025, 
                                  linewidth=1, edgecolor='#2E7D32', 
                                  facecolor='#2E7D32')
        fig.add_artist(rect)
        
        plt.text(0.15, y_pos-0.0125, 'Pos Pengeluaran', fontsize=10, 
                fontweight='bold', color='white', va='center')
        plt.text(0.45, y_pos-0.0125, 'Persentase', fontsize=10, 
                fontweight='bold', color='white', va='center', ha='center')
        plt.text(0.85, y_pos-0.0125, 'Jumlah (Rp)', fontsize=10, 
                fontweight='bold', color='white', va='center', ha='right')
        y_pos -= 0.04
        
        # Data rows
        pengeluaran_data = [
            ('Pos Zakat', '(2.5%)', format_idr(allocations['zakat'])),
            ('Pos ISWAF', '(Max 7.5%)', format_idr(allocations['iswaf'])),
            ('Pos Utang', '(Max 35%)', format_idr(allocations['utang_total'])),
            ('  a. Utang Produktif', 'Max (20%)', format_idr(allocations['utang_produktif'])),
            ('  b. Utang Konsumtif', 'Max (15%)', format_idr(allocations['utang_konsumtif'])),
            ('Pos Kontribusi Asuransi', 'min (10%)', format_idr(allocations['kontribusi_asuransi'])),
            ('Pos Dana Masa Depan', 'min (10%)', format_idr(allocations['dana_masa_depan'])),
            ('Pos Belanja Sekarang', '', format_idr(allocations['belanja_sekarang'])),
        ]
        
        for i, (pos, persen, jumlah) in enumerate(pengeluaran_data):
            bg_color = '#F5F5F5' if i % 2 == 0 else 'white'
            if i == 2:  # Highlight Pos Utang
                bg_color = '#E8F5E9'
            
            rect = mpatches.Rectangle((0.1, y_pos-0.022), 0.8, 0.022, 
                                      linewidth=0.5, edgecolor='gray', 
                                      facecolor=bg_color)
            fig.add_artist(rect)
            
            plt.text(0.12, y_pos-0.011, pos, fontsize=9, va='center')
            plt.text(0.45, y_pos-0.011, persen, fontsize=8, va='center', ha='center')
            plt.text(0.88, y_pos-0.011, jumlah, fontsize=9, va='center', ha='right')
            y_pos -= 0.022
        
        y_pos -= 0.02
        
        # Total dan Status
        surplus_defisit = allocations['surplus_defisit']
        status = "Surplus" if surplus_defisit >= 0 else "Defisit"
        status_color = '#2E7D32' if surplus_defisit >= 0 else '#C62828'
        
        # Total Anggaran
        rect = mpatches.Rectangle((0.1, y_pos-0.025), 0.8, 0.025, 
                                  linewidth=1, edgecolor='#2E7D32', 
                                  facecolor='#C8E6C9')
        fig.add_artist(rect)
        plt.text(0.15, y_pos-0.0125, 'Total Anggaran', fontsize=11, 
                fontweight='bold', va='center')
        plt.text(0.85, y_pos-0.0125, format_idr(allocations['total_anggaran']), 
                fontsize=11, fontweight='bold', va='center', ha='right')
        y_pos -= 0.03
        
        # Status
        rect = mpatches.Rectangle((0.1, y_pos-0.025), 0.8, 0.025, 
                                  linewidth=1, edgecolor=status_color, 
                                  facecolor=status_color)
        fig.add_artist(rect)
        plt.text(0.15, y_pos-0.0125, status, fontsize=11, 
                fontweight='bold', color='white', va='center')
        plt.text(0.85, y_pos-0.0125, format_idr(abs(surplus_defisit)), 
                fontsize=11, fontweight='bold', color='white', va='center', ha='right')
        y_pos -= 0.04
        
        # Rekomendasi
        if surplus_defisit < 0:
            recommendation_text = (
                "⚠️ PERINGATAN: Anggaran Anda mengalami DEFISIT. "
                "Silakan tinjau kembali pos-pos pengeluaran yang mungkin melebihi "
                "persentase yang disarankan. Pertimbangkan untuk mengurangi pos "
                "Belanja Sekarang atau meningkatkan pemasukan."
            )
            box_color = '#FFCDD2'
            text_color = '#C62828'
        else:
            recommendation_text = (
                "✓ SELAMAT: Anggaran Anda mengalami SURPLUS! "
                "Disarankan untuk menambah alokasi pada Pos Dana Masa Depan dalam "
                "bentuk investasi yang AMAN dan MENGUNTUNGKAN. Hindari hanya menabung, "
                "gunakan instrumen investasi seperti reksa dana, obligasi, atau emas "
                "untuk mengoptimalkan dana surplus Anda."
            )
            box_color = '#C8E6C9'
            text_color = '#2E7D32'
        
        # Wrap text
        words = recommendation_text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 70:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        box_height = len(lines) * 0.018 + 0.02
        rect = mpatches.Rectangle((0.1, y_pos-box_height), 0.8, box_height, 
                                  linewidth=1, edgecolor=text_color, 
                                  facecolor=box_color, alpha=0.3)
        fig.add_artist(rect)
        
        for i, line in enumerate(lines):
            plt.text(0.12, y_pos - 0.015 - (i * 0.018), line, 
                    fontsize=9, color=text_color, va='top')
        
        # Footer
        plt.text(0.5, 0.02, '💡 AKTA - Anggaran Keuangan Tahunan', 
                ha='center', fontsize=9, style='italic', color='gray')
        plt.text(0.5, 0.01, 'Membantu Anda merencanakan keuangan dengan lebih baik', 
                ha='center', fontsize=8, style='italic', color='gray')
        
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.axis('off')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
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
st.caption("💡 AKTA - Anggaran Keuangan Tahunan | Membantu Anda merencanakan keuangan dengan lebih baik")