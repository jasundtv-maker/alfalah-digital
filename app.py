import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import urllib.parse

st.set_page_config(
    page_title="Al-Falah Digital V5",
    page_icon="🕌",
    layout="wide"
)

KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"

# ================= DATA AWAL =================

pengurus = {
    "Pelindung": ["Dadan Haris (Kepala Desa Sukasari)"],
    "Pembina": ["Aah Hj Encep Bahrul Ulum"],
    "Penasihat": ["Pih Uce"],
    "Ketua DKM": ["Aang Deden Kasyful Anwar"],
    "Wakil Ketua": ["Iden Tazuni"],
    "Sekretaris": ["Ustadz Ihin"],
    "Bendahara": ["Aceng Abdul Roup"],
    "Bidang Pendidikan dan Pengajian": ["Usep", "Bim-Bim", "Dede Adol", "M. Oleh"],
    "Bidang Humas dan Informasi": ["Wa Hamid", "Ahmad Fauzi", "Ruslan Abdul Gani", "Yudi"],
    "Bidang Sosial dan Kemanusiaan": ["Wa Adu", "M. Ajang", "M. Ece Abda", "Abda", "M. Iman", "Ceng Sasa"],
    "Bidang Sarana dan Prasarana": ["Agus Sobur", "Dede Eon", "Jiun", "Dede Ro’i", "Andri", "Empay"],
    "Bidang Kebersihan": ["Baba", "Ujang", "Endat"],
    "Bidang Ibadah dan Dakwah": ["Aang Deden", "Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Pih Uce"],
    "Bidang Keamanan": ["Ace Pu’ad", "Nyanyang (Gonyol)", "M. Emon"]
}

jadwal = [
    ["Pengajian Laki-laki Malam Rabu", "Setiap malam Rabu, pukul 19:30 - 21:30 WIB", "Ustadz Ihin, Ustadz Nanang, Ustadz Jujun, Aang Deden"],
    ["Pengajian Ibu-ibu Hari Senin", "Setiap hari Senin, pukul 07:30 - 09:00 WIB", "Ustadz Nanang, Aang Deden, Ustadz Ihin, Ustadz Ihin"],
    ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "Aang Deden Kasyful Anwar"]
]

# ================= FUNGSI =================

def load_kas():
    if os.path.exists(KAS_FILE):
        return pd.read_csv(KAS_FILE)
    return pd.DataFrame(columns=["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"])

def save_kas(df):
    df.to_csv(KAS_FILE, index=False)

def load_pengumuman():
    if os.path.exists(PENGUMUMAN_FILE):
        return pd.read_csv(PENGUMUMAN_FILE)
    return pd.DataFrame(columns=["Tanggal", "Judul", "Isi"])

def save_pengumuman(df):
    df.to_csv(PENGUMAN_FILE, index=False)

def rupiah(angka):
    return "Rp {:,.0f}".format(angka).replace(",", ".")

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

# ================= HEADER =================

st.markdown("""
# 🕌 AL-FALAH DIGITAL V5
### Masjid Jami Al-Falah  
Kp. Caringin RT 005 RW 005, Desa Sukasari, Kecamatan Karangtengah, Kabupaten Cianjur
""")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "💰 Input Kas",
        "📦 Input Kotak Amal",
        "📊 Laporan Kas",
        "👥 Pengurus DKM",
        "📅 Jadwal Pengajian",
        "📢 Pengumuman",
        "📲 Share WhatsApp"
    ]
)

kas_df = load_kas()
pengumuman_df = load_pengumuman()

# ================= DASHBOARD =================

if menu == "🏠 Dashboard":
    pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum() if not kas_df.empty else 0
    pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum() if not kas_df.empty else 0
    saldo = pemasukan - pengeluaran

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Saldo Kas", rupiah(saldo))
    col2.metric("⬆️ Total Pemasukan", rupiah(pemasukan))
    col3.metric("⬇️ Total Pengeluaran", rupiah(pengeluaran))
    col4.metric("👥 Pengurus", sum(len(v) for v in pengurus.values()))

    st.divider()
    st.subheader("📅 Jadwal Utama")
    st.dataframe(pd.DataFrame(jadwal, columns=["Kegiatan", "Waktu Kegiatan", "Pengisi"]), use_container_width=True)

# ================= INPUT KAS =================

