import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from datetime import datetime
import json

# Konfigurasi Halaman & Tema Mobile-App (Full Version)
st.set_page_config(page_title="Portfolio Pemeliharaan Sipil", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], .stApp { 
        font-family: 'Inter', sans-serif; 
        background-color: #f8fafc !important; 
        color: #0f172a !important; 
    }
    
    /* Header Selector */
    .project-selector-container { 
        background-color: #1e3a8a; 
        padding: 15px; 
        border-radius: 12px; 
        margin-bottom: 15px; 
        text-align: center; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    }
    .project-selector-title { color: #ffffff; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    
    /* Card Styling */
    .app-header { background-color: #ffffff !important; padding: 15px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 15px; text-align: center; border-bottom: 3px solid #1e3a8a; }
    .app-title { color: #0f172a !important; font-size: 15px; font-weight: 700; line-height: 1.4; }
    .app-subtitle { color: #475569 !important; font-size: 11px; font-weight: 600; margin-top: 5px; }
    
    /* Metrics */
    .metric-container { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 15px; }
    .metric-card { flex: 1; background-color: #ffffff !important; padding: 10px 4px; border-radius: 10px; border: 1px solid #cbd5e1; text-align: center; }
    .metric-card.alert { border-top: 4px solid #ef4444; }
    .metric-card.normal { border-top: 4px solid #3b82f6; }
    .metric-label { font-size: 9px; color: #64748b !important; font-weight: 700; text-transform: uppercase; }
    .metric-val { font-size: 17px; font-weight: 800; color: #0f172a !important; }
    
    /* Tabel Tanpa Singkatan */
    .stTable { font-size: 11px !important; }
    th { background-color: #f1f5f9 !important; color: #1e293b !important; font-weight: 700 !important; }
    
    /* Signature Area */
    .sign-container { 
        display: block; 
        text-align: center; 
        font-size: 10px; 
        color: #475569 !important; 
        margin-top: 25px; 
        padding-top: 15px; 
        border-top: 1px solid #cbd5e1; 
    }
    .sign-box { margin-bottom: 20px; font-weight: 700; }
    
    header { display: none !important; } #MainMenu { display: none !important; } footer { display: none !important; }
    </style>
""", unsafe_allow_html=True)

try:
    # Koneksi Secrets
    kredensial = json.loads(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(kredensial)
    
    DAFTAR_PROJECT = {
        "PLTA Ubrug Tahap 2": "Master Data Project - Sipil Pemeliharaan PLN IP UBP SGL",
        "Pekerjaan Sipil Lainnya": "Master Data Baru"
    }

    st.markdown("<div class='project-selector-container'><div class='project-selector-title'>DAFTAR PROYEK PEMELIHARAAN SIPIL</div>", unsafe_allow_html=True)
    selected_project = st.selectbox("", list(DAFTAR_PROJECT.keys()), label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    sh = gc.open(DAFTAR_PROJECT[selected_project])
    
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
                {m['No_Kontrak']} <br> 
                Target Selesai: {m['Target_Selesai']} | Update: {datetime.now().strftime('%d %b %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if not df_progress.empty:
        p = df_progress.iloc[-1]
        dev_val = float(str(p['Deviasi_Persen']).replace('%',''))
        color_val = "#ef4444" if dev_val < 0 else "#10b981"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card normal"><div class="metric-label">Rencana</div><div class="metric-val">{p['Rencana_Persen']}%</div></div>
            <div class="metric-card normal"><div class="metric-label">Aktual</div><div class="metric-val">{p['Aktual_Persen']}%</div></div>
            <div class="metric-card {'alert' if dev_val < 0 else 'normal'}">
                <div class="metric-label">Deviasi</div>
                <div class="metric-val" style="color: {color_val};">{p['Deviasi_Persen']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Tabs Detail
    with st.expander("1. REALISASI PEKERJAAN", expanded=True):
        if not df_realisasi.empty: st.table(df_realisasi)
    with st.expander("2. QUALITY CONTROL DAN TEMUAN"):
        if not df_qc.empty: st.table(df_qc)
    with st.expander("3. RENCANA KERJA MINGGU DEPAN"):
        if not df_rencana.empty: st.table(df_rencana)
    with st.expander("4. STATUS ADMINISTRASI & PENAGIHAN"):
        if not df_admin.empty: st.table(df_admin)

    # Signature Area (Tanpa Singkatan)
    st.markdown(f"""
        <div class="sign-container">
            <div class="sign-box">PT Solusi Paripurna Indonesia<br><br><br>(____________________)</div>
            <div class="sign-box">PT PLN (Persero) PUSMANPRO UPMK I<br><br><br>(____________________)</div>
            <div class="sign-box">PT PLN Indonesia Power UBP Saguling<br><br><br>(____________________)</div>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Data tidak ditemukan. Silakan cek Nama File di Google Sheets.")
