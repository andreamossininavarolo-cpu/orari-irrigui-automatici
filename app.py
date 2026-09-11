import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Turni Navarolo", layout="centered")
st.title("🌊 Turni Irrigui Storti")

# Dizionari per la traduzione in italiano di giorni e mesi
GIORNI_IT = {
    "Monday": "lunedì", "Tuesday": "martedì", "Wednesday": "mercoledì",
    "Thursday": "giovedì", "Friday": "venerdì", "Saturday": "sabato", "Sunday": "domenica"
}

MESI_IT = {
    "January": "gennaio", "February": "febbraio", "March": "marzo", "April": "aprile",
    "May": "maggio", "June": "giugno", "July": "luglio", "August": "agosto",
    "September": "settembre", "October": "ottobre", "November": "novembre", "December": "dicembre"
}

def formatta_data_it(dt):
    """Formatta la data in italiano con il giorno a parole e il mese in grassetto HTML."""
    giorno_sett = GIORNI_IT.get(dt.strftime('%A'), dt.strftime('%A'))
    giorno_num = dt.strftime('%d')
    mese = MESI_IT.get(dt.strftime('%B'), dt.strftime('%B'))
    anno = dt.strftime('%y')
    ora = dt.strftime('%H:%M')
    return f"{giorno_sett} {giorno_num} <b>{mese}</b> '{anno} alle ore <b>{ora}</b>"

# --- Dati Iniziali Estratti dal File Ufficiale PARTENZE 2026.xlsx ---
def get_initial_data():
    return pd.DataFrame([
        {"Canale": "Corte Emilia", "Ore": 50.0, "Data_Partenza": "02/05/2026", "Ora_Partenza": "20:00"},
        {"Canale": "Pirolo", "Ore": 50.0, "Data_Partenza": "04/05/2026", "Ora_Partenza": "22:00"},
        {"Canale": "Cà Lame", "Ore": 34.0, "Data_Partenza": "07/05/2026", "Ora_Partenza": "00:00"},
        {"Canale": "Madonna Lame", "Ore": 213.0, "Data_Partenza": "08/05/2026", "Ora_Partenza": "10:00"},
        {"Canale": "Cividale Nord A", "Ore": 99.0, "Data_Partenza": "25/04/2026", "Ora_Partenza": "07:00"},
        {"Canale": "Belvedere Nord", "Ore": 41.0, "Data_Partenza": "29/04/2026", "Ora_Partenza": "10:00"},
        {"Canale": "Cividale Nord vecchia", "Ore": 81.0, "Data_Partenza": "14/04/2026", "Ora_Partenza": "11:00"},
        {"Canale": "Cò de Vanni 1°", "Ore": 58.0, "Data_Partenza": "23/04/2026", "Ora_Partenza": "02:00"},
        {"Canale": "1° Gruppo bocchette", "Ore": 80.0, "Data_Partenza": "04/05/2026", "Ora_Partenza": "11:00"},
        {"Canale": "Spineda", "Ore": 30.0, "Data_Partenza": "07/05/2026", "Ora_Partenza": "19:00"},
        {"Canale": "Ossola 2° Rid.", "Ore": 40.0, "Data_Partenza": "26/04/2026", "Ora_Partenza": "10:00"},
        {"Canale": "Agraria Rid.", "Ore": 60.0, "Data_Partenza": "28/04/2026", "Ora_Partenza": "02:00"},
        {"Canale": "Manzoglio Rid.", "Ore": 80.0, "Data_Partenza": "30/04/2026", "Ora_Partenza": "14:00"},
        {"Canale": "Fiascale Rid.", "Ore": 120.0, "Data_Partenza": "03/05/2026", "Ora_Partenza": "22:00"},
        {"Canale": "Tessagli Rid.", "Ore": 90.0, "Data_Partenza": "13/04/2026", "Ora_Partenza": "22:00"},
        {"Canale": "Roncole Rid.", "Ore": 110.0, "Data_Partenza": "17/04/2026", "Ora_Partenza": "16:00"},
        {"Canale": "Vaja Rid.", "Ore": 80.0, "Data_Partenza": "22/04/2026", "Ora_Partenza": "06:00"},
        {"Canale": "Riglio Rid.", "Ore": 140.0, "Data_Partenza": "25/04/2026", "Ora_Partenza": "14:00"},
        {"Canale": "Breda 3°", "Ore": 37.0, "Data_Partenza": "01/05/2026", "Ora_Partenza": "10:00"},
        {"Canale": "Breda 4°", "Ore": 19.0, "Data_Partenza": "02/05/2026", "Ora_Partenza": "23:00"},
        {"Canale": "Delmoncello 1° ridotta", "Ore": 70.0, "Data_Partenza": "03/05/2026", "Ora_Partenza": "18:00"},
    ])

if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()

# --- Stato della data selezionata ---
if 'data_selezionata' not in st.session_state:
    st.session_state.data_selezionata = datetime.now().date()

# --- Menu Impostazioni ---
with st.expander("⚙️ Impostazioni Stagione", expanded=False):
    d_fine = st.date_input("Fine Stagione:", datetime(2026, 9, 22).date(), format="DD/MM/YYYY")
    ciclo_giorni = st.number_input("Ogni quanti giorni riparte il ciclo?", min_value=1, value=14)
    if st.button("♻️ Reset Dati Tabella"):
        st.session_state.df_canali = get_initial_data()
        st.rerun()

