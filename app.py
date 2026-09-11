import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Configurazione Pagina e Stile ---
st.set_page_config(page_title="Turni Navarolo", layout="centered")

st.markdown("""
<style>
    /* Stile compatto per il titolo */
    h1 { font-size: 1.9em !important; margin-bottom: 0px !important; padding-bottom: 0px !important; }
    /* Forza le colonne dei pulsanti a stare in linea */
    [data-testid="column"] {
        width: calc(33.333% - 8px) !important;
        flex: 1 1 calc(33.333% - 8px) !important;
        min-width: calc(33% - 8px) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌊 Turni Irrigui Storti")

# --- Dati e Funzioni ---
@st.cache_data
def get_initial_data():
    """Carica i dati di partenza dei canali basati sul file PARTENZE 2026.xlsx."""
    return pd.DataFrame([
        {"Canale": "Corte Emilia", "Ore": 50.0, "Data_Partenza": "02/05/2026", "Ora_Partenza": "20:00"},
        {"Canale": "Pirolo", "Ore": 50.0, "Data_Partenza": "04/05/2026", "Ora_Partenza": "22:00"},
        {"Canale": "Cà Lame", "Ore": 34.0, "Data_Partenza": "07/05/2026", "Ora_Partenza": "00:00"},
        {"Canale": "Madonna Lame", "Ore": 213.0, "Data_Partenza": "08/05/2026", "Ora_Partenza": "10:00"},
        {"Canale": "Cividale Nord A", "Ore": 99.0, "Data_Partenza": "25/04/2026", "Ora_Partenza": "07:00"},
        {"Canale": "Belvedere Nord", "Ore": 41.0, "Data_Partenza": "29/04/2026", "Ora_Partenza": "10:00"},
        {"Canale": "Cividale Nord vecchia", "Ore": 81.0, "Data_Partenza": "14/04/2026", "Ora_Partenza": "11:00"},
    ])

@st.cache_data
def calcola_turni(df_canali, fine_stagione, giorni_ciclo):
    turni = []
    for _, row in df_canali.dropna().iterrows():
        try:
            start_dt = datetime.strptime(f"{row['Data_Partenza']} {row['Ora_Partenza']}", "%d/%m/%Y %H:%M")
            durata = float(row['Ore'])
            current_start = start_dt
            while current_start < fine_stagione:
                end_turn = current_start + timedelta(hours=durata)
                turni.append({"Canale": row['Canale'], "Inizio": current_start, "Fine": end_turn})
                current_start += timedelta(days=giorni_ciclo)
        except (ValueError, TypeError):
            continue
    return pd.DataFrame(turni)

# --- Inizializzazione Stato ---
if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()
if 'data_selezionata' not in st.session_state:
    st.session_state.data_selezionata = datetime.now().date()

# --- Menu a scomparsa ---
with st.expander("⚙️ Impostazioni e Modifica Dati"):
    d_fine = st.date_input("Fine Stagione:", datetime(2026, 9, 22).date(), format="DD/MM/YYYY")
    ciclo_giorni = st.number_input("Ogni quanti giorni riparte il ciclo?", min_value=1, value=14)
    if st.button("♻️ Reset Dati"):
        st.session_state.df_canali = get_initial_data()
        st.rerun()
    st.markdown("---")
    edited_df = st.data_editor(st.session_state.df_canali, num_rows="dynamic", use_container_width=True, hide_index=True)
    st.session_state.df_canali = edited_df

end_stagione = datetime.combine(d_fine, datetime.max.time())
df_risultato = calcola_turni(st.session_state.df_canali, end_stagione, ciclo_giorni)

# --- Interfaccia Principale ---
st.markdown("---")
if not df_risultato.empty:
    st.subheader("📅 Programma del Giorno")

    # Pulsanti di navigazione su una riga
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ IERI", use_container_width=True):
            st.session_state.data_selezionata -= timedelta(days=1)
            st.rerun()
    with col2:
        # CORREZIONE: Ora il pulsante imposta la data odierna reale
        if st.button("🗓️ OGGI", use_container_width=True):
            st.session_state.data_selezionata = datetime.now().date()
            st.rerun()
    with col3:
        if st.button("DOMANI ➡️", use_container_width=True):
            st.session_state.data_selezionata += timedelta(days=1)
            st.rerun()

    # Calendario per data specifica
    giorno_selezionato = st.date_input("O vai a una data specifica:", value=st.session_state.data_selezionata, format="DD/MM/YYYY", label_visibility="collapsed")
    if giorno_selezionato != st.session_state.data_selezionata:
        st.session_state.data_selezionata = giorno_selezionato
        st.rerun()
    
    inizio_giorno = datetime.combine(giorno_selezionato, datetime.min.time())
    fine_giorno = inizio_giorno + timedelta(days=1)
    
    turni_del_giorno = df_risultato[(df_risultato['Inizio'] < fine_giorno) & (df_risultato['Fine'] > inizio_giorno)].sort_values(by='Inizio')
    
    st.markdown("---")
    if turni_del_giorno.empty:
        st.success(f"✅ Nessun canale in funzione il {giorno_selezionato.strftime('%d/%m/%Y')}.")
    else:
        for _, turno in turni_del_giorno.iterrows():
            st.markdown(f"""
            <div style="border-left: 8px solid #1f77b4; background-color: #f0f2f6; padding: 12px; margin-bottom: 8px; border-radius: 5px;">
                <h3 style="margin: 0 0 8px 0;">{turno['Canale']}</h3>
                <p style="margin:0;">🟢 <b>Apertura:</b> {turno['Inizio'].strftime('%d/%m %H:%M')}</p>
                <p style="margin:0;">🔴 <b>Chiusura:</b> {turno['Fine'].strftime('%d/%m %H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("Dati non sufficienti per il calcolo. Controlla le impostazioni.")

