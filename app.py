import streamlit as st
import pandas as pd
from datetime import date
import os
import urllib.parse
import requests

st.set_page_config(page_title="APP MASJID JAMI AL-FALAH", page_icon="🕌", layout="wide")

KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"
BANNER_FILE = "banner.png"

KOLOM_KAS = ["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"]
KOLOM_PENGUMUMAN = ["Tanggal", "Judul", "Isi"]

CHAT_ID = "8951538688"

pengurus = {
    "Pelindung": ["Dadan Haris (Kepala Desa Sukasari)"],
    "Pembina": ["Aah Hj Encep Bahrul Ulum"],
    "Penasihat": ["Pih Uce"],
    "Ketua DKM": ["Aang Deden Kasyful Anwar"],
    "Wakil Ketua": ["Iden Tazuni"],
    "Sekretaris": ["Ustadz Ihin"],
    "Bendahara": ["Aceng Abdul Roup"],
    "Pendidikan & Pengajian": ["Usep", "Bim-Bim", "Dede Adol", "M. Oleh"],
    "Humas & Informasi": ["Wa Hamid", "Ahmad Fauzi", "Ruslan Abdul Gani", "Yudi"],
    "Sosial & Kemanusiaan": ["Wa Adu", "M. Ajang", "M. Ece Abda", "M. Iman", "Ceng Sasa"],
    "Sarana & Prasarana": ["Agus Sobur", "Dede Eon", "Jiun", "Dede Ro’i", "Andri", "Empay"],
    "Kebersihan": ["Baba", "Ujang", "Endat"],
    "Ibadah & Dakwah": ["Aang Deden", "Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Pih Uce"],
    "Keamanan": ["Ace Pu’ad", "Nyanyang (Gonyol)", "M. Emon"]
}

jadwal = [
    ["Pengajian Laki-laki Malam Rabu", "Malam Rabu, 19:30 - 21:30 WIB", "Ustadz Ihin, Ustadz Nanang, Ustadz Jujun, Aang Deden"],
    ["Pengajian Ibu-ibu Hari Senin", "Senin, 07:30 - 09:00 WIB", "Ustadz Nanang, Aang Deden, Ustadz Ihin, Ustadz Ihin"],
    ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "Aang Deden Kasyful Anwar"]
]

def rupiah(angka):
    return "Rp {:,.0f}".format(float(angka)).replace(",", ".")

def load_kas():
    if os.path.exists(KAS_FILE):
        df = pd.read_csv(KAS_FILE)
        for k in KOLOM_KAS:
            if k not in df.columns:
                df[k] = 0 if k == "Jumlah" else ""
        df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)
        return df[KOLOM_KAS]
    return pd.DataFrame(columns=KOLOM_KAS)

def save_kas(df):
    df.to_csv(KAS_FILE, index=False)

def load_pengumuman():
    if os.path.exists(PENGUMUMAN_FILE):
        df = pd.read_csv(PENGUMUMAN_FILE)
        for k in KOLOM_PENGUMUMAN:
            if k not in df.columns:
                df[k] = ""
        return df[KOLOM_PENGUMUMAN]
    return pd.DataFrame(columns=KOLOM_PENGUMUMAN)

def save_pengumuman(df):
    df.to_csv(PENGUMUMAN_FILE, index=False)

def wa_link(text):
    return "https://wa.me/?text=" + urllib.parse.quote(text)

def kirim_telegram(pesan):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        try:
            token = st.secrets["TELEGRAM_BOT_TOKEN"]
        except:
            token = None

    if not token:
        return False, "Token Telegram belum dipasang di Streamlit Secrets."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, json={"chat_id": CHAT_ID, "text": pesan})
    return res.ok, res.text

kas_df = load_kas()
pengumuman_df = load_pengumuman()

st.sidebar.title("🕌 Menu")
menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "🏠 Dashboard",
        "📊 Laporan Kas",
        "👥 Pengurus DKM",
        "📅 Jadwal Pengajian",
        "📢 Pengumuman",
        "📲 Share WhatsApp"
    ]
)

