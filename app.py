import streamlit as st
import pandas as pd
from datetime import date
import os
import urllib.parse

st.set_page_config(page_title="Al-Falah Digital V5", page_icon="🕌", layout="wide")

KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"

KOLOM_KAS = ["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"]
KOLOM_PENGUMUMAN = ["Tanggal", "Judul", "Isi"]

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
    "Bidang Sosial dan Kemanusiaan": ["Wa Adu", "M. Ajang", "M. Ece Abda", "M. Iman", "Ceng Sasa"],
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

def rupiah(angka):
    try:
        return "Rp {:,.0f}".format(float(angka)).replace(",", ".")
    except:
        return "Rp 0"

def load_kas():
    if os.path.exists(KAS_FILE):
        try:
            df = pd.read_csv(KAS_FILE)
            for kolom in KOLOM_KAS:
                if kolom not in df.columns:
                    df[kolom] = 0 if kolom == "Jumlah" else ""
            df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)
            return df[KOLOM_KAS]
        except:
            return pd.DataFrame(columns=KOLOM_KAS)
    return pd.DataFrame(columns=KOLOM_KAS)

def save_kas(df):
    df.to_csv(KAS_FILE, index=False)

def load_pengumuman():
    if os.path.exists(PENGUMUMAN_FILE):
        try:
            df = pd.read_csv(PENGUMUMAN_FILE)
            for kolom in KOLOM_PENGUMUMAN:
                if kolom not in df.columns:
                    df[kolom] = ""
            return df[KOLOM_PENGUMUMAN]
        except:
            return pd.DataFrame(columns=KOLOM_PENGUMUMAN)
    return pd.DataFrame(columns=KOLOM_PENGUMUMAN)

def save_pengumuman(df):
    df.to_csv(PENGUMUMAN_FILE, index=False)

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

kas_df = load_kas()
pengumuman_df = load_pengumuman()

st.markdown("""
# 🕌 APP MASJID JAMI AL-FALAH

### Masjid Jami Al-Falah
### Kp. Caringin RT 005 RW 005
### Desa Sukasari - Kecamatan Karangtengah - Kabupaten Cianjur

⭐ Sistem Informasi, Administrasi, Kas, Pengajian dan Pengumuman Masjid
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

if menu == "🏠 Dashboard":

   st.image(
       "banner.png",
       use_container_width=True
   )

    st.title("🕌 APP MASJID JAMI AL-FALAH")

    pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Saldo Kas", rupiah(saldo))
    c2.metric("⬆️ Total Pemasukan", rupiah(pemasukan))
    c3.metric("⬇️ Total Pengeluaran", rupiah(pengeluaran))
    c4.metric("👥 Pengurus", sum(len(v) for v in pengurus.values()))

    st.divider()
    st.subheader("📅 Jadwal Utama")

    st.dataframe(
        pd.DataFrame(jadwal, columns=["Kegiatan", "Waktu Kegiatan", "Pengisi"]),
        use_container_width=True
    )

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
        data = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Jenis": jenis,
            "Kategori": kategori,
            "Keterangan": keterangan,
            "Jumlah": jumlah,
            "Petugas": petugas
        }])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        st.success("Data kas berhasil disimpan.")

elif menu == "📦 Input Kotak Amal":
    st.subheader("📦 Input Buka Kotak Amal")

    with st.form("form_kotak"):
        tanggal = st.date_input("Tanggal Buka Kotak Amal", date.today())
        keterangan = st.text_input("Keterangan", value="Kotak amal masjid")
        jumlah = st.number_input("Jumlah Uang", min_value=0, step=1000)
        petugas = st.text_input("Petugas Penghitung", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan Kotak Amal")

    if simpan:
        data = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Jenis": "Pemasukan",
            "Kategori": "Kotak Amal",
            "Keterangan": keterangan,
            "Jumlah": jumlah,
            "Petugas": petugas
        }])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)
        st.success("Kotak amal berhasil masuk ke kas masjid.")

elif menu == "📊 Laporan Kas":
    st.subheader("📊 Laporan Kas Masjid")

    if kas_df.empty:
        st.info("Belum ada data kas.")
    else:
        kas_df["Tanggal"] = pd.to_datetime(kas_df["Tanggal"], errors="coerce")

        daftar_bulan = sorted(
            kas_df["Tanggal"].dropna().dt.strftime("%Y-%m").unique(),
            reverse=True
        )

        if len(daftar_bulan) == 0:
            st.warning("Belum ada tanggal kas yang valid.")
            st.stop()

        bulan = st.selectbox("Pilih Bulan", daftar_bulan)
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

elif menu == "👥 Pengurus DKM":
    st.subheader("👥 Struktur Pengurus DKM")

    for jabatan, daftar_nama in pengurus.items():
        with st.expander(jabatan, expanded=jabatan in ["Ketua DKM", "Wakil Ketua", "Sekretaris", "Bendahara"]):
            for nama in daftar_nama:
                st.write(f"- {nama}")

elif menu == "📅 Jadwal Pengajian":
    st.subheader("📅 Jadwal Pengajian")
    st.dataframe(pd.DataFrame(jadwal, columns=["Kegiatan", "Waktu Kegiatan", "Pengisi"]), use_container_width=True)
    st.info("Notifikasi otomatis tetap berjalan melalui GitHub Actions dan Telegram Bot.")

elif menu == "📢 Pengumuman":
    st.subheader("📢 Buat Pengumuman")

    with st.form("form_pengumuman"):
        tanggal = st.date_input("Tanggal", date.today())
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        simpan = st.form_submit_button("💾 Simpan Pengumuman")

    if simpan:
        data = pd.DataFrame([{
            "Tanggal": str(tanggal),
            "Judul": judul,
            "Isi": isi
        }])
        pengumuman_df = pd.concat([pengumuman_df, data], ignore_index=True)
        save_pengumuman(pengumuman_df)
        st.success("Pengumuman berhasil disimpan.")

    st.divider()
    st.subheader("Daftar Pengumuman")
    if pengumuman_df.empty:
        st.info("Belum ada pengumuman.")
    else:
        st.dataframe(pengumuman_df, use_container_width=True)

elif menu == "📲 Share WhatsApp":
    st.subheader("📲 Share ke WhatsApp")

    teks = st.text_area(
        "Teks yang akan dibagikan",
        value="""Assalamu'alaikum Warahmatullahi Wabarakatuh

Pengumuman Masjid Jami Al-Falah
Kp. Caringin

Insya Allah akan dilaksanakan kegiatan di Masjid Jami Al-Falah.

Mohon kehadiran dan partisipasinya.

Jazakumullahu khairan.
"""
    )

    st.markdown(f"[📤 Bagikan ke WhatsApp]({wa_link(teks)})")
    st.code(teks)
