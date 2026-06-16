import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# =========================
# AL-FALAH DIGITAL V12
# =========================

NAMA_MASJID = "Masjid Jami Al-Falah"
ALAMAT_MASJID = "Kp Caringin RT 005 / RW 005, Desa Sukasari, Kec. Karangtengah, Kab. Cianjur"

KETUA_DKM = "Aang Deden Kasyful Anwar"
WAKIL_KETUA = "Iden Tazuni"
BENDAHARA = "Aceng Abdul Roup"

LINK_APP = "https://kas-masjid-alfalah.streamlit.app"
GRUP_AL_BARZAJI = "https://chat.whatsapp.com/JWobEDYP9MXEfDYHt8zlLR"

KAS_FILE = "kas_masjid.csv"
JAMAAH_FILE = "jamaah.csv"

ADMIN_PASSWORD = "alfalah123"

SALDO_AWAL = 7080000

# =========================
# DATA AWAL
# =========================

DATA_KAS_AWAL = [
    ["01-05-2026", "Mei 2026", "Pemasukan", "Saldo Awal", "Serah terima dari bendahara lama", 7080000],
    ["15-05-2026", "Mei 2026", "Pemasukan", "Kotak Amal", "Setoran kotak amal diterima bendahara", 1661500],
    ["31-05-2026", "Mei 2026", "Pemasukan", "Kotak Amal", "Pembukaan kotak amal", 942500],
    ["01-06-2026", "Juni 2026", "Pengeluaran", "Perlengkapan", "White board 2 buah dan spidol", 358000],
]

DATA_JAMAAH_AWAL = [
    ["Usep", "Laki-laki", "6285871353759", "Ya", "-"],
    ["Elan", "Laki-laki", "6281916018461", "Ya", "-"],
    ["Joni", "Laki-laki", "628562287257", "Ya", "-"],
    ["Aang Kipl", "Laki-laki", "6285722764887", "Ya", "-"],
    ["Ustadz Ihin", "Laki-laki", "6287799541295", "Ya", "-"],
    ["Mang Ade Jiban", "Laki-laki", "6285927979070", "Ya", "-"],
    ["Dede Ro'i", "Laki-laki", "6281912607968", "Ya", "-"],
    ["Yudi", "Laki-laki", "6287708449234", "Ya", "-"],
    ["Amoy", "Perempuan", "6285794505300", "Ya", "-"],
    ["Zuri", "Perempuan", "6285220812225", "Ya", "-"],
    ["Mang Emon", "Laki-laki", "6283893804659", "Ya", "-"],
    ["Wawan", "Laki-laki", "6283113138008", "Ya", "-"],
    ["Hj. Uus", "Perempuan", "6283869494725", "Ya", "-"],
    ["Hanah", "Perempuan", "6287875612116", "Ya", "-"],
    ["Th. Ai Warung", "Perempuan", "6281911421598", "Ya", "-"],
    ["Th. Ai", "Perempuan", "6285603226828", "Ya", "-"],
    ["Neng", "Perempuan", "6283833418940", "Ya", "-"],
    ["Aang Deden", "Laki-laki", "6285722090778", "Khusus", "Hanya jika beliau pengisi acara"],
]

# =========================
# FUNGSI
# =========================

def format_rupiah(angka):
    return "Rp {:,.0f}".format(float(angka)).replace(",", ".")


def normalisasi_wa(nomor):
    nomor = str(nomor).replace("+", "").replace("-", "").replace(" ", "")
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    return nomor


def link_wa(nomor, pesan):
    nomor = normalisasi_wa(nomor)
    return f"https://wa.me/{nomor}?text={urllib.parse.quote(pesan)}"


def init_kas():
    if not os.path.exists(KAS_FILE):
        df = pd.DataFrame(
            DATA_KAS_AWAL,
            columns=["tanggal", "bulan", "jenis", "kategori", "keterangan", "jumlah"]
        )
        df.to_csv(KAS_FILE, index=False)


def init_jamaah():
    if not os.path.exists(JAMAAH_FILE):
        df = pd.DataFrame(
            DATA_JAMAAH_AWAL,
            columns=["Nama", "JenisKelamin", "NoWA", "Aktif", "Catatan"]
        )
        df.to_csv(JAMAAH_FILE, index=False)


def baca_kas():
    init_kas()

    df = pd.read_csv(KAS_FILE)

    # Ubah semua nama kolom menjadi huruf kecil
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Pastikan kolom jumlah ada
    if "jumlah" not in df.columns:

        if "Jumlah" in df.columns:
            df.rename(columns={"Jumlah": "jumlah"}, inplace=True)

        elif "JUMLAH" in df.columns:
            df.rename(columns={"JUMLAH": "jumlah"}, inplace=True)

        else:
            df["jumlah"] = 0

    df["jumlah"] = pd.to_numeric(
        df["jumlah"],
        errors="coerce"
    ).fillna(0)

    return df

