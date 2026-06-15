import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os
import urllib.parse
import requests

st.set_page_config(page_title="APP MASJID JAMI AL-FALAH", page_icon="🕌", layout="wide")

KAS_FILE = "kas_masjid.csv"
PENGUMUMAN_FILE = "pengumuman.csv"
BANNER_FILE = "banner.png"
CHAT_ID = "8951538688"

KOLOM_KAS = ["Tanggal", "Jenis", "Kategori", "Keterangan", "Jumlah", "Petugas"]
KOLOM_PENGUMUMAN = ["Tanggal", "Judul", "Isi"]

pengurus = {
    "Pelindung": ["Dadan Haris"],
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

pengajian_malam_rabu = ["Ustadz Ihin", "Ustadz Nanang", "Ustadz Jujun", "Aang Deden"]
pengajian_senin = ["Ustadz Nanang", "Aang Deden", "Ustadz Ihin", "Ustadz Ihin"]

def rupiah(angka):
    try:
        return "Rp {:,.0f}".format(float(angka)).replace(",", ".")
    except:
        return "Rp 0"

def load_kas():
    if os.path.exists(KAS_FILE):
        try:
            df = pd.read_csv(KAS_FILE)
            for k in KOLOM_KAS:
                if k not in df.columns:
                    df[k] = 0 if k == "Jumlah" else ""
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
            for k in KOLOM_PENGUMUMAN:
                if k not in df.columns:
                    df[k] = ""
            return df[KOLOM_PENGUMUMAN]
        except:
            return pd.DataFrame(columns=KOLOM_PENGUMUMAN)
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
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": pesan}, timeout=10)
        return True
    except:
        return False

def tanggal_berikutnya(target_weekday):
    hari_ini = date.today()
    selisih = (target_weekday - hari_ini.weekday()) % 7
    if selisih == 0:
        selisih = 7
    return hari_ini + timedelta(days=selisih)

def index_rotasi(tanggal_acuan):
    start = date(2026, 6, 16)
    minggu = ((tanggal_acuan - start).days // 7) % 4
    return minggu

def format_tanggal(tgl):
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    nama_bulan = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    return f"{nama_hari[tgl.weekday()]}, {tgl.day} {nama_bulan[tgl.month-1]} {tgl.year}"

kas_df = load_kas()
pengumuman_df = load_pengumuman()

st.sidebar.title("🕌 APP AL-FALAH")
menu = st.sidebar.radio(
    "Menu Admin",
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

    if os.path.exists(BANNER_FILE):
        st.image(BANNER_FILE, use_container_width=True)

    st.markdown("""
    <div style="
        background: linear-gradient(135deg,#064e3b,#047857,#d4af37);
        padding: 28px;
        border-radius: 22px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    ">
        <h1 style="margin-bottom:5px;">🕌 APP MASJID JAMI AL-FALAH</h1>
        <h3 style="margin-top:0;">Sistem Informasi dan Administrasi Masjid Terpadu</h3>
        <p>Kp. Caringin RT 005 RW 005, Desa Sukasari, Karangtengah, Cianjur</p>
    </div>
    """, unsafe_allow_html=True)

    pemasukan = kas_df[kas_df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = kas_df[kas_df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Saldo Kas", rupiah(saldo))
    c2.metric("⬆️ Total Pemasukan", rupiah(pemasukan))
    c3.metric("⬇️ Total Pengeluaran", rupiah(pengeluaran))
    c4.metric("👥 Pengurus", sum(len(v) for v in pengurus.values()))

    st.divider()

    tgl_rabu = tanggal_berikutnya(2)
    idx_rabu = index_rotasi(tgl_rabu)
    ustadz_rabu = pengajian_malam_rabu[idx_rabu]

    tgl_senin = tanggal_berikutnya(0)
    idx_senin = index_rotasi(tgl_senin)
    ustadz_senin = pengajian_senin[idx_senin]

    st.markdown("## 📌 Jadwal Pengajian Minggu Ini")

    a, b = st.columns(2)

    with a:
        st.markdown(f"""
        <div style="
            background:#f0fdf4;
            border:1px solid #bbf7d0;
            padding:20px;
            border-radius:18px;
            box-shadow:0 4px 14px rgba(0,0,0,0.08);
        ">
            <h3>📖 Pengajian Laki-laki Malam Rabu</h3>
            <p><b>📅 Tanggal:</b> {format_tanggal(tgl_rabu)}</p>
            <p><b>🕢 Waktu:</b> 19:30 - 21:30 WIB</p>
            <p><b>👳 Pengisi:</b> {ustadz_rabu}</p>
            <p style="font-size:14px;color:#374151;">
            Catatan: Jika ustadz tidak berhalangan. Jika berhalangan, akan diganti oleh ustadz lain.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown(f"""
        <div style="
            background:#fffbeb;
            border:1px solid #fde68a;
            padding:20px;
            border-radius:18px;
            box-shadow:0 4px 14px rgba(0,0,0,0.08);
        ">
            <h3>🌸 Pengajian Ibu-ibu Hari Senin</h3>
            <p><b>📅 Tanggal:</b> {format_tanggal(tgl_senin)}</p>
            <p><b>🕢 Waktu:</b> 07:30 - 09:00 WIB</p>
            <p><b>👳 Pengisi:</b> {ustadz_senin}</p>
            <p style="font-size:14px;color:#374151;">
            Catatan: Jika ustadz tidak berhalangan. Jika berhalangan, akan diganti oleh ustadz lain.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background:#eff6ff;
        border:1px solid #bfdbfe;
        padding:18px;
        border-radius:18px;
        margin-top:18px;
    ">
        <h3>🌙 Syahriahan Sholawat</h3>
        <p><b>Waktu:</b> Malam Jumat awal bulan Hijriah, pukul 20:00 - 21:30 WIB</p>
        <p><b>Pengisi:</b> Aang Deden Kasyful Anwar</p>
        <p style="font-size:14px;color:#374151;">
        Catatan: Jika tidak berhalangan. Jika berhalangan, akan diganti oleh ustadz lain.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📋 Transaksi Kas Terbaru")
    if kas_df.empty:
        st.info("Belum ada data kas.")
    else:
        tampil = kas_df.tail(7).copy()
        tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
        st.dataframe(tampil, use_container_width=True)

    st.divider()

    st.subheader("👥 Pengurus Inti DKM")
    p1, p2, p3, p4 = st.columns(4)
    p1.info("Ketua DKM\n\nAang Deden Kasyful Anwar")
    p2.info("Wakil Ketua\n\nIden Tazuni")
    p3.info("Sekretaris\n\nUstadz Ihin")
    p4.info("Bendahara\n\nAceng Abdul Roup")

    st.divider()

    st.subheader("📢 Pengumuman Terbaru")
    if pengumuman_df.empty:
        st.info("Belum ada pengumuman.")
    else:
        st.dataframe(pengumuman_df.tail(5), use_container_width=True)

elif menu == "💰 Input Kas":
    st.subheader("💰 Input Kas Admin")

    with st.form("form_kas"):
        c1, c2, c3 = st.columns(3)
        tanggal = c1.date_input("Tanggal", date.today())
        jenis = c2.selectbox("Jenis", ["Pemasukan", "Pengeluaran"])
        kategori = c3.selectbox(
            "Kategori",
            ["Infaq Jumat", "Kotak Amal", "Donatur", "Pembangunan", "Listrik", "Kebersihan", "Lainnya"]
        )
        keterangan = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah", min_value=0, step=1000)
        petugas = st.text_input("Petugas", value="Aceng Abdul Roup")
        simpan = st.form_submit_button("💾 Simpan Kas")

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

        pesan = f"""🕌 APP MASJID JAMI AL-FALAH

Data Kas Baru
Jenis: {jenis}
Kategori: {kategori}
Tanggal: {tanggal}
Jumlah: {rupiah(jumlah)}
Petugas: {petugas}
Keterangan: {keterangan}
"""
        kirim_telegram(pesan)
        st.success("Data kas berhasil disimpan.")

elif menu == "📦 Input Kotak Amal":
    st.subheader("📦 Input Kotak Amal Admin")

    with st.form("form_kotak"):
        tanggal = st.date_input("Tanggal Buka Kotak Amal", date.today())
        jumlah = st.number_input("Jumlah Kotak Amal", min_value=0, step=1000)
        keterangan = st.text_input("Keterangan", value="Kotak amal masjid")
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

        pesan = f"""🕌 APP MASJID JAMI AL-FALAH

Pemasukan Kotak Amal
Tanggal: {tanggal}
Jumlah: {rupiah(jumlah)}
Petugas: {petugas}
Keterangan: {keterangan}
"""
        kirim_telegram(pesan)
        st.success("Kotak amal berhasil disimpan.")

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

        pemasukan_bulan = laporan[laporan["Jenis"] == "Pemasukan"]["Jumlah"].sum()
        pengeluaran_bulan = laporan[laporan["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
        saldo_bulan = pemasukan_bulan - pengeluaran_bulan

        c1, c2, c3 = st.columns(3)
        c1.metric("Pemasukan Bulan Ini", rupiah(pemasukan_bulan))
        c2.metric("Pengeluaran Bulan Ini", rupiah(pengeluaran_bulan))
        c3.metric("Saldo Bulan Ini", rupiah(saldo_bulan))

        tampil = laporan.copy()
        tampil["Jumlah"] = tampil["Jumlah"].apply(rupiah)
        st.dataframe(tampil, use_container_width=True)

        csv = laporan.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Laporan CSV", csv, f"laporan_kas_{bulan}.csv", "text/csv")

elif menu == "👥 Pengurus DKM":
    st.subheader("👥 Struktur Pengurus DKM")
    for jabatan, daftar_nama in pengurus.items():
        with st.expander(jabatan, expanded=jabatan in ["Ketua DKM", "Wakil Ketua", "Sekretaris", "Bendahara"]):
            for nama in daftar_nama:
                st.write(f"- {nama}")

elif menu == "📅 Jadwal Pengajian":
    st.subheader("📅 Jadwal Pengajian Lengkap")
    df_jadwal = pd.DataFrame([
        ["Pengajian Laki-laki Malam Rabu", "Malam Rabu", "19:30 - 21:30 WIB", "Ihin → Nanang → Jujun → Aang Deden"],
        ["Pengajian Ibu-ibu Hari Senin", "Senin", "07:30 - 09:00 WIB", "Nanang → Aang Deden → Ihin → Ihin"],
        ["Syahriahan Sholawat", "Malam Jumat awal bulan Hijriah", "20:00 - 21:30 WIB", "Aang Deden Kasyful Anwar"]
    ], columns=["Kegiatan", "Hari", "Waktu", "Rotasi/Pengisi"])
    st.dataframe(df_jadwal, use_container_width=True)

elif menu == "📢 Pengumuman":
    st.subheader("📢 Buat Pengumuman")

    with st.form("form_pengumuman"):
        judul = st.text_input("Judul Pengumuman")
        isi = st.text_area("Isi Pengumuman")
        simpan = st.form_submit_button("💾 Simpan Pengumuman")

    if simpan:
        data = pd.DataFrame([{
            "Tanggal": str(date.today()),
            "Judul": judul,
            "Isi": isi
        }])
        pengumuman_df = pd.concat([pengumuman_df, data], ignore_index=True)
        save_pengumuman(pengumuman_df)
        st.success("Pengumuman berhasil disimpan.")

    if not pengumuman_df.empty:
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
