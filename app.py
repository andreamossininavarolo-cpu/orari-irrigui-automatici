import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Turni Navarolo", layout="centered")
st.title("🌊 Turni Irrigui Storti")

# --- Dati Iniziali Estratti dal File Ufficiale PARTENZE 2026.xlsx ---
def get_initial_data():
    """
    Questa funzione contiene l'esatto elenco e le durate delle competenze
    estratte dal file PARTENZE 2026.xlsx.
    L'ordine numerico è fondamentale per la sequenza a cascata.
    """
    return pd.DataFrame([
        {"Ordine": 1, "Canale": "Corte Emilia", "Ore": 50.0},
        {"Ordine": 2, "Canale": "Pirolo", "Ore": 50.0},
        {"Ordine": 3, "Canale": "Pirolo Rid.", "Ore": 0.0}, # Durata 0, verrà saltato
        {"Ordine": 4, "Canale": "Cà Lame", "Ore": 34.0},
        {"Ordine": 5, "Canale": "Madonna Lame", "Ore": 213.0},
        {"Ordine": 6, "Canale": "Madonna Lame ridotta", "Ore": 72.0},
        {"Ordine": 7, "Canale": "Cividale Nord A", "Ore": 99.0},
        {"Ordine": 8, "Canale": "Belvedere Nord", "Ore": 41.0},
        {"Ordine": 9, "Canale": "Belvedere Nord rid", "Ore": 150.0},
        {"Ordine": 10, "Canale": "Cividale Nord vecchia rid.", "Ore": 50.0},
        {"Ordine": 11, "Canale": "Cividale Nord vecchia", "Ore": 81.0},
        {"Ordine": 12, "Canale": "Cividale Nord vecchia Rid Pvot", "Ore": 50.0},
        {"Ordine": 13, "Canale": "Cò de Vanni 1°", "Ore": 58.0},
        {"Ordine": 14, "Canale": "Cò de Vanni 2°", "Ore": 180.0},
        {"Ordine": 15, "Canale": "Cò de Vanni 2° Rid.", "Ore": 35.0},
        {"Ordine": 16, "Canale": "1° Gruppo bocchette", "Ore": 80.0},
        {"Ordine": 17, "Canale": "Spineda", "Ore": 30.0},
        {"Ordine": 18, "Canale": "Spineda Rid.", "Ore": 80.0},
        {"Ordine": 19, "Canale": "Fornace Rid.", "Ore": 10.0},
        {"Ordine": 20, "Canale": "S.Fiore 1°", "Ore": 10.0},
        {"Ordine": 21, "Canale": "S.Fiore 1° Rid.", "Ore": 165.0},
        {"Ordine": 22, "Canale": "S.Fiore 2°.", "Ore": 30.0},
        {"Ordine": 23, "Canale": "S.Fiore 2° Rid.", "Ore": 80.0},
        {"Ordine": 24, "Canale": "Cà de Bottoli rid.", "Ore": 40.0},
        {"Ordine": 25, "Canale": "Sec.Pomara Rid.", "Ore": 150.0},
        {"Ordine": 26, "Canale": "Pomara Rid.", "Ore": 35.0},
        {"Ordine": 27, "Canale": "Orti Rid.", "Ore": 90.0},
        {"Ordine": 28, "Canale": "S.Pietro", "Ore": 67.0},
        {"Ordine": 29, "Canale": "S.Pietro Rid.", "Ore": 90.0},
        {"Ordine": 30, "Canale": "Ossola 1° Rid.", "Ore": 50.0},
        {"Ordine": 31, "Canale": "Ossola 2° Rid.", "Ore": 40.0},
        {"Ordine": 32, "Canale": "Agraria Rid.", "Ore": 60.0},
        {"Ordine": 33, "Canale": "Manzoglio Rid.", "Ore": 80.0},
        {"Ordine": 34, "Canale": "Fiascale Rid.", "Ore": 120.0},
        {"Ordine": 35, "Canale": "Tessagli Rid.", "Ore": 90.0},
        {"Ordine": 36, "Canale": "Roncole Rid.", "Ore": 110.0},
        {"Ordine": 37, "Canale": "Vaja Rid.", "Ore": 80.0},
        {"Ordine": 38, "Canale": "Riglio Rid.", "Ore": 140.0},
        {"Ordine": 39, "Canale": "Breda 3°", "Ore": 37.0},
        {"Ordine": 40, "Canale": "Breda 4°", "Ore": 19.0},
        {"Ordine": 41, "Canale": "Delmoncello 1° ridotta", "Ore": 70.0},
        {"Ordine": 42, "Canale": "Delmoncello 2°", "Ore": 10.0},
        {"Ordine": 43, "Canale": "Casalmerlino ridotta", "Ore": 20.0},
        {"Ordine": 44, "Canale": "Bocchette Secondario Casalmerlino", "Ore": 14.0},
        {"Ordine": 45, "Canale": "Bocchette Secondario Casalmerlino rid", "Ore": 30.0},
        {"Ordine": 46, "Canale": "Bonfanti", "Ore": 300.0},
        {"Ordine": 47, "Canale": "Levata", "Ore": 300.0},
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
with st.expander("📝 Modifica Sequenza e Durate", expanded=False):
    edited_df = st.data_editor(
        st.session_state.df_canali,
        num_rows="dynamic", use_container_width=True, hide_index=True,
        column_config={
            "Ordine": st.column_config.NumberColumn("Ordine", help="Sequenza di partenza", required=True),
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
    df_valid = df_canali.dropna(subset=['Ordine', 'Ore', 'Canale']).copy()
    # Converte le colonne in numerico, gestendo eventuali errori
    df_valid['Ordine'] = pd.to_numeric(df_valid['Ordine'], errors='coerce')
    df_valid['Ore'] = pd.to_numeric(df_valid['Ore'], errors='coerce')
    df_valid = df_valid.dropna(subset=['Ordine', 'Ore'])
    df_valid = df_valid.sort_values(by="Ordine")

    if df_valid.empty or df_valid['Ore'].sum() <= 0:
        return pd.DataFrame()

    # Calcola la durata totale di UN ciclo completo
    durata_totale_ciclo_ore = df_valid['Ore'].sum()
    if durata_totale_ciclo_ore == 0: return pd.DataFrame()
    durata_ciclo_timedelta = timedelta(hours=durata_totale_ciclo_ore)
    
    tempo_corrente = start_dt
    while tempo_corrente < end_dt:
        for _, row in df_valid.iterrows():
            durata = float(row['Ore'])
            if durata <= 0: continue
            
            fine_turno = tempo_corrente + timedelta(hours=durata)
            if tempo_corrente < end_dt:
                turni.append({
                    "Canale": row['Canale'], "Inizio": tempo_corrente, "Fine": min(fine_turno, end_dt)
                })
            tempo_corrente = fine_turno
            if tempo_corrente >= end_dt: break
    
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
        for _, turno in turni_del_giorno.iterrows():
            ora_in = turno['Inizio'].strftime('%d/%m ore %H:%M')
            ora_fi = turno['Fine'].strftime('%d/%m ore %H:%M')
            
            st.markdown(f"""
            <div style="border-left: 8px solid #1f77b4; background-color: #f0f2f6; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #111;">{turno['Canale']}</h3>
                <p style="font-size: 1.1em; margin:0;">🟢 <b>Apertura:</b> {ora_in}</p>
                <p style="font-size: 1.1em; margin:5px 0;">🔴 <b>Chiusura:</b> {ora_fi}</p>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("Dettaglio Completo Stagione (CSV)"):
        st.dataframe(df_risultato.style.format({"Inizio": "{:%d/%m/%Y %H:%M}", "Fine": "{:%d/%m/%Y %H:%M}"}), hide_index=True)
        csv = df_risultato.to_csv(index=False, date_format='%d/%m/%Y %H:%M').encode('utf-8')
        st.download_button("📥 Scarica Intera Stagione", data=csv, file_name="orari_stagione.csv", mime="text/csv")
else:
    st.warning("Nessun dato da calcolare. Controlla le impostazioni.")
