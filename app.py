import streamlit as st
import pandas as pd
import qrcode
import os
from io import BytesIO
from datetime import datetime
import urllib.parse

# =========================
# AL-FALAH DIGITAL V1
# =========================

NAMA_MASJID = "Masjid Jami Al-Falah"
ALAMAT_MASJID = "Kp Caringin RT 005 / RW 005, Desa Sukasari, Kec. Karangtengah, Kab. Cianjur"
KETUA_DKM = "Aang Deden Kasyful Anwar"
BENDAHARA = "Aceng Abdul Roup"

WA_AANG_DEDEN = "6285722090778"
WA_USTADZ_IHIN = "6287799541295"

REK_BCA = "1831149782"
DANA = "081395440454"

KAS_FILE = "kas_masjid.csv"
ADMIN_PASSWORD = "alfalah123"


# =========================
# FUNGSI
# =========================

def format_rupiah(angka):
    try:
        return "Rp {:,.0f}".format(float(angka)).replace(",", ".")
    except:
        return "Rp 0"


def baca_kas():
    if os.path.exists(KAS_FILE):
        return pd.read_csv(KAS_FILE)

    return pd.DataFrame(columns=[
        "tanggal",
        "jenis",
        "kategori",
        "keterangan",
        "jumlah"
    ])


def simpan_transaksi(jenis, kategori, keterangan, jumlah):
    data = baca_kas()

    transaksi_baru = pd.DataFrame([{
        "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "jenis": jenis,
        "kategori": kategori,
        "keterangan": keterangan,
        "jumlah": jumlah
    }])

    data = pd.concat([data, transaksi_baru], ignore_index=True)
    data.to_csv(KAS_FILE, index=False)


def hitung_saldo():
    data = baca_kas()

    if data.empty:
        return 0, 0, 0

    pemasukan = data[data["jenis"] == "Pemasukan"]["jumlah"].sum()
    pengeluaran = data[data["jenis"] == "Pengeluaran"]["jumlah"].sum()
    saldo = pemasukan - pengeluaran

    return pemasukan, pengeluaran, saldo


def link_wa(nomor, pesan):
    pesan_encode = urllib.parse.quote(pesan)
    return f"https://wa.me/{nomor}?text={pesan_encode}"


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
# SETUP HALAMAN
# =========================