end_stagione = datetime.combine(d_fine, datetime.max.time())

# --- Tabella Modificabile ---
with st.expander("📝 Modifica Partenze e Durate", expanded=False):
    edited_df = st.data_editor(
        st.session_state.df_canali,
        num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "Canale": st.column_config.TextColumn("Canale", required=True),
            "Ore": st.column_config.NumberColumn("Ore", required=True),
            "Data_Partenza": st.column_config.TextColumn("Data Prima Partenza", help="Formato GG/MM/AAAA", required=True),
            "Ora_Partenza": st.column_config.TextColumn("Ora Prima Partenza", help="Formato HH:MM", required=True),
        }
    )
    st.session_state.df_canali = edited_df

# --- Motore di Calcolo ---
@st.cache_data
def calcola_turni_da_partenze(df_canali, fine_stagione, giorni_ciclo):
    turni = []
    df_valid = df_canali.dropna().copy()
    
    for _, row in df_valid.iterrows():
        try:
            start_dt_primo_ciclo = datetime.strptime(f"{row['Data_Partenza']} {row['Ora_Partenza']}", "%d/%m/%Y %H:%M")
            durata_ore = float(row['Ore'])
            
            inizio_ciclo_canale = start_dt_primo_ciclo
            while inizio_ciclo_canale < fine_stagione:
                fine_turno = inizio_ciclo_canale + timedelta(hours=durata_ore)
                turni.append({
                    "Canale": row['Canale'],
                    "Inizio": inizio_ciclo_canale,
                    "Fine": fine_turno
                })
                inizio_ciclo_canale += timedelta(days=giorni_ciclo)
        except (ValueError, TypeError):
            continue
            
    return pd.DataFrame(turni)

df_risultato = calcola_turni_da_partenze(st.session_state.df_canali, end_stagione, ciclo_giorni)

st.markdown("---")
if not df_risultato.empty:
    st.subheader("📅 Programma del Giorno")
    
    # --- PULSANTI DI NAVIGAZIONE RAPIDA ---
    col_ieri, col_oggi, col_domani = st.columns(3)
    
    with col_ieri:
        if st.button("⬅️ IERI", use_container_width=True):
            st.session_state.data_selezionata -= timedelta(days=1)
            st.rerun()
            
    with col_oggi:
        if st.button("📅 OGGI", use_container_width=True):
            st.session_state.data_selezionata = datetime.now().date()
            st.rerun()
            
    with col_domani:
        if st.button("DOMANI ➡️", use_container_width=True):
            st.session_state.data_selezionata += timedelta(days=1)
            st.rerun()
            
    # Calendario di controllo
    giorno_selezionato = st.date_input(
        "Oppure vai a una data specifica:", 
        value=st.session_state.data_selezionata, 
        format="DD/MM/YYYY"
    )
    st.session_state.data_selezionata = giorno_selezionato
    
    inizio_giorno = datetime.combine(st.session_state.data_selezionata, datetime.min.time())
    fine_giorno = inizio_giorno + timedelta(days=1)
    
    turni_del_giorno = df_risultato[
        (df_risultato['Inizio'] < fine_giorno) & (df_risultato['Fine'] > inizio_giorno)
    ].sort_values(by='Inizio')
    
    if turni_del_giorno.empty:
        st.success(f"✅ Nessun canale in funzione il {giorno_selezionato.strftime('%d/%m/%Y')}.")
    else:
        for _, turno in turni_del_giorno.iterrows():
            ora_in = formatta_data_it(turno['Inizio'])
            ora_fi = formatta_data_it(turno['Fine'])
            
            # Icone cerchio HTML ad alto contrasto e brillantezza
            pallino_verde = '<span style="display:inline-block; width:15px; height:15px; background-color:#00FF00; border-radius:50%; border:2px solid #005000; margin-right:8px; vertical-align:middle; box-shadow: 0px 0px 4px #00FF00;"></span>'
            pallino_rosso = '<span style="display:inline-block; width:15px; height:15px; background-color:#FF0000; border-radius:50%; border:2px solid #500000; margin-right:8px; vertical-align:middle; box-shadow: 0px 0px 4px #FF0000;"></span>'
            
            st.markdown(f"""
            <div style="border-left: 8px solid #1f77b4; background-color: #f0f2f6; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                <h3 style="margin: 0 0 12px 0; color: #111; font-weight: bold; font-size: 1.3em;">{turno['Canale']}</h3>
                <p style="font-size: 1.15em; margin: 0 0 8px 0; display: flex; align-items: center;">
                    {pallino_verde} <span style="vertical-align: middle;"><b>Apertura:</b> {ora_in}</span>
                </p>
                <p style="font-size: 1.15em; margin: 0; display: flex; align-items: center;">
                    {pallino_rosso} <span style="vertical-align: middle;"><b>Chiusura:</b> {ora_fi}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("Dettaglio Completo Stagione (CSV)"):
        st.dataframe(df_risultato.style.format({"Inizio": "{:%d/%m/%Y %H:%M}", "Fine": "{:%d/%m/%Y %H:%M}"}), hide_index=True)
        csv = df_risultato.to_csv(index=False, date_format='%d/%m/%Y %H:%M').encode('utf-8')
        st.download_button("📥 Scarica Intera Stagione", data=csv, file_name="orari_stagione.csv", mime="text/csv")
else:
    st.warning("Nessun dato da calcolare. Controlla la tabella delle partenze.")
