import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Turni Navarolo", layout="centered")
st.title("🌊 Turni Irrigui a Cascata")

# --- Dati Iniziali Estratti dal Nuovo PDF ---
def get_initial_data():
    return pd.DataFrame([
        {"Ordine": 1, "Canale": "Corte Emilia", "Ore": 24.0, "l/s": 120},
        {"Ordine": 2, "Canale": "Pirolo", "Ore": 18.0, "l/s": 90},
        {"Ordine": 3, "Canale": "Cividale Nord A", "Ore": 48.0, "l/s": 100},
        {"Ordine": 4, "Canale": "Nord Vecchia", "Ore": 12.0, "l/s": 70},
        {"Ordine": 5, "Canale": "Belvedere Nord", "Ore": 12.0, "l/s": 65},
        {"Ordine": 6, "Canale": "OSSOLA 2 RID", "Ore": 12.0, "l/s": 80},
        {"Ordine": 7, "Canale": "AGRARIA RID", "Ore": 8.0, "l/s": 50},
        {"Ordine": 8, "Canale": "MANZOGLIO RID", "Ore": 36.0, "l/s": 150},
        {"Ordine": 9, "Canale": "TESSAGLI RID", "Ore": 14.0, "l/s": 70},
        {"Ordine": 10, "Canale": "BONFANTE", "Ore": 10.0, "l/s": 85},
        {"Ordine": 11, "Canale": "Bocchette", "Ore": 20.0, "l/s": 110},
        {"Ordine": 12, "Canale": "BREDA 3", "Ore": 12.0, "l/s": 50},
        {"Ordine": 13, "Canale": "BREDA 4", "Ore": 12.0, "l/s": 40},
    ])

if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()

# --- Menu Impostazioni ---
with st.expander("⚙️ Impostazioni Stagione", expanded=False):
    d_inizio = st.date_input("Inizio Stagione:", datetime(2026, 4, 1).date(), format="DD/MM/YYYY")
    t_inizio = st.time_input("Ora Inizio:", datetime(2026, 4, 1, 8, 0).time())
    d_fine = st.date_input("Fine Stagione:", datetime(2026, 9, 22).date(), format="DD/MM/YYYY")
    ciclo_giorni = st.number_input("Ogni quanti giorni riparte il ciclo?", min_value=1, value=14)
    
    if st.button("♻️ Reset Dati Originali"):
        st.session_state.df_canali = get_initial_data()
        st.rerun()

start_stagione = datetime.combine(d_inizio, t_inizio)
end_stagione = datetime.combine(d_fine, datetime.min.time())

# --- Tabella Interattiva ---
with st.expander("📝 Modifica Sequenza e Durate", expanded=False):
    st.info("I canali partiranno in sequenza dall'alto verso il basso.")
    edited_df = st.data_editor(
        st.session_state.df_canali,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ordine": st.column_config.NumberColumn("Ord.", min_value=1, step=1, required=True),
            "Canale": st.column_config.TextColumn("Canale", required=True),
            "Ore": st.column_config.NumberColumn("Ore", min_value=0.1, step=0.5, format="%.1f", required=True),
            "l/s": st.column_config.NumberColumn("l/s"),
        }
    )
    st.session_state.df_canali = edited_df

# --- Calcolo a Cascata Unica ---
turni = []
if not edited_df.empty and 'Ordine' in edited_df.columns:
    df_valid = edited_df.dropna(subset=['Ordine', 'Ore']).copy()
    df_valid['Ordine'] = pd.to_numeric(df_valid['Ordine'], errors='coerce')
    df_valid['Ore'] = pd.to_numeric(df_valid['Ore'], errors='coerce')
    df_valid = df_valid.dropna()
    df_valid = df_valid.sort_values(by="Ordine")

    if not df_valid.empty and df_valid['Ore'].sum() > 0:
        inizio_ciclo = start_stagione
        
        while inizio_ciclo < end_stagione:
            corrente = inizio_ciclo
            for _, row in df_valid.iterrows():
                durata = float(row['Ore'])
                if durata <= 0: continue
                
                fine_turno = corrente + timedelta(hours=durata)
                
                if corrente < end_stagione:
                    turni.append({
                        "Sequenza": int(row['Ordine']),
                        "Canale": row['Canale'],
                        "Inizio": corrente,
                        "Fine": min(fine_turno, end_stagione),
                        "l/s": row.get('l/s', 0)
                    })
                corrente = fine_turno
                
            # Il ciclo riparte dopo X giorni dall'inizio del ciclo precedente
            inizio_ciclo += timedelta(days=ciclo_giorni)

df_risultato = pd.DataFrame(turni)

# --- Visualizzazione Schede Giornaliere ---
st.markdown("---")
if not df_risultato.empty:
    st.subheader("📅 Cosa devo aprire oggi?")
    giorno_selezionato = st.date_input("Mostra turni per il giorno:", datetime(2026, 4, 1).date(), format="DD/MM/YYYY")
    
    inizio_giorno = datetime.combine(giorno_selezionato, datetime.min.time())
    fine_giorno = inizio_giorno + timedelta(days=1)
    
    # Prendi i turni in corso nel giorno selezionato
    turni_del_giorno = df_risultato[
        (df_risultato['Inizio'] < fine_giorno) & (df_risultato['Fine'] > inizio_giorno)
    ].sort_values(by='Inizio')
    
    if turni_del_giorno.empty:
        st.success("🎉 Nessun canale aperto in questa data!")
    else:
        for _, turno in turni_del_giorno.iterrows():
            ora_in = turno['Inizio'].strftime('%d/%m/%y ore %H:%M')
            ora_fi = turno['Fine'].strftime('%d/%m/%y ore %H:%M')
            
            st.markdown(f"""
            <div style="border-left: 8px solid #1f77b4; background-color: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #333;">{turno['Canale']}</h3>
                <p style="margin: 5px 0; font-size: 16px;">🟢 <b>Apertura:</b> {ora_in}</p>
                <p style="margin: 5px 0; font-size: 16px;">🔴 <b>Chiusura:</b> {ora_fi}</p>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">Portata stimata: {turno['l/s']} l/s</p>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📥 Scarica Excel Intera Stagione"):
        st.dataframe(df_risultato, hide_index=True)
        csv = df_risultato.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica CSV", data=csv, file_name="orari_stagione_navarolo.csv", mime="text/csv")
else:
    st.warning("Assicurati di aver inserito durate valide nella tabella.")
