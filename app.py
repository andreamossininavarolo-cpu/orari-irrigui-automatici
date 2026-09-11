import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Turni Navarolo", layout="centered")
st.title("🌊 Turni Irrigui")

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

with st.expander("⚙️ Impostazioni Stagione", expanded=False):
    # Formato europeo GG/MM/AAAA per i calendari
    d_inizio = st.date_input("Inizio Stagione:", datetime(2026, 4, 1).date(), format="DD/MM/YYYY")
    t_inizio = st.time_input("Ora Inizio:", datetime(2026, 4, 1, 8, 0).time())
    d_fine = st.date_input("Fine Stagione:", datetime(2026, 9, 22).date(), format="DD/MM/YYYY")
    ciclo_giorni = st.number_input("Ciclo (Giorni):", min_value=1, value=14)
    
    if st.button("♻️ Reset Dati Tabella"):
        st.session_state.df_canali = get_initial_data()
        st.rerun()

start_stagione = datetime.combine(d_inizio, t_inizio)
end_stagione = datetime.combine(d_fine, datetime.min.time())

with st.expander("📝 Modifica Canali e Durate", expanded=False):
    edited_df = st.data_editor(
        st.session_state.df_canali,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Gr.": st.column_config.NumberColumn("Gr.", min_value=1, step=1, required=True),
            "Canale": st.column_config.TextColumn("Canale", required=True),
            "Ore": st.column_config.NumberColumn("Ore", min_value=0.1, step=0.5, format="%.1f", required=True),
            "l/s": st.column_config.NumberColumn("l/s"),
        }
    )
    st.session_state.df_canali = edited_df

# Calcolo turni
turni = []
if not edited_df.empty and 'Gr.' in edited_df.columns:
    df_valid = edited_df.dropna(subset=['Gr.', 'Ore']).copy()
    df_valid['Gr.'] = pd.to_numeric(df_valid['Gr.'], errors='coerce')
    df_valid['Ore'] = pd.to_numeric(df_valid['Ore'], errors='coerce')
    df_valid = df_valid.dropna()

    if not df_valid.empty and df_valid['Ore'].sum() > 0:
        for g in sorted(df_valid['Gr.'].unique()):
            df_g = df_valid[df_valid['Gr.'] == g]
            inizio_ciclo = start_stagione
            
            while inizio_ciclo < end_stagione:
                corrente = inizio_ciclo
                for _, row in df_g.iterrows():
                    durata = float(row['Ore'])
                    if durata <= 0: continue
                    fine_turno = corrente + timedelta(hours=durata)
                    
                    if corrente < end_stagione:
                        turni.append({
                            "Gruppo": int(g),
                            "Canale": row['Canale'],
                            "Inizio": corrente,
                            "Fine": min(fine_turno, end_stagione),
                            "l/s": row.get('l/s', 0)
                        })
                    corrente = fine_turno
                inizio_ciclo += timedelta(days=ciclo_giorni)

df_risultato = pd.DataFrame(turni)

st.markdown("---")
if not df_risultato.empty:
    st.subheader("📅 Cosa c'è da fare?")
    # Calendario per la ricerca con formato europeo
    giorno_selezionato = st.date_input("Mostra turni per il giorno:", datetime(2026, 4, 1).date(), format="DD/MM/YYYY")
    
    inizio_giorno = datetime.combine(giorno_selezionato, datetime.min.time())
    fine_giorno = inizio_giorno + timedelta(days=1)
    
    # Prendi solo i turni che si accavallano con la data scelta
    turni_del_giorno = df_risultato[
        (df_risultato['Inizio'] < fine_giorno) & (df_risultato['Fine'] > inizio_giorno)
    ].sort_values(by=['Gruppo', 'Inizio'])
    
    if turni_del_giorno.empty:
        st.success("🎉 Nessun canale aperto in questa data!")
    else:
        colori = {1: "#1f77b4", 2: "#ff7f0e", 3: "#2ca02c", 4: "#d62728", 5: "#9467bd"}
        for _, turno in turni_del_giorno.iterrows():
            colore_gruppo = colori.get(turno['Gruppo'] % 5 + 1, "#333")
            
            # Formattazione data in GG/MM/AA
            ora_in = turno['Inizio'].strftime('%d/%m/%y ore %H:%M')
            ora_fi = turno['Fine'].strftime('%d/%m/%y ore %H:%M')
            
            st.markdown(f"""
            <div style="border-left: 8px solid {colore_gruppo}; background-color: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 5px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #333;">{turno['Canale']}</h3>
                <p style="margin: 5px 0; font-size: 16px;">🟢 <b>Apertura:</b> {ora_in}</p>
                <p style="margin: 5px 0; font-size: 16px;">🔴 <b>Chiusura:</b> {ora_fi}</p>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">Gruppo: {turno['Gruppo']} | Portata: {turno['l/s']} l/s</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    csv = df_risultato.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica Intera Stagione (CSV)", data=csv, file_name="orari_stagione.csv", mime="text/csv")
else:
    st.warning("Inserisci i dati nei menu in alto.")