def baca_jamaah():
    init_jamaah()
    df = pd.read_csv(JAMAAH_FILE, dtype=str).fillna("-")
    return df


def simpan_transaksi(tanggal, bulan, jenis, kategori, keterangan, jumlah):
    df = baca_kas()
    baru = pd.DataFrame([{
        "tanggal": tanggal,
        "bulan": bulan,
        "jenis": jenis,
        "kategori": kategori,
        "keterangan": keterangan,
        "jumlah": jumlah
    }])
    df = pd.concat([df, baru], ignore_index=True)
    df.to_csv(KAS_FILE, index=False)


def hitung_kas():
    df = baca_kas()
    pemasukan = df[df["jenis"] == "Pemasukan"]["jumlah"].sum()
    pengeluaran = df[df["jenis"] == "Pengeluaran"]["jumlah"].sum()
    saldo = pemasukan - pengeluaran
    kotak_amal = df[df["kategori"] == "Kotak Amal"]["jumlah"].sum()
    return pemasukan, pengeluaran, saldo, kotak_amal


def buat_pesan_senenan(pengisi):
    return f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Besok seperti biasa akan dilaksanakan Pengajian Senenan di Madrasah Al-Falah pada pukul 07.30 WIB.

👳 Pengisi:
{pengisi}

📍 Tempat:
Madrasah Al-Falah

👥 Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih kepada jamaah yang hadir tepat waktu.

Pesan ini dikirim otomatis melalui Al-Falah Digital."""


def buat_pesan_malam_rabu(pengisi):
    return f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Malam ini akan dilaksanakan Pengajian Malam Rabu di Madrasah Al-Falah pada pukul 19.30 WIB.

👳 Pengisi:
{pengisi}

📍 Tempat:
Madrasah Al-Falah

👥 Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih kepada jamaah yang hadir tepat waktu.

Pesan ini dikirim otomatis melalui Al-Falah Digital."""


def buat_pesan_syahriahan():
    return f"""Assalamu'alaikum Warahmatullahi Wabarakatuh.

Malam ini akan dilaksanakan Syahriahan Sholawat di Masjid Jami Al-Falah.

👳 Pimpinan:
Aang Deden Kasyful Anwar

📍 Tempat:
Masjid Jami Al-Falah

👥 Grup Jamaah AL-BARZAJI:
{GRUP_AL_BARZAJI}

🌐 Informasi jadwal dan pengumuman terbaru:
{LINK_APP}

Terima kasih atas partisipasi seluruh jamaah.

Pesan ini dikirim otomatis melalui Al-Falah Digital."""


# =========================
# TAMPILAN
# =========================

st.set_page_config(
    page_title="Al-Falah Digital V12",
    page_icon="🕌",
    layout="wide"
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
    font-size: 44px;
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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🕌 AL-FALAH DIGITAL</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{NAMA_MASJID}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{ALAMAT_MASJID}</div>', unsafe_allow_html=True)

st.divider()

pemasukan, pengeluaran, saldo, kotak_amal = hitung_kas()
jamaah_df = baca_jamaah()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Saldo Kas", format_rupiah(saldo))
c2.metric("Pemasukan", format_rupiah(pemasukan))
c3.metric("Pengeluaran", format_rupiah(pengeluaran))
c4.metric("Kotak Amal", format_rupiah(kotak_amal))

st.divider()

menu = st.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "💰 Laporan Kas",
        "💚 Sedekah",
        "📖 Jadwal Pengajian",
        "👥 Data Jamaah",
        "📢 Share WhatsApp",
        "🔐 Admin Bendahara"
    ],
    horizontal=True
)

# =========================
# DASHBOARD
# =========================

if menu == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard Masjid")

    st.markdown(f"""
    <div class="card">
        <h3>{NAMA_MASJID}</h3>
        <p>{ALAMAT_MASJID}</p>
        <p><b>Ketua DKM:</b> {KETUA_DKM}</p>
        <p><b>Wakil Ketua:</b> {WAKIL_KETUA}</p>
        <p><b>Bendahara:</b> {BENDAHARA}</p>
    </div>
    """, unsafe_allow_html=True)

    j1, j2, j3 = st.columns(3)
    j1.metric("Total Jamaah", len(jamaah_df))
    j2.metric("Laki-laki", len(jamaah_df[jamaah_df["JenisKelamin"] == "Laki-laki"]))
    j3.metric("Perempuan", len(jamaah_df[jamaah_df["JenisKelamin"] == "Perempuan"]))

    st.markdown("## 📌 Agenda Tetap")
    st.markdown("""
    <div class="info-card">📖 Pengajian Senenan - Senin 07.30 WIB - Madrasah Al-Falah</div>
    <div class="info-card">📖 Pengajian Malam Rabu - Selasa 19.30 WIB - Madrasah Al-Falah</div>
    <div class="info-card">🌙 Syahriahan Sholawat - Malam Jumat awal bulan Hijriah - Masjid Al-Falah</div>
    """, unsafe_allow_html=True)

