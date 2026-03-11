import streamlit as st

import pandas as pd

import gspread

import plotly.graph_objects as go

from datetime import datetime

import json



# Konfigurasi Halaman & Tema Mobile-App

st.set_page_config(page_title="Portfolio Pemeliharaan Sipil", layout="centered", initial_sidebar_state="collapsed")



st.markdown("""

    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    

    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; background-color: #f8fafc !important; color: #0f172a !important; }

    

    /* Styling Dropdown Multi-Project */

    .project-selector-container { background-color: #1e3a8a; padding: 15px; border-radius: 12px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }

    .project-selector-title { color: #ffffff; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }

    div[data-baseweb="select"] > div { background-color: #ffffff !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 16px !important; color: #0f172a !important; cursor: pointer !important; }

    

    .app-header { background-color: #ffffff !important; padding: 15px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; text-align: center; border: 1px solid #e2e8f0; }

    .app-title { color: #0f172a !important; font-size: 16px; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.5px; }

    .app-subtitle { color: #475569 !important; font-size: 12px; font-weight: 600; }

    

    .metric-container { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 15px; }

    .metric-card { flex: 1; background-color: #ffffff !important; padding: 12px 5px; border-radius: 10px; border: 1px solid #cbd5e1; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

    .metric-card.normal { border-top: 4px solid #3b82f6; }

    .metric-card.alert { border-top: 4px solid #ef4444; }

    .metric-label { font-size: 10px; color: #475569 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

    .metric-val { font-size: 18px; font-weight: 800; color: #0f172a !important; margin-top: 4px; }

    

    .streamlit-expanderHeader { background-color: #ffffff !important; color: #1e3a8a !important; font-size: 14px !important; font-weight: 700 !important; border-radius: 8px; border: 1px solid #e2e8f0; }

    div[data-testid="stExpanderDetails"] { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #e2e8f0; border-top: none; padding: 10px; border-radius: 0 0 8px 8px; }

    

    .stTable { font-size: 12px !important; background-color: #ffffff !important; }

    th { background-color: #e2e8f0 !important; color: #0f172a !important; font-weight: 700 !important; border-bottom: 2px solid #cbd5e1 !important; }

    td { background-color: #ffffff !important; color: #0f172a !important; border-bottom: 1px solid #e2e8f0 !important; padding: 8px !important; }

    

    header { display: none !important; } #MainMenu { display: none !important; } footer { display: none !important; }

    

    .sign-container { display: flex; justify-content: space-between; text-align: center; font-size: 10px; color: #475569 !important; margin-top: 20px; padding-top: 15px; border-top: 1px solid #cbd5e1; font-weight: 600; }

    </style>

""", unsafe_allow_html=True)



try:

    kredensial = json.loads(st.secrets["gcp_service_account"])

    gc = gspread.service_account_from_dict(kredensial)

    

    # =====================================================================

    # PENGATURAN DATABASE MULTI-PROJECT

    # Tambahkan nama project dan nama file Google Sheets-nya di bawah ini:

    # =====================================================================

    DAFTAR_PROJECT = {

        "PLTA Ubrug Tahap 2": "Master Data Project - Sipil Pemeliharaan PLN IP UBP SGL",

        "Project Jembatan Cikuya (Contoh)": "File Spreadsheet Cikuya",

        "Project Bendungan (Contoh)": "File Spreadsheet Bendungan"

    }



    # UI Dropdown Pemilihan Project

    st.markdown("<div class='project-selector-container'><div class='project-selector-title'>PILIH PORTFOLIO PROYEK</div>", unsafe_allow_html=True)

    selected_project = st.selectbox("", list(DAFTAR_PROJECT.keys()), label_visibility="collapsed")

    st.markdown("</div>", unsafe_allow_html=True)



    # Buka Google Sheets berdasarkan project yang dipilih

    # Perintah error handling jika file belum ada

    try:

        sh = gc.open(DAFTAR_PROJECT[selected_project])

    except gspread.exceptions.SpreadsheetNotFound:

        st.error(f"File Google Sheets '{DAFTAR_PROJECT[selected_project]}' belum dibuat atau belum dibagikan ke email Service Account. Silakan buat filenya terlebih dahulu.")

        st.stop()



    def get_df(name):

        return pd.DataFrame(sh.worksheet(name).get_all_records())



    df_master = get_df("DATA_MASTER_PROYEK")

    df_progress = get_df("PROGRESS_GLOBAL")

    df_realisasi = get_df("REALISASI_PEKERJAAN")

    df_qc = get_df("QUALITY_CONTROL_DAN_TEMUAN")

    df_rencana = get_df("RENCANA_MINGGU_DEPAN")

    df_admin = get_df("STATUS_APPROVAL_ADMINISTRASI")



    if not df_master.empty:

        m = df_master.iloc[0]

        st.markdown(f"""

        <div class="app-header">

            <div class="app-title">{m['Nama_Pekerjaan']}</div>

            <div class="app-subtitle">

                Kontrak: {m['No_Kontrak']} <br> Target: {m['Target_Selesai']} | Update: {datetime.now().strftime('%d %b %Y')}

            </div>

        </div>

        """, unsafe_allow_html=True)
