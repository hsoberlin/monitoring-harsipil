import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from datetime import datetime

# 1. Konfigurasi Halaman & Tema Mobile-App
st.set_page_config(page_title="Monitoring PLTA Ubrug", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Reset & Font */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8fafc; }
    
    /* Header Minimalis */
    .app-header {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        text-align: center;
        border-bottom: 3px solid #1e3a8a;
    }
    .app-title { color: #0f172a; font-size: 18px; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.5px; }
    .app-subtitle { color: #64748b; font-size: 12px; font-weight: 400; }
    
    /* Flexbox Metrics untuk HP (Sejajar dalam 1 baris) */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 15px;
    }
    .metric-card {
        flex: 1;
        background: #ffffff;
        padding: 12px 5px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .metric-card.normal { border-top: 3px solid #3b82f6; }
    .metric-card.alert { border-top: 3px solid #ef4444; }
    .metric-label { font-size: 10px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-val { font-size: 18px; font-weight: 700; color: #0f172a; margin-top: 4px; }
    
    /* Styling Tabel & Expander */
    .streamlit-expanderHeader { font-size: 14px !important; font-weight: 600 !important; color: #1e3a8a !important; }
    .stTable { font-size: 11px !important; }
    th { background-color: #f1f5f9 !important; color: #334155 !important; font-weight: 600 !important; }
    td { color: #1e293b !important; padding: 6px 8px !important; }
    
    /* Sembunyikan Elemen Default */
    header { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    
    /* Tanda Tangan Flex */
    .sign-container {
        display: flex;
        justify-content: space-between;
        text-align: center;
        font-size: 10px;
        color: #475569;
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

try:
    # 2. Koneksi Google Sheets
    kredensial = json.loads(st.secrets["gcp_service_account"])
gc = gspread.service_account_from_dict(kredensial)
    sh = gc.open("Master Data Project - Sipil Pemeliharaan PLN IP UBP SGL")
    
    def get_df(name):
        return pd.DataFrame(sh.worksheet(name).get_all_records())

    df_master = get_df("DATA_MASTER_PROYEK")
    df_progress = get_df("PROGRESS_GLOBAL")
    df_realisasi = get_df("REALISASI_PEKERJAAN")
    df_qc = get_df("QUALITY_CONTROL_DAN_TEMUAN")
    df_rencana = get_df("RENCANA_MINGGU_DEPAN")
    df_admin = get_df("STATUS_APPROVAL_ADMINISTRASI")

    # --- HEADER ---
    if not df_master.empty:
        m = df_master.iloc[0]
        st.markdown(f"""
        <div class="app-header">
            <div class="app-title">{m['Nama_Pekerjaan']}</div>
            <div class="app-subtitle">
                {m['No_Kontrak']} | Target: {m['Target_Selesai']}<br>
                Update: {datetime.now().strftime('%d %b %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- METRIK UTAMA (Tampil paling atas di HP) ---
    if not df_progress.empty:
        p = df_progress.iloc[-1]
        dev_val = float(str(p['Deviasi_Persen']).replace('%',''))
        alert_class = "alert" if dev_val < 0 else "normal"
        color_val = "#ef4444" if dev_val < 0 else "#10b981"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card normal">
                <div class="metric-label">Rencana</div>
                <div class="metric-val">{p['Rencana_Persen']}%</div>
            </div>
            <div class="metric-card normal">
                <div class="metric-label">Aktual</div>
                <div class="metric-val">{p['Aktual_Persen']}%</div>
            </div>
            <div class="metric-card {alert_class}">
                <div class="metric-label">Deviasi</div>
                <div class="metric-val" style="color: {color_val};">{p['Deviasi_Persen']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- GRAFIK S-CURVE (Compact) ---
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_progress['Minggu_Ke'], y=df_progress['Rencana_Persen'], name='Rencana', line=dict(color='#3b82f6', width=2), mode='lines+markers', marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=df_progress['Minggu_Ke'], y=df_progress['Aktual_Persen'], name='Aktual', line=dict(color='#ef4444', width=2), mode='lines+markers', marker=dict(size=6)))
        
        fig.update_layout(
            height=220, # Sangat ringkas untuk HP
            margin=dict(l=10, r=10, t=5, b=5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
            xaxis=dict(tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}) # Sembunyikan toolbar plotly

    # --- MENU DETAIL (Expanders / Menu Lipat) ---
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    with st.expander("STATUS APPROVAL ADMINISTRASI (KRITIS)", expanded=True):
        if not df_admin.empty:
            st.table(df_admin)

    with st.expander("REALISASI PEKERJAAN (MINGGU 25)"):
        if not df_realisasi.empty:
            st.table(df_realisasi)

    with st.expander("QUALITY CONTROL DAN TEMUAN"):
        if not df_qc.empty:
            st.table(df_qc)

    with st.expander("RENCANA KERJA (MINGGU 26)"):
        if not df_rencana.empty:
            st.table(df_rencana)

    # --- PENGESAHAN ---
    st.markdown("""
        <div class="sign-container">
            <div style="flex: 1;">PT Solusi Paripurna Indonesia<br><br><br><br>(____________________)</div>
            <div style="flex: 1;">PT PLN (Persero) PUSMANPRO<br><br><br><br>(____________________)</div>
            <div style="flex: 1;">PT PLN IP UBP Saguling<br><br><br><br>(____________________)</div>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Gagal memuat data dari Spreadsheet. Error: {e}")

