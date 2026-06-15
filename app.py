import streamlit as st
import pandas as pd
import qrcode
import os
from io import BytesIO
from datetime import datetime
import urllib.parse

# =========================
# AL-FALAH DIGITAL V3
# =========================

NAMA_MASJID = "Masjid Jami Al-Falah"
ALAMAT_MASJID = "Kp Caringin RT 005 / RW 005, Desa Sukasari, Kec. Karangtengah, Kab. Cianjur"
KETUA_DKM = "Aang Deden Kasyful Anwar"
BENDAHARA = "Aceng Abdul Roup"

WA_BENDAHARA = "6281395440454"
WA_AANG_DEDEN = "6285722090778"
WA_USTADZ_IHIN = "6287799541295"

REK_BCA = "1831149782"
DANA = "081395440454"

ADMIN_PASSWORD = "alfalah123"
KAS_FILE = "kas_masjid.csv"

SALDO_AWAL = 8383500


# =========================
# FUNGSI
# =========================

def format_rupiah(angka):
    try:
        return "Rp {:,.0f}".format(float(angka)).replace(",", ".")
    except Exception:
        return "Rp 0"


def data_awal():
    return pd.DataFrame([{
        "tanggal": "30-06-2026",
        "bulan": "Juni 2026",
        "jenis": "Pemasukan",
        "kategori": "Kotak Amal",
        "keterangan": "Pembukaan kotak amal",
        "jumlah": 942500
    }])


def baca_kas():
    kolom = ["tanggal", "bulan", "jenis", "kategori", "keterangan", "jumlah"]

    if os.path.exists(KAS_FILE):
        data = pd.read_csv(KAS_FILE)

        for k in kolom:
            if k not in data.columns:
                data[k] = "-"

        data["jumlah"] = pd.to_numeric(data["jumlah"], errors="coerce").fillna(0)
        return data[kolom]

    data = data_awal()
    data.to_csv(KAS_FILE, index=False)
    return data


def simpan_transaksi(tanggal, bulan, jenis, kategori, keterangan, jumlah):
    data = baca_kas()

    baru = pd.DataFrame([{
        "tanggal": tanggal,
        "bulan": bulan,
        "jenis": jenis,
        "kategori": kategori,
        "keterangan": keterangan,
        "jumlah": jumlah
    }])

    data = pd.concat([data, baru], ignore_index=True)
    data.to_csv(KAS_FILE, index=False)


def hitung_kas():
    data = baca_kas()

    pemasukan = data[data["jenis"] == "Pemasukan"]["jumlah"].sum()
    pengeluaran = data[data["jenis"] == "Pengeluaran"]["jumlah"].sum()
    saldo = SALDO_AWAL + pemasukan - pengeluaran

    return pemasukan, pengeluaran, saldo


def link_wa(nomor, pesan):
    return f"https://wa.me/{nomor}?text={urllib.parse.quote(pesan)}"


