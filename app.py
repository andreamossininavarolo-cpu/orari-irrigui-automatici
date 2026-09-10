import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Configurazione della pagina
st.set_page_config(
    page_title="Gestione Turni Irrigui - Navarolo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titolo principale
st.title("🌊 Consorzio Navarolo: Gestione Turni Irrigui")
st.write("Modifica i dati nella tabella: il programma si ricalcolerà per l'intera stagione.")
st.markdown("---")

# 1. Parametri di Partenza nella barra laterale
st.sidebar.header("⚙️ Parametri di Configurazione")
data_inizio_stagione = st.sidebar.date_input("Data inizio stagione:", datetime(2026, 4, 1).date())
ora_inizio_stagione = st.sidebar.time_input("Ora inizio stagione:", datetime(2026, 4, 1, 8, 0).time())
data_fine_stagione = st.sidebar.date_input("Data fine stagione:", datetime(2026, 9, 22).date())
data_ora_start = datetime.combine(data_inizio_stagione, ora_inizio_stagione)

# 2. Inizializzazione dei dati con GRUPPI
if 'df_canali' not in st.session_state:
    st.session_state.df_canali = pd.DataFrame([
        {"Gruppo": 1, "Utenza": "Corte Emilia", "Durata_Ore": 24.0, "Portata_ls": 120},
        {"Gruppo": 1, "Utenza": "Pirolo", "Durata_Ore": 18.0, "Portata_ls": 90},
        {"Gruppo": 2, "Utenza": "Cividale Nord A", "Durata_Ore": 48.0, "Portata_ls": 100},
        {"Gruppo": 2, "Utenza": "Cividale Nord Vecchia", "Durata_Ore": 12.0, "Portata_ls": 70},
        {"Gruppo": 3, "Utenza": "OSSOLA 2 RID", "Durata_Ore": 12.0, "Portata_ls": 80},
        {"Gruppo": 3, "Utenza": "MANZOGLIO RID", "Durata_Ore": 36.0, "Portata_ls": 150},
        {"Gruppo": 4, "Utenza": "BREDA 3", "Durata_Ore": 12.0, "Portata_ls": 50},
        {"Gruppo": 4, "Utenza": "BREDA 4", "Durata_Ore": 12.0, "Portata_ls": 40},
    ])

# 3. Tabella modificabile
st.subheader("📝 Tabellone Canali, Durate e Gruppi")
st.info("Modifica i dati, specialmente il 'Gruppo' e la 'Durata_Ore', per cambiare la sequenza.")

# CORREZIONE: Ho reso esplicito l'ordine delle colonne per evitare che "Gruppo" scompaia
edited_df = st.data_editor(
    st.session_state.df_canali,
    column_order=("Gruppo", "Utenza", "Durata_Ore", "Portata_ls"), # Forza l'ordine
    column_config={
        "Gruppo": st.column_config.NumberColumn("Gruppo", help="Canali con lo stesso Gruppo partono insieme in parallelo ad altri gruppi", min_value=1, step=1, required=True),
        "Utenza": st.column_config.TextColumn("Nome Canale / Utenza", required=True),
        "Durata_Ore": st.column_config.NumberColumn("Durata Turno (Ore)", min_value=0.5, step=0.5, format="%.1f h", required=True),
        "Portata_ls": st.column_config.NumberColumn("Portata (l/s)"),
    },
    num_rows="dynamic",
    use_container_width=True,
)

# 4. Funzione di calcolo con CICLI e GRUPPI
def calcola_turnazione_gruppi(df, start_stagione, end_stagione):
    turni_totali = []
    
    # Dizionario per tenere traccia del tempo di fine per ogni gruppo
    fine_per_gruppo = {gruppo: start_stagione for gruppo in df['Gruppo'].unique()}

    active = True
    while active:
        active = False
        for gruppo_id in sorted(df['Gruppo'].unique()):
            df_gruppo = df[df['Gruppo'] == gruppo_id]
            
            tempo_corrente = fine_per_gruppo[gruppo_id]
            
            if tempo_corrente >= end_stagione:
                continue
            
            active = True
            
            for idx, row in df_gruppo.iterrows():
                fine_turno = tempo_corrente + timedelta(hours=float(row['Durata_Ore']))
                turni_totali.append({
                    "Utenza": row['Utenza'],
                    "Inizio": tempo_corrente,
                    "Fine": fine_turno,
                    "Gruppo": f"Gruppo {gruppo_id}"
                })
                tempo_corrente = fine_turno
            
            fine_per_gruppo[gruppo_id] = tempo_corrente
        
    return pd.DataFrame(turni_totali)

# Calcoliamo il nuovo cronoprogramma
df_cronoprogramma = pd.DataFrame()
if not edited_df.empty and 'Gruppo' in edited_df.columns and pd.to_numeric(edited_df['Durata_Ore'], errors='coerce').sum() > 0:
    st.session_state.df_canali = edited_df
    df_cronoprogramma = calcola_turnazione_gruppi(st.session_state.df_canali, data_ora_start, datetime.combine(data_fine_stagione, datetime.min.time()))

st.markdown("---")

# 5. Grafico di Gantt Interattivo
st.subheader("📊 Grafico Temporale Interattivo (Gantt)")

if not df_cronoprogramma.empty:
    fig = px.timeline(
        df_cronoprogramma, x_start="Inizio", x_end="Fine", y="Utenza", color="Gruppo",
        labels={"Utenza": "Canale", "Gruppo": "Gruppo di Turnazione"},
        title="Programmazione Ciclica Canali per Gruppo"
    )
    fig.update_yaxes(autorange="reversed", title_text="")
    fig.update_layout(
        height=max(500, len(edited_df["Utenza"].unique()) * 35),
        xaxis=dict(title="Calendario Turnazione", tickformat="%d %b")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nessun dato da visualizzare. Controlla che ci siano canali nella tabella con una durata maggiore di zero.")

st.markdown("---")

# 6. Tabellone Finale e Download
st.subheader("📅 Calendario Turni Calcolato (Completo)")
if not df_cronoprogramma.empty:
    df_visualizzabile = df_cronoprogramma.copy()
    df_visualizzabile["Inizio"] = df_visualizzabile["Inizio"].dt.strftime('%d/%m/%Y %H:%M')
    df_visualizzabile["Fine"] = df_visualizzabile["Fine"].dt.strftime('%d/%m/%Y %H:%M')
    
    st.dataframe(df_visualizzabile, use_container_width=True, height=400)
    
    csv_data = df_cronoprogramma.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica Orari (CSV per Excel)",
        data=csv_data,
        file_name=f"orario_irrigazione_gruppi_{data_inizio_stagione}.csv",
        mime="text/csv"
    )
