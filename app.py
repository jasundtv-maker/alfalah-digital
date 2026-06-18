import streamlit as st
import gspread
import requests
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials

# =========================================================
# APP MASJID JAMI AL-FALAH V19.2
# Fokus:
# - Dashboard Pengumuman
# - Admin Pengumuman
# - Simpan ke Sheet "Pengumuman"
# - Tes WA Fonte/Fonnte nomor masjid baru
# =========================================================

# =========================
# KONFIGURASI APP
# =========================
st.set_page_config(
    page_title="APP MASJID JAMI AL-FALAH V19.2",
    page_icon="🕌",
    layout="wide"
)

WA_AUTO = True
NOMOR_MASJID = "087742958453"
NAMA_SPREADSHEET = "Data Jamaah Al-Falah"

# Secrets yang dipakai:
# FONNTE_TOKEN = "token_fonnte_akang"
# FONTE_DEVICE_ID = "6287742958453"  # boleh ada, tidak wajib dipakai di kode ini
FONNTE_TOKEN = st.secrets.get("FONNTE_TOKEN", "")

# =========================
# KONEKSI GOOGLE SHEET
# =========================
@st.cache_resource
def koneksi_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Format secrets akang: type, project_id, private_key, client_email, dll
    # langsung di root secrets, bukan [gcp_service_account]
    creds = Credentials.from_service_account_info(
        dict(st.secrets),
        scopes=scope
    )

    client = gspread.authorize(creds)

    # Tidak pakai SHEET_ID agar tidak error 404 kalau SHEET_ID kosong
    return client.open(NAMA_SPREADSHEET)


try:
    sheet = koneksi_sheet()
except Exception as e:
    st.error("❌ Gagal koneksi ke Google Sheet.")
    st.warning(
        "Pastikan nama spreadsheet benar: Data Jamaah Al-Falah, "
        "dan service account sudah diberi akses Editor ke Google Sheet."
    )
    st.code(str(e))
    st.stop()


# =========================
# PASTIKAN SHEET PENGUMUMAN ADA
# =========================
def pastikan_sheet_pengumuman():
    try:
        ws = sheet.worksheet("Pengumuman")
    except Exception:
        ws = sheet.add_worksheet(
            title="Pengumuman",
            rows=1000,
            cols=4
        )
        ws.append_row([
            "Tanggal",
            "Judul",
            "Isi",
            "MasaAktifJam"
        ])

    return ws


# =========================
# KIRIM WA FONNTE / FONTE
# =========================
def kirim_wa_fonnte(target, pesan):
    if not WA_AUTO:
        return False, "WA_AUTO masih OFF"

    if not FONNTE_TOKEN:
        return False, "FONNTE_TOKEN belum diisi di Streamlit Secrets"

    url = "https://api.fonnte.com/send"

    headers = {
        "Authorization": FONNTE_TOKEN
    }

    data = {
        "target": str(target),
        "message": pesan,
        "countryCode": "62"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            timeout=30
        )

        return response.status_code == 200, response.text

    except Exception as e:
        return False, str(e)


# =========================
# AMBIL PENGUMUMAN AKTIF
# =========================
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

        except Exception:
            continue

    return aktif


# =========================
# SIMPAN PENGUMUMAN
# =========================
def simpan_pengumuman(judul, isi, masa_aktif_jam):
    ws = pastikan_sheet_pengumuman()

    tanggal = datetime.now().strftime("%d/%m/%Y %H:%M")

    ws.append_row([
        tanggal,
        judul,
        isi,
        masa_aktif_jam
    ])

    pesan_wa = f"""📢 PENGUMUMAN MASJID JAMI AL-FALAH

{judul}

{isi}

🕌 Masjid Jami Al-Falah
Kp. Caringin RT/RW 005/005
Desa Sukasari, Karangtengah, Cianjur
"""

    sukses, respon = kirim_wa_fonnte(
        NOMOR_MASJID,
        pesan_wa
    )

    return sukses, respon


# =========================
# SIDEBAR MENU
# =========================
st.sidebar.title("🕌 AL-FALAH V19.2")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Admin Pengumuman",
        "Tes WA Fonte"
    ]
)


# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("🕌 APP MASJID JAMI AL-FALAH")
    st.caption("Kp. Caringin RT/RW 005/005 Desa Sukasari")

    st.markdown("---")

    pengumuman = ambil_pengumuman_aktif()

    if pengumuman:
        st.subheader("📢 Pengumuman Masjid")

        for p in reversed(pengumuman):
            st.info(f"""
### {p.get("Judul", "")}

{p.get("Isi", "")}
""")
    else:
        st.info("Belum ada pengumuman aktif.")


# =========================
# ADMIN PENGUMUMAN
# =========================
elif menu == "Admin Pengumuman":
    st.title("📢 Admin Pengumuman Masjid")

    jenis = st.selectbox(
        "Jenis Pengumuman",
        [
            "Syahriahan",
            "Pengajian",
            "Jumat",
            "Umum"
        ]
    )

    if jenis == "Syahriahan":
        judul_default = "Syahriahan Masjid Jami Al-Falah"
        isi_default = """Assalamu'alaikum Warahmatullahi Wabarakatuh

Insya Allah akan dilaksanakan kegiatan Syahriahan Masjid Jami Al-Falah pada:

🗓 Kamis malam Jumat
🕖 Ba'da Isya
📍 Masjid Jami Al-Falah Kp. Caringin

Kami mengundang seluruh jamaah dan masyarakat untuk hadir bersama-sama dalam pembacaan sholawat, dzikir, dan doa.

Jazakumullahu khairan.

Wassalamu'alaikum Warahmatullahi Wabarakatuh."""
    elif jenis == "Pengajian":
        judul_default = "Pengajian Masjid Jami Al-Falah"
        isi_default = """Assalamu'alaikum Warahmatullahi Wabarakatuh

Insya Allah akan dilaksanakan kegiatan pengajian di Masjid Jami Al-Falah.

Kami mengundang seluruh jamaah dan masyarakat untuk hadir.

Wassalamu'alaikum Warahmatullahi Wabarakatuh."""
    elif jenis == "Jumat":
        judul_default = "Informasi Shalat Jumat"
        isi_default = """Assalamu'alaikum Warahmatullahi Wabarakatuh

Diberitahukan kepada seluruh jamaah Masjid Jami Al-Falah mengenai pelaksanaan Shalat Jumat.

Mohon hadir tepat waktu.

Wassalamu'alaikum Warahmatullahi Wabarakatuh."""
    else:
        judul_default = ""
        isi_default = ""

    judul = st.text_input(
        "Judul",
        value=judul_default
    )

    isi = st.text_area(
        "Isi Pengumuman",
        value=isi_default,
        height=280
    )

    masa_aktif = st.number_input(
        "Masa Aktif di Dashboard / jam",
        min_value=1,
        max_value=720,
        value=168
    )

    if st.button("💾 Simpan & Kirim WA"):
        if not judul.strip() or not isi.strip():
            st.warning("Judul dan isi pengumuman wajib diisi.")
        else:
            sukses, respon = simpan_pengumuman(
                judul,
                isi,
                masa_aktif
            )

            st.success("✅ Pengumuman berhasil disimpan ke Sheet.")

            if sukses:
                st.success("✅ WA berhasil dikirim dari nomor masjid.")
            else:
                st.error("❌ WA gagal dikirim.")

            st.code(respon)


# =========================
# TES WA FONTE
# =========================
elif menu == "Tes WA Fonte":
    st.title("📲 Tes WA Fonte Nomor Masjid")

    st.info(f"Nomor masjid aktif: {NOMOR_MASJID}")

    target = st.text_input(
        "Nomor tujuan tes",
        value=NOMOR_MASJID
    )

    pesan = st.text_area(
        "Pesan Tes",
        value="""Assalamu'alaikum.

Tes WA otomatis dari APP MASJID JAMI AL-FALAH V19.2.

Jika pesan ini masuk, berarti nomor baru masjid sudah berhasil terhubung dengan Fonte/Fonnte.

🕌 Masjid Jami Al-Falah""",
        height=220
    )

    if st.button("🚀 Kirim Tes WA Sekarang"):
        sukses, respon = kirim_wa_fonnte(
            target,
            pesan
        )

        if sukses:
            st.success("✅ Tes WA berhasil dikirim.")
        else:
            st.error("❌ Tes WA gagal.")

        st.code(respon)
