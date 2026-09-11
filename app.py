import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Turni Navarolo", layout="centered")
st.title("🌊 Turni Irrigui")

# --- Dati Iniziali ---
def get_initial_data():
    return pd.DataFrame([
        {"Gr.": 1, "Canale": "Corte Emilia", "Ore": 24.0, "l/s": 120},
        {"Gr.": 1, "Canale": "Pirolo", "Ore": 18.0, "l/s": 90},
        {"Gr.": 2, "Canale": "Cividale Nord A", "Ore": 48.0, "l/s": 100},
        {"Gr.": 2, "Canale": "Cividale Nord Vecchia", "Ore": 12.0, "l/s": 70},
        {"Gr.": 3, "Canale": "OSSOLA 2 RID", "Ore": 12.0, "l/s": 80},
        {"Gr.": 3, "Canale": "MANZOGLIO RID", "Ore": 36.0, "l/s": 150},
        {"Gr.": 4, "Canale": "BREDA 3", "Ore": 12.0, "l/s": 50},
        {"Gr.": 4, "Canale": "BREDA 4", "Ore": 12.0, "l/s": 40},
    ])

if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()

# --- Menu Impostazioni ---
with st.expander("⚙️ Impostazioni", expanded=False):
    d_inizio = st.date_input("Inizio Stagione:", datetime(2026, 4, 1).date(), format="DD/MM/YYYY")
    t_inizio = st.time_input("Ora Inizio:", datetime(2026, 4, 1, 8, 0).time())
    d_fine = st.date_input("Fine Stagione:", datetime(2026, 9, 22).date(), format="DD/MM/YYYY")
    
    if st.button("♻️ Reset Dati"):
        st.session_state.df_canali = get_initial_data()
        st.rerun()

start_stagione = datetime.combine(d_inizio, t_inizio)
end_stagione = datetime.combine(d_fine, datetime.min.time())

# --- Tabella Modificabile ---
with st.expander("📝 Modifica Canali", expanded=True):
    edited_df = st.data_editor(
        st.session_state.df_canali,
        num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "Gr.": st.column_config.NumberColumn("Gr.", help="Ordine di esecuzione dei gruppi", required=True),
            "Canale": st.column_config.TextColumn("Canale", required=True),
            "Ore": st.column_config.NumberColumn("Ore", required=True),
            "l/s": st.column_config.NumberColumn("l/s"),
        }
    )
    st.session_state.df_canali = edited_df

# --- Motore di Calcolo a Cascata Unica ---
@st.cache_data
def calcola_cascata_unica(df_canali, start_dt, end_dt):
    turni = []
    df_valid = df_canali.dropna(subset=['Gr.', 'Ore', 'Canale']).copy()
    df_valid['Gr.'] = pd.to_numeric(df_valid['Gr.'], errors='coerce')
    df_valid['Ore'] = pd.to_numeric(df_valid['Ore'], errors='coerce')
    df_valid = df_valid.dropna(subset=['Gr.', 'Ore'])
    df_valid = df_valid.sort_values(by=['Gr.', 'Canale']) # Ordina per gruppo e poi per nome

    if df_valid.empty or df_valid['Ore'].sum() <= 0:
        return pd.DataFrame()

    tempo_corrente = start_dt
    while tempo_corrente < end_dt:
        for _, row in df_valid.iterrows():
            durata = float(row['Ore'])
            if durata <= 0: continue
            
            fine_turno = tempo_corrente + timedelta(hours=durata)
            if tempo_corrente < end_dt:
                turni.append({
                    "Gruppo": int(row['Gr.']), "Canale": row['Canale'],
                    "Inizio": tempo_corrente, "Fine": min(fine_turno, end_dt),
                    "l/s": row.get('l/s', 0)
                })
            tempo_corrente = fine_turno
            # Se siamo andati oltre la fine, interrompi il ciclo interno
            if tempo_corrente >= end_dt:
                break
    
    return pd.DataFrame(turni)

# --- Visualizzazione Mobile ---
df_risultato = calcola_cascata_unica(st.session_state.df_canali, start_stagione, end_stagione)

st.markdown("---")
if not df_risultato.empty:
    st.subheader("📅 Programma del Giorno")
    
    giorno_selezionato = st.date_input("Mostra turni per il giorno:", datetime.now().date(), format="DD/MM/YYYY")
    
    inizio_giorno = datetime.combine(giorno_selezionato, datetime.min.time())
    fine_giorno = inizio_giorno + timedelta(days=1)
    
    turni_del_giorno = df_risultato[
        (df_risultato['Inizio'] < fine_giorno) & (df_risultato['Fine'] > inizio_giorno)
    ].sort_values(by='Inizio')
    
    if turni_del_giorno.empty:
        st.success("✅ Nessun canale in funzione in questa data.")
    else:
        colori = {1: "#1f77b4", 2: "#ff7f0e", 3: "#2ca02c", 4: "#d62728", 5: "#9467bd"}
        
        for _, turno in turni_del_giorno.iterrows():
            colore_gruppo = colori.get(turno['Gruppo'], "#333")
            ora_in = turno['Inizio'].strftime('%d/%m ore %H:%M')
            ora_fi = turno['Fine'].strftime('%d/%m ore %H:%M')
            
            st.markdown(f"""
            <div style="border-left: 8px solid {colore_gruppo}; background-color: #f0f2f6; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #111;">{turno['Canale']}</h3>
                <p style="font-size: 1.1em; margin:0;">🟢 <b>Apertura:</b> {ora_in}</p>
                <p style="font-size: 1.1em; margin:5px 0;">🔴 <b>Chiusura:</b> {ora_fi}</p>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("Dettaglio Completo Stagione (CSV)"):
        st.dataframe(df_risultato, hide_index=True)
        csv = df_risultato.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Intera Stagione", data=csv, file_name="orari_stagione.csv", mime="text/csv")
else:
    st.warning("Nessun dato da calcolare. Controlla le impostazioni.")

