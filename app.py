import streamlit as st
import gspread
import requests
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

# =========================
# KONFIGURASI
# =========================
st.set_page_config(
    page_title="APP MASJID JAMI AL-FALAH V19.2",
    page_icon="🕌",
    layout="wide"
)

WA_AUTO = True
NOMOR_MASJID = "087742958453"

# Mengambil konfigurasi dari secrets.toml
try:
    FONNTE_TOKEN = st.secrets["FONNTE_TOKEN"]
    SHEET_ID = st.secrets["SHEET_ID"]
except KeyError as e:
    st.error(f"Error: Kunci {e} belum diatur di Streamlit Secrets. Pastikan Anda sudah menyimpan file secrets.toml dengan benar.")
    st.stop()

# =========================
# KONEKSI GOOGLE SHEET
# =========================
@st.cache_resource
def koneksi_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

# Inisialisasi koneksi
try:
    sheet = koneksi_sheet()
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets: {e}")
    st.stop()

# =========================
# FUNGSI-FUNGSI
# =========================
def pastikan_sheet_pengumuman():
    try:
        ws = sheet.worksheet("Pengumuman")
    except:
        ws = sheet.add_worksheet(title="Pengumuman", rows=1000, cols=4)
        ws.append_row(["Tanggal", "Judul", "Isi", "MasaAktifJam"])
    return ws

def kirim_wa_fonnte(target, pesan):
    if not WA_AUTO: return False, "WA_AUTO masih OFF"
    
    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_TOKEN}
    data = {"target": str(target), "message": pesan, "countryCode": "62"}
    
    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        return r.status_code == 200, r.text
    except Exception as e:
        return False, str(e)

def ambil_pengumuman_aktif():
    ws = pastikan_sheet_pengumuman()
    data = ws.get_all_records()
    aktif = []
    for row in data:
        try:
            tanggal_text = str(row.get("Tanggal", "")).strip()
            masa_aktif = int(row.get("MasaAktifJam", 0))
            tanggal = datetime.strptime(tanggal_text, "%d/%m/%Y %H:%M")
            expired = tanggal + timedelta(hours=masa_aktif)
            if datetime.now() <= expired:
                aktif.append(row)
        except: pass
    return aktif

def simpan_pengumuman(judul, isi, masa_aktif_jam):
    ws = pastikan_sheet_pengumuman()
    tanggal = datetime.now().strftime("%d/%m/%Y %H:%M")
    ws.append_row([tanggal, judul, isi, masa_aktif_jam])
    
    pesan_wa = f"📢 PENGUMUMAN MASJID JAMI AL-FALAH\n\n{judul}\n\n{isi}\n\n🕌 Masjid Jami Al-Falah\nKp. Caringin RT/RW 005/005\nDesa Sukasari, Karangtengah, Cianjur"
    
    return kirim_wa_fonnte(NOMOR_MASJID, pesan_wa)

# =========================
# UI SIDEBAR & MENU
# =========================
st.sidebar.title("🕌 AL-FALAH V19.2")
menu = st.sidebar.radio("Menu", ["Dashboard", "Admin Pengumuman", "Tes WA Fonte"])

if menu == "Dashboard":
    st.title("🕌 APP MASJID JAMI AL-FALAH")
    st.caption("Kp. Caringin RT/RW 005/005 Desa Sukasari")
    st.markdown("---")
    pengumuman = ambil_pengumuman_aktif()
    if pengumuman:
        for p in reversed(pengumuman):
            st.info(f"### {p.get('Judul', '')}\n\n{p.get('Isi', '')}")
    else:
        st.info("Belum ada pengumuman aktif.")

elif menu == "Admin Pengumuman":
    st.title("📢 Admin Pengumuman Masjid")
    jenis = st.selectbox("Jenis Pengumuman", ["Syahriahan", "Pengajian", "Jumat", "Umum"])
    
    if jenis == "Syahriahan":
        judul_default = "Syahriahan Masjid Jami Al-Falah"
        isi_default = "Assalamu'alaikum...\n\nInsya Allah akan dilaksanakan kegiatan Syahriahan Masjid Jami Al-Falah.\n\n🗓 Kamis malam Jumat\n🕖 Ba'da Isya\n📍 Masjid Jami Al-Falah"
    else:
        judul_default, isi_default = "", ""

    judul = st.text_input("Judul", value=judul_default)
    isi = st.text_area("Isi Pengumuman", value=isi_default, height=280)
    masa_aktif = st.number_input("Masa Aktif di Dashboard / jam", min_value=1, max_value=720, value=168)

    if st.button("💾 Simpan & Kirim WA"):
        if not judul or not isi:
            st.warning("Judul dan isi wajib diisi.")
        else:
            sukses, respon = simpan_pengumuman(judul, isi, masa_aktif)
            st.success("✅ Pengumuman berhasil disimpan.")
            if sukses: st.success("✅ WA berhasil dikirim.")
            else: st.error(f"❌ WA gagal dikirim: {respon}")

elif menu == "Tes WA Fonte":
    st.title("📲 Tes WA Fonte")
    target = st.text_input("Nomor tujuan", value=NOMOR_MASJID)
    pesan = st.text_area("Pesan Tes", value="Assalamu'alaikum. Tes kirim pesan dari APP MASJID.")
    if st.button("🚀 Kirim Tes WA"):
        sukses, respon = kirim_wa_fonnte(target, pesan)
        if sukses: st.success("✅ Terkirim.")
        else: st.error(f"❌ Gagal: {respon}")