def buat_qr(link):
    qr = qrcode.QRCode(version=2, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# =========================
# HALAMAN
# =========================

st.set_page_config(
    page_title="Al-Falah Digital V3",
    page_icon="🕌",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #002b1a, #00150d);
    color: white;
}
.main-title {
    text-align: center;
    color: #ffd700;
    font-size: 42px;
    font-weight: 900;
}
.sub-title {
    text-align: center;
    color: white;
    font-size: 18px;
    font-weight: 700;
}
.card {
    background-color: #063b25;
    padding: 20px;
    border-radius: 18px;
    border: 2px solid #ffd700;
    margin-bottom: 18px;
}
.green-card {
    background-color: #0b5c38;
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 14px;
    border: 1px solid #ffd700;
}
.info-card {
    background-color: #09301f;
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 12px;
}
.warning-card {
    background-color: #3b2f00;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid #ffd700;
    margin-bottom: 12px;
}
label, .stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label, .stDateInput label {
    color: white !important;
    font-weight: bold !important;
}
input, textarea, select {
    color: black !important;
    background-color: white !important;
}
div.stButton > button {
    width: 100%;
    background-color: #0fbf63;
    color: white;
    font-size: 20px;
    font-weight: 900;
    border-radius: 14px;
    border: none;
    padding: 14px;
}
div.stDownloadButton > button {
    width: 100%;
    background-color: #ffd700;
    color: black;
    font-size: 18px;
    font-weight: 900;
    border-radius: 12px;
    border: none;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown('<div class="main-title">🕌 AL-FALAH DIGITAL</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{NAMA_MASJID}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{ALAMAT_MASJID}</div>', unsafe_allow_html=True)

st.divider()

pemasukan, pengeluaran, saldo = hitung_kas()

col1, col2, col3 = st.columns(3)
col1.metric("Pemasukan", format_rupiah(pemasukan))
col2.metric("Pengeluaran", format_rupiah(pengeluaran))
col3.metric("Saldo Kas", format_rupiah(saldo))

st.caption(f"Saldo awal sebelum pembukaan kotak amal: {format_rupiah(SALDO_AWAL)}")

st.divider()

menu = st.radio(
    "Menu Al-Falah Digital",
    [
        "🏠 Beranda",
        "💰 Laporan Kas",
        "💚 Sedekah",
        "📖 Jadwal Pengajian",
        "🌙 Syahriahan Sholawat",
        "🔐 Admin Bendahara"
    ]
)

# =========================
# BERANDA
# =========================

if menu == "🏠 Beranda":
    st.markdown("## 🏠 Beranda")

    st.markdown(f"""
    <div class="card">
        <h3>{NAMA_MASJID}</h3>
        <p>{ALAMAT_MASJID}</p>
        <p><b>Ketua DKM:</b> {KETUA_DKM}</p>
        <p><b>Bendahara:</b> {BENDAHARA}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Ringkasan Kas")
    st.markdown(f"""
    <div class="green-card">
        <h3>Saldo Kas Saat Ini</h3>
        <h1>{format_rupiah(saldo)}</h1>
        <p>Total Pemasukan: {format_rupiah(pemasukan)}</p>
        <p>Total Pengeluaran: {format_rupiah(pengeluaran)}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📌 Fitur")
    st.markdown("""
    <div class="info-card">✅ Laporan kas masjid transparan</div>
    <div class="info-card">✅ Input pemasukan dan pengeluaran bulanan</div>
    <div class="info-card">✅ Informasi sedekah dan infaq</div>
    <div class="info-card">✅ Jadwal pengajian mingguan</div>
    <div class="info-card">✅ Informasi syahriahan sholawat</div>
    """, unsafe_allow_html=True)


# =========================
# LAPORAN KAS
# =========================

elif menu == "💰 Laporan Kas":
    st.markdown("## 💰 Laporan Kas Masjid")

    data = baca_kas()

    bulan_list = ["Semua"] + sorted(data["bulan"].dropna().unique().tolist())
    pilih_bulan = st.selectbox("Pilih Bulan", bulan_list)

    if pilih_bulan != "Semua":
        data_tampil = data[data["bulan"] == pilih_bulan].copy()
    else:
        data_tampil = data.copy()

    total_masuk = data_tampil[data_tampil["jenis"] == "Pemasukan"]["jumlah"].sum()
    total_keluar = data_tampil[data_tampil["jenis"] == "Pengeluaran"]["jumlah"].sum()

    c1, c2 = st.columns(2)
    c1.metric("Pemasukan Terpilih", format_rupiah(total_masuk))
    c2.metric("Pengeluaran Terpilih", format_rupiah(total_keluar))

    if data_tampil.empty:
        st.info("Belum ada transaksi.")
    else:
        data_view = data_tampil.copy()
        data_view["jumlah"] = data_view["jumlah"].apply(format_rupiah)
        st.dataframe(data_view, use_container_width=True)

        csv = data_tampil.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Laporan CSV",
            data=csv,
            file_name="laporan_kas_alfalah.csv",
            mime="text/csv"
        )


# =========================
# SEDEKAH
# =========================

elif menu == "💚 Sedekah":
    st.markdown("## 💚 Sedekah Masjid Jami Al-Falah")

    st.markdown(f"""
    <div class="card">
        <p>
        Bagi jamaah yang ingin berpartisipasi dalam pembangunan, operasional,
        kegiatan keagamaan, dan kemakmuran Masjid Jami Al-Falah, dapat menyalurkan
        infak, sedekah, dan donasi melalui:
        </p>

        <h3>🏦 Bank BCA</h3>
        <h2>{REK_BCA}</h2>
        <p>a.n. {BENDAHARA}</p>

        <h3>📱 DANA</h3>
        <h2>{DANA}</h2>
        <p>a.n. {BENDAHARA}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-card">
        <p>
        Karena saat ini Masjid Jami Al-Falah belum memiliki rekening resmi atas nama masjid,
        maka untuk sementara donasi dititipkan melalui rekening Bendahara DKM.
        </p>
        <p>
        Seluruh dana yang masuk akan dicatat, dilaporkan secara terbuka,
        dan dipergunakan untuk kepentingan Masjid Jami Al-Falah.
        </p>
        <p>
        Penerimaan dan penggunaan dana menjadi tanggung jawab Bendahara DKM,
        diketahui dan diawasi oleh Ketua DKM serta seluruh jajaran pengurus DKM.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pesan = f"Assalamualaikum, saya ingin konfirmasi sedekah untuk {NAMA_MASJID}."
    st.link_button(
        "📱 Konfirmasi Sedekah ke Bendahara",
        link_wa(WA_BENDAHARA, pesan),
        use_container_width=True
    )


# =========================
# JADWAL
# =========================

elif menu == "📖 Jadwal Pengajian":
    st.markdown("## 📖 Jadwal Pengajian")

    st.markdown("""
    <div class="green-card">
        <h3>📖 Pengajian Laki-Laki</h3>
        <p><b>Tempat:</b> Madrasah Al-Falah</p>
        <p><b>Waktu:</b> Selasa malam Rabu</p>
        <p><b>Jam:</b> 19.30 - 21.30 WIB</p>
        <p><b>Penceramah:</b> Aang Deden, Ustadz Ihin, Ustadz Nanang, Ustadz Jujun</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="green-card">
        <h3>👩 Pengajian Ibu-Ibu</h3>
        <p><b>Tempat:</b> Madrasah Al-Falah</p>
        <p><b>Waktu:</b> Senin pagi</p>
        <p><b>Jam:</b> 07.30 - 09.00 WIB</p>
        <p><b>Minggu ke-1:</b> Aang Deden Kasyful Anwar</p>
        <p><b>Minggu ke-2:</b> Ustadz Ihin</p>
        <p><b>Minggu ke-3:</b> Ustadz Ihin</p>
        <p><b>Minggu ke-4:</b> Ustadz Nanang</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📱 Hubungi Penceramah")
    st.link_button(
        "📱 Hubungi Aang Deden",
        link_wa(WA_AANG_DEDEN, "Assalamualaikum Aang Deden, mengingatkan jadwal pengajian di Madrasah Al-Falah."),
        use_container_width=True
    )
    st.link_button(
        "📱 Hubungi Ustadz Ihin",
        link_wa(WA_USTADZ_IHIN, "Assalamualaikum Ustadz Ihin, mengingatkan jadwal pengajian di Madrasah Al-Falah."),
        use_container_width=True
    )


# =========================
# SHOLAWAT
# =========================

elif menu == "🌙 Syahriahan Sholawat":
    st.markdown("## 🌙 Syahriahan Sholawat")

    st.markdown(f"""
    <div class="card">
        <h3>Syahriahan Sholawat Masjid Jami Al-Falah</h3>
        <p><b>Tempat:</b> {NAMA_MASJID}</p>
        <p><b>Waktu:</b> Malam Jumat awal bulan Hijriah</p>
        <p>
        Kegiatan syahriahan sholawat dilaksanakan sebagai bentuk ikhtiar
        mempererat ukhuwah, memperbanyak sholawat, dan memakmurkan masjid.
        </p>
    </div>
    """, unsafe_allow_html=True)


# =========================
# ADMIN
# =========================

elif menu == "🔐 Admin Bendahara":
    st.markdown("## 🔐 Admin Bendahara")

    password = st.text_input("Masukkan Password Admin", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Login admin berhasil.")

        tab1, tab2, tab3 = st.tabs(["➕ Input Kas", "📊 Data Kas", "⚙️ Info"])

        with tab1:
            st.markdown("### ➕ Input Transaksi Kas")

            tanggal_input = st.date_input("Tanggal Transaksi")
            bulan = st.text_input("Bulan Laporan", value=datetime.now().strftime("%B %Y"))

            jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])

            kategori = st.selectbox(
                "Kategori",
                [
                    "Kotak Amal",
                    "Infaq Jumat",
                    "Sedekah Jamaah",
                    "Donasi Pembangunan",
                    "Operasional Masjid",
                    "Listrik / Air",
                    "Kebersihan",
                    "Kegiatan Keagamaan",
                    "Pembangunan",
                    "Lainnya"
                ]
            )

            keterangan = st.text_area("Keterangan")
            jumlah = st.number_input("Jumlah", min_value=0, step=500)

            if st.button("💾 SIMPAN TRANSAKSI"):
                if jumlah <= 0:
                    st.warning("Jumlah harus lebih dari 0.")
                else:
                    tanggal = tanggal_input.strftime("%d-%m-%Y")
                    simpan_transaksi(tanggal, bulan, jenis, kategori, keterangan, jumlah)
                    st.success("Transaksi berhasil disimpan.")
                    st.rerun()

        with tab2:
            st.markdown("### 📊 Data Kas")
            data = baca_kas()

            if data.empty:
                st.info("Belum ada data kas.")
            else:
                st.dataframe(data, use_container_width=True)

                csv = data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Semua Data Kas",
                    data=csv,
                    file_name="data_kas_masjid_alfalah.csv",
                    mime="text/csv"
                )

        with tab3:
            st.info(f"Saldo awal sistem: {format_rupiah(SALDO_AWAL)}")
            st.info("Password admin saat ini: alfalah123")

    elif password:
        st.error("Password salah.")


st.divider()
st.caption("Al-Falah Digital V3 | Masjid Jami Al-Falah | Transparansi, Amanah, dan Kemakmuran Masjid")