st.set_page_config(
    page_title="Al-Falah Digital",
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
    font-weight: 600;
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
label, .stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label {
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
</style>
""", unsafe_allow_html=True)


# =========================
# HEADER
# =========================

st.markdown('<div class="main-title">🕌 AL-FALAH DIGITAL</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{NAMA_MASJID}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{ALAMAT_MASJID}</div>', unsafe_allow_html=True)

st.divider()

pemasukan, pengeluaran, saldo = hitung_saldo()

col1, col2, col3 = st.columns(3)
col1.metric("Pemasukan", format_rupiah(pemasukan))
col2.metric("Pengeluaran", format_rupiah(pengeluaran))
col3.metric("Saldo Kas", format_rupiah(saldo))

st.divider()


# =========================
# MENU UTAMA
# =========================

menu = st.radio(
    "Menu Al-Falah Digital",
    [
        "🏠 Beranda",
        "💰 Laporan Kas",
        "💚 Sedekah",
        "📖 Jadwal Pengajian",
        "🌙 Syahriahan Sholawat",
        "🔐 Admin Bendahara"
    ],
    horizontal=False
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

    st.markdown("## 📌 Fitur")
    st.markdown("""
    <div class="info-card">✅ Laporan kas masjid transparan</div>
    <div class="info-card">✅ Informasi sedekah dan infaq</div>
    <div class="info-card">✅ Jadwal pengajian mingguan</div>
    <div class="info-card">✅ Informasi syahriahan sholawat</div>
    <div class="info-card">✅ Admin bendahara untuk input kas</div>
    """, unsafe_allow_html=True)


# =========================
# LAPORAN KAS
# =========================

elif menu == "💰 Laporan Kas":
    st.markdown("## 💰 Laporan Kas Masjid")

    pemasukan, pengeluaran, saldo = hitung_saldo()

    st.markdown(f"""
    <div class="card">
        <h3>Saldo Kas Saat Ini</h3>
        <h2>{format_rupiah(saldo)}</h2>
        <p>Total Pemasukan: {format_rupiah(pemasukan)}</p>
        <p>Total Pengeluaran: {format_rupiah(pengeluaran)}</p>
    </div>
    """, unsafe_allow_html=True)

    data = baca_kas()

    if data.empty:
        st.info("Belum ada transaksi kas.")
    else:
        data_tampil = data.copy()
        data_tampil["jumlah"] = data_tampil["jumlah"].apply(format_rupiah)
        st.dataframe(data_tampil, use_container_width=True)


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

        <hr>

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

        <p>
        Semoga Allah SWT membalas setiap kebaikan dan sedekah yang diberikan
        dengan pahala yang berlipat ganda. Aamiin Ya Rabbal 'Alamiin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    pesan = f"Assalamualaikum, saya ingin konfirmasi sedekah untuk {NAMA_MASJID}."
    st.link_button(
        "📱 Konfirmasi Sedekah ke Bendahara",
        link_wa("6281395440454", pesan),
        use_container_width=True
    )


# =========================
# JADWAL PENGAJIAN
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

    pesan_aang = "Assalamualaikum Aang Deden, mengingatkan jadwal pengajian di Madrasah Al-Falah."
    pesan_ihin = "Assalamualaikum Ustadz Ihin, mengingatkan jadwal pengajian di Madrasah Al-Falah."

    st.link_button(
        "📱 Hubungi Aang Deden",
        link_wa(WA_AANG_DEDEN, pesan_aang),
        use_container_width=True
    )

    st.link_button(
        "📱 Hubungi Ustadz Ihin",
        link_wa(WA_USTADZ_IHIN, pesan_ihin),
        use_container_width=True
    )


# =========================
# SYAHRIAHAN
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

        tab1, tab2, tab3 = st.tabs(["➕ Pemasukan", "➖ Pengeluaran", "📊 Data Kas"])

        with tab1:
            st.markdown("### ➕ Input Pemasukan")

            kategori = st.selectbox(
                "Kategori Pemasukan",
                [
                    "Infaq Jumat",
                    "Sedekah Jamaah",
                    "Donasi Pembangunan",
                    "Kotak Amal",
                    "Lainnya"
                ]
            )

            keterangan = st.text_area("Keterangan Pemasukan")
            jumlah = st.number_input("Jumlah Pemasukan", min_value=0, step=1000)

            if st.button("💾 Simpan Pemasukan"):
                if jumlah <= 0:
                    st.warning("Jumlah harus lebih dari 0.")
                else:
                    simpan_transaksi("Pemasukan", kategori, keterangan, jumlah)
                    st.success("Pemasukan berhasil disimpan.")
                    st.rerun()

        with tab2:
            st.markdown("### ➖ Input Pengeluaran")

            kategori = st.selectbox(
                "Kategori Pengeluaran",
                [
                    "Operasional Masjid",
                    "Listrik / Air",
                    "Kebersihan",
                    "Kegiatan Keagamaan",
                    "Pembangunan",
                    "Lainnya"
                ]
            )

            keterangan = st.text_area("Keterangan Pengeluaran")
            jumlah = st.number_input("Jumlah Pengeluaran", min_value=0, step=1000)

            if st.button("💾 Simpan Pengeluaran"):
                if jumlah <= 0:
                    st.warning("Jumlah harus lebih dari 0.")
                else:
                    simpan_transaksi("Pengeluaran", kategori, keterangan, jumlah)
                    st.success("Pengeluaran berhasil disimpan.")
                    st.rerun()

        with tab3:
            st.markdown("### 📊 Data Kas")
            data = baca_kas()

            if data.empty:
                st.info("Belum ada data kas.")
            else:
                st.dataframe(data, use_container_width=True)

                csv = data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Laporan CSV",
                    data=csv,
                    file_name="laporan_kas_alfalah.csv",
                    mime="text/csv"
                )

    elif password:
        st.error("Password salah.")


st.divider()
st.caption("Al-Falah Digital | Masjid Jami Al-Falah | Transparansi, Amanah, dan Kemakmuran Masjid")