elif menu == "💰 Input Kas":
    st.subheader("💰 Input Kas Masjid")

    with st.form("form_kas"):
        tanggal = st.date_input("Tanggal", date.today())
        jenis = st.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = st.selectbox("Kategori", ["Infaq Jumat", "Kotak Amal", "Donatur", "Pembangunan", "Listrik", "Kebersihan", "Lainnya"])
        keterangan = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah", min_value=0, step=1000)
        petugas = st.text_input("Petugas", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan")

    if simpan:
        data = {
            "Tanggal": str(tanggal),
            "Jenis": jenis,
            "Kategori": kategori,
            "Keterangan": keterangan,
            "Jumlah": jumlah,
            "Petugas": petugas
        }
        kas_df = pd.concat([kas_df, pd.DataFrame([data])], ignore_index=True)
        save_kas(kas_df)
        st.success("Data kas berhasil disimpan.")

# ================= KOTAK AMAL =================

elif menu == "📦 Input Kotak Amal":
    st.subheader("📦 Input Buka Kotak Amal")

    with st.form("form_kotak_amal"):
        tanggal = st.date_input("Tanggal Buka Kotak Amal", date.today())
        keterangan = st.text_input("Keterangan", value="Kotak amal masjid")
        jumlah = st.number_input("Jumlah Uang", min_value=0, step=1000)
        petugas = st.text_input("Petugas Penghitung", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan Kotak Amal")

    if simpan:
        data = {
            "Tanggal": str(tanggal),
            "Jenis": "Pemasukan",
            "Kategori": "Kotak Amal",
            "Keterangan": keterangan,
            "Jumlah": jumlah,
            "Petugas": petugas
        }
        kas_df = pd.concat([kas_df, pd.DataFrame([data])], ignore_index=True)
        save_kas(kas_df)
        st.success("Pemasukan kotak amal berhasil disimpan ke kas masjid.")

# ================= LAPORAN =================

elif menu == "📊 Laporan Kas":
    st.subheader("📊 Laporan Kas Masjid")

    if kas_df.empty:
        st.info("Belum ada data kas.")
    else:
        kas_df["Tanggal"] = pd.to_datetime(kas_df["Tanggal"])
        daftar_bulan = sorted(kas
        laporan = kas_df[kas_df["Tanggal"].dt.strftime("%Y-%m") == bulan]

        pemasukan = laporan[laporan["Jenis"] == "Pemasukan"]["Jumlah"].sum()
        pengeluaran = laporan[laporan["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
        saldo = pemasukan - pengeluaran

        c1, c2, c3 = st.columns(3)
        c1.metric("Pemasukan", rupiah(pemasukan))
        c2.metric("Pengeluaran", rupiah(pengeluaran))
        c3.metric("Saldo Bulan Ini", rupiah(saldo))

        st.dataframe(laporan, use_container_width=True)

        csv = laporan.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Laporan CSV", csv, f"laporan_kas_{bulan}.csv", "text/csv")

# ================= PENGURUS =================

elif menu == "👥 Pengurus DKM":
    st.subheader("👥 Struktur Pengurus DKM")

    for jabatan, nama_list in pengurus.items():
        with st.expander(jabatan, expanded=True if jabatan in ["Ketua DKM", "Wakil Ketua", "Sekretaris", "Bendahara"] else False):
            for nama in nama_list:
                st.write(f"- {nama}")

# ================= JADWAL =================

elif menu == "📅 Jadwal Pengajian":
    st.subheader("📅 Jadwal Pengajian")

    df_jadwal = pd.DataFrame(jadwal, columns=["Kegiatan", "Waktu Notifikasi", "Pengisi"])
    st.dataframe(df_jadwal, use_container_width=True)

    st.info("Notifikasi otomatis berjalan melalui GitHub Actions dan Telegram Bot.")

# ================= PENGUMUMAN =================

elif menu == "📢 Pengumuman":
    st.subheader("📢 Buat Pengumuman")

    with st.form("form_pengumuman"):
        tanggal = st.date_input("Tanggal", date.today())
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        simpan = st.form_submit_button("💾 Simpan Pengumuman")

    if simpan:
        data = {
            "Tanggal": str(tanggal),
            "Judul": judul,
            "Isi": isi
        }
        pengumuman_df = pd.concat([pengumuman_df, pd.DataFrame([data])], ignore_index=True)
        pengumuman_df.to_csv(PENGUMUMAN_FILE, index=False)
        st.success("Pengumuman berhasil disimpan.")

    st.divider()
    st.subheader("Daftar Pengumuman")

    if pengumuman_df.empty:
        st.info("Belum ada pengumuman.")
    else:
        st.dataframe(pengumuman_df, use_container_width=True)

# ================= SHARE WHATSAPP =================

elif menu == "📲 Share WhatsApp":
    st.subheader("📲 Share Pengumuman ke WhatsApp")

    teks = st.text_area(
        "Tulis teks yang akan dibagikan",
        value="""Assalamu'alaikum Warahmatullahi Wabarakatuh

Pengumuman Masjid Jami Al-Falah
Kp. Caringin

Insya Allah akan dilaksanakan kegiatan di Masjid Jami Al-Falah.

Mohon kehadiran dan partisipasinya.

Jazakumullahu khairan.
"""
    )

    link = wa_link(teks)
    st.markdown(f"[📤 Bagikan ke WhatsApp]({link})")

    st.code(teks)