if menu == "🏠 Dashboard":

    if os.path.exists(BANNER_FILE):
        st.image(BANNER_FILE, use_container_width=True)

    st.markdown("""
    <div style="
    background:linear-gradient(135deg,#064e3b,#15803d,#d4af37);
    padding:22px;
    border-radius:18px;
    color:white;
    text-align:center;
    margin-bottom:25px;
    box-shadow:0 6px 20px rgba(0,0,0,0.25);
    ">
    <h1>🕌 APP MASJID JAMI AL-FALAH</h1>
    <h3>Sistem Informasi dan Administrasi Masjid Terpadu</h3>
    <p>Kp. Caringin RT 005 RW 005, Desa Sukasari, Karangtengah, Cianjur</p>
    </div>
    """, unsafe_allow_html=True)

    pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Saldo Kas", rupiah(saldo))
    c2.metric("⬆️ Pemasukan", rupiah(pemasukan))
    c3.metric("⬇️ Pengeluaran", rupiah(pengeluaran))
    c4.metric("👥 Pengurus", sum(len(v) for v in pengurus.values()))

    st.divider()

    st.subheader("📦 Input Cepat Kotak Amal")
    with st.form("form_kotak_dashboard"):
        c1, c2 = st.columns(2)
        tanggal = c1.date_input("Tanggal", date.today())
        jumlah = c2.number_input("Jumlah Kotak Amal", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan", value="Kotak amal masjid")
        petugas = st.text_input("Petugas", value="Aceng Abdul Roup")
        simpan_kotak = st.form_submit_button("💾 Simpan Kotak Amal")

    if simpan_kotak:
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

        pesan = f"""🕌 APP MASJID JAMI AL-FALAH

Pemasukan Kotak Amal

Tanggal: {tanggal}
Jumlah: {rupiah(jumlah)}
Petugas: {petugas}
Keterangan: {keterangan}
"""
        kirim_telegram(pesan)
        st.success("Kotak amal berhasil disimpan.")

    st.divider()

    st.subheader("💰 Input Kas Cepat")
    with st.form("form_kas_dashboard"):
        c1, c2, c3 = st.columns(3)
        tanggal2 = c1.date_input("Tanggal Kas", date.today())
        jenis = c2.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = c3.selectbox("Kategori", ["Infaq Jumat", "Kotak Amal", "Donatur", "Pembangunan", "Listrik", "Kebersihan", "Lainnya"])
        keterangan2 = st.text_input("Keterangan Kas")
        jumlah2 = st.number_input("Jumlah Kas", min_value=0, step=1000)
        petugas2 = st.text_input("Petugas Kas", value="Aceng Abdul Roup")
        simpan_kas = st.form_submit_button("💾 Simpan Kas")

    if simpan_kas:
        data = pd.DataFrame([{
            "Tanggal": str(tanggal2),
            "Jenis": jenis,
            "Kategori": kategori,
            "Keterangan": keterangan2,
            "Jumlah": jumlah2,
            "Petugas": petugas2
        }])
        kas_df = pd.concat([kas_df, data], ignore_index=True)
        save_kas(kas_df)

        pesan = f"""🕌 APP MASJID JAMI AL-FALAH

Data Kas Baru

Jenis: {jenis}
Kategori: {kategori}
Tanggal: {tanggal2}
Jumlah: {rupiah(jumlah2)}
Petugas: {petugas2}
Keterangan: {keterangan2}
"""
        kirim_telegram(pesan)
        st.success("Data kas berhasil disimpan.")

    st.divider()

    st.subheader("📅 Jadwal Pengajian")
    st.dataframe(
        pd.DataFrame(jadwal, columns=["Kegiatan", "Waktu Kegiatan", "Pengisi"]),
        use_container_width=True
    )

    st.subheader("👥 Pengurus Inti DKM")
    c1, c2, c3, c4 = st.columns(4)
    c1.info("Ketua DKM\n\nAang Deden Kasyful Anwar")
    c2.info("Wakil Ketua\n\nIden Tazuni")
    c3.info("Sekretaris\n\nUstadz Ihin")
    c4.info("Bendahara\n\nAceng Abdul Roup")

    st.divider()

    st.subheader("📢 Pengumuman Cepat")
    with st.form("form_pengumuman_dashboard"):
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        simpan_pengumuman = st.form_submit_button("💾 Simpan Pengumuman")

    if simpan_pengumuman:
        data = pd.DataFrame([{
            "Tanggal": str(date.today()),
            "Judul": judul,
            "Isi": isi
        }])
        pengumuman_df = pd.concat([pengumuman_df, data], ignore_index=True)
        save_pengumuman(pengumuman_df)
        st.success("Pengumuman berhasil disimpan.")

    if not pengumuman_df.empty:
        st.subheader("📋 Pengumuman Terbaru")
        st.dataframe(pengumuman_df.tail(5), use_container_width=True)

    st.divider()

    st.subheader("📲 Share WhatsApp")
    teks_wa = st.text_area(
        "Teks Share WhatsApp",
        value="""Assalamu'alaikum Warahmatullahi Wabarakatuh

Pengumuman Masjid Jami Al-Falah
Kp. Caringin

Insya Allah akan dilaksanakan kegiatan di Masjid Jami Al-Falah.

Mohon kehadiran dan partisipasinya.

Jazakumullahu khairan.
"""
    )
    st.markdown(f"[📤 Bagikan ke WhatsApp]({wa_link(teks_wa)})")

elif menu == "📊 Laporan Kas":
    st.subheader("📊 Laporan Kas Masjid")

    if kas_df.empty:
        st.info("Belum ada data kas.")
    else:
        kas_df["Tanggal"] = pd.to_datetime(kas_df["Tanggal"], errors="coerce")
        daftar_bulan = sorted(kas_df["Tanggal"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)

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

elif menu == "📢 Pengumuman":
    st.subheader("📢 Daftar Pengumuman")
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