# =========================
# LAPORAN KAS
# =========================

elif menu == "💰 Laporan Kas":
    st.markdown("## 💰 Laporan Kas Masjid")
    df = baca_kas()

    bulan_list = ["Semua"] + sorted(df["bulan"].dropna().unique().tolist())
    pilih_bulan = st.selectbox("Pilih Bulan", bulan_list)

    if pilih_bulan != "Semua":
        tampil = df[df["bulan"] == pilih_bulan].copy()
    else:
        tampil = df.copy()

    total_masuk = tampil[tampil["jenis"] == "Pemasukan"]["jumlah"].sum()
    total_keluar = tampil[tampil["jenis"] == "Pengeluaran"]["jumlah"].sum()

    k1, k2 = st.columns(2)
    k1.metric("Pemasukan Terpilih", format_rupiah(total_masuk))
    k2.metric("Pengeluaran Terpilih", format_rupiah(total_keluar))

    view = tampil.copy()
    view["jumlah"] = view["jumlah"].apply(format_rupiah)
    st.dataframe(view, use_container_width=True)

    csv = tampil.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Laporan CSV", csv, "laporan_kas_alfalah.csv", "text/csv")

# =========================
# SEDEKAH
# =========================

elif menu == "💚 Sedekah":
    st.markdown("## 💚 Sedekah Masjid Jami Al-Falah")

    st.markdown(f"""
    <div class="card">
        <p>Bagi jamaah yang ingin menyalurkan infak, sedekah, dan donasi untuk Masjid Jami Al-Falah:</p>
        <h3>🏦 Bank BCA</h3>
        <h2>1831149782</h2>
        <p>a.n. Aceng Abdul Roup</p>
        <h3>📱 DANA</h3>
        <h2>081395440454</h2>
        <p>a.n. Aceng Abdul Roup</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-card">
    Karena saat ini Masjid Jami Al-Falah belum memiliki rekening resmi atas nama masjid,
    maka untuk sementara donasi dititipkan melalui rekening Bendahara DKM.
    Seluruh dana akan dicatat, dilaporkan secara terbuka, dan digunakan untuk kepentingan masjid.
    </div>
    """, unsafe_allow_html=True)

# =========================
# JADWAL
# =========================

elif menu == "📖 Jadwal Pengajian":
    st.markdown("## 📖 Jadwal Pengajian")

    st.markdown("""
    <div class="green-card">
        <h3>📖 Pengajian Senenan</h3>
        <p><b>Tempat:</b> Madrasah Al-Falah</p>
        <p><b>Hari:</b> Senin pagi</p>
        <p><b>Jam:</b> 07.30 - 09.00 WIB</p>
        <p><b>Rotasi:</b> Aang Deden, Ustadz Ihin, Ustadz Ihin, Ustadz Nanang</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="green-card">
        <h3>📖 Pengajian Malam Rabu</h3>
        <p><b>Tempat:</b> Madrasah Al-Falah</p>
        <p><b>Hari:</b> Selasa malam Rabu</p>
        <p><b>Jam:</b> 19.30 - 21.30 WIB</p>
        <p><b>Rotasi:</b> Ustadz Ihin, Ustadz Nanang, Ustadz Jujun, Aang Deden</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="green-card">
        <h3>🌙 Syahriahan Sholawat</h3>
        <p><b>Tempat:</b> Masjid Jami Al-Falah</p>
        <p><b>Waktu:</b> Malam Jumat awal bulan Hijriah</p>
        <p><b>Pimpinan:</b> Aang Deden Kasyful Anwar</p>
    </div>
    """, unsafe_allow_html=True)

# =========================
# DATA JAMAAH
# =========================

elif menu == "👥 Data Jamaah":
    st.markdown("## 👥 Data Jamaah")

    df = baca_jamaah()

    a1, a2, a3 = st.columns(3)
    a1.metric("Total Jamaah", len(df))
    a2.metric("Laki-laki", len(df[df["JenisKelamin"] == "Laki-laki"]))
    a3.metric("Perempuan", len(df[df["JenisKelamin"] == "Perempuan"]))

    st.dataframe(df, use_container_width=True)

    st.divider()
    st.markdown("## ➕ Tambah Jamaah")

    with st.form("form_jamaah"):
        nama = st.text_input("Nama")
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        nowa = st.text_input("Nomor WhatsApp")
        catatan = st.text_input("Catatan", value="-")
        submit = st.form_submit_button("💾 Simpan Jamaah")

        if submit:
            if nama.strip() == "" or nowa.strip() == "":
                st.warning("Nama dan nomor WA wajib diisi.")
            else:
                baru = pd.DataFrame([{
                    "Nama": nama,
                    "JenisKelamin": jk,
                    "NoWA": normalisasi_wa(nowa),
                    "Aktif": "Ya",
                    "Catatan": catatan
                }])
                df = pd.concat([df, baru], ignore_index=True)
                df.to_csv(JAMAAH_FILE, index=False)
                st.success("Jamaah berhasil ditambahkan.")
                st.rerun()

# =========================
# SHARE WHATSAPP
# =========================

elif menu == "📢 Share WhatsApp":
    st.markdown("## 📢 Share WhatsApp Jamaah")

    df = baca_jamaah()

    jenis_pengumuman = st.selectbox(
        "Pilih Jenis Pengumuman",
        ["Pengajian Senenan", "Pengajian Malam Rabu", "Syahriahan Sholawat"]
    )

    if jenis_pengumuman == "Pengajian Senenan":
        pengisi = st.selectbox("Pengisi", ["Aang Deden Kasyful Anwar", "Ustadz Ihin", "Ustadz Nanang"])
        pesan = buat_pesan_senenan(pengisi)
        target = df[(df["JenisKelamin"] == "Perempuan") & (df["Aktif"] == "Ya")]

    elif jenis_pengumuman == "Pengajian Malam Rabu":
        pengisi = st.selectbox("Pengisi", ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden Kasyful Anwar"])
        pesan = buat_pesan_malam_rabu(pengisi)
        target = df[(df["JenisKelamin"] == "Laki-laki") & (df["Aktif"] == "Ya")]

        if pengisi == "Aang Deden Kasyful Anwar":
            khusus = df[df["Nama"].str.lower().str.contains("aang deden", na=False)]
            target = pd.concat([target, khusus]).drop_duplicates(subset=["NoWA"])

    else:
        pesan = buat_pesan_syahriahan()
        target = df[df["Aktif"].isin(["Ya", "Khusus"])]

    st.markdown("### Isi Pesan")
    st.text_area("Pesan siap kirim", value=pesan, height=260)

    st.markdown(f"### Target Penerima: {len(target)} Jamaah")
    st.dataframe(target[["Nama", "JenisKelamin", "NoWA", "Aktif"]], use_container_width=True)

    st.warning("Untuk saat ini WhatsApp masih dibuka satu per satu agar aman dan tidak dianggap spam.")

    for _, row in target.iterrows():
        st.link_button(
            f"📱 Kirim ke {row['Nama']}",
            link_wa(row["NoWA"], pesan),
            use_container_width=True
        )

# =========================
# ADMIN
# =========================

elif menu == "🔐 Admin Bendahara":
    st.markdown("## 🔐 Admin Bendahara")

    password = st.text_input("Password Admin", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Login berhasil.")

        tab1, tab2 = st.tabs(["➕ Input Kas", "📊 Data Kas"])

        with tab1:
            tanggal_input = st.date_input("Tanggal Transaksi")
            bulan = st.text_input("Bulan Laporan", value=datetime.now().strftime("%B %Y"))
            jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
            kategori = st.selectbox(
                "Kategori",
                ["Kotak Amal", "Infaq Jumat", "Sedekah Jamaah", "Donasi Pembangunan",
                 "Operasional Masjid", "Listrik / Air", "Kebersihan", "Kegiatan Keagamaan",
                 "Pembangunan", "Perlengkapan", "Lainnya"]
            )
            keterangan = st.text_area("Keterangan")
            jumlah = st.number_input("Jumlah", min_value=0, step=500)

            if st.button("💾 SIMPAN TRANSAKSI"):
                if jumlah <= 0:
                    st.warning("Jumlah harus lebih dari 0.")
                else:
                    simpan_transaksi(
                        tanggal_input.strftime("%d-%m-%Y"),
                        bulan,
                        jenis,
                        kategori,
                        keterangan,
                        jumlah
                    )
                    st.success("Transaksi berhasil disimpan.")
                    st.rerun()

        with tab2:
            df = baca_kas()
            st.dataframe(df, use_container_width=True)

    elif password:
        st.error("Password salah.")

st.divider()
st.caption("Al-Falah Digital V12 | Masjid Jami Al-Falah | Transparansi, Amanah, dan Kemakmuran Masjid")
