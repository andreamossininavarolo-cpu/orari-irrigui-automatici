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

# 2. Inizializzazione dei dati con GRUPPI e un elenco completo
if 'df_canali' not in st.session_state:
    # Aggiunto un campo 'Gruppo' per gestire canali paralleli.
    # Canali nello stesso gruppo vengono eseguiti in sequenza.
    # Canali in gruppi diversi possono essere eseguiti in parallelo.
    st.session_state.df_canali = pd.DataFrame([
        {"Gruppo": 1, "Utenza": "Corte Emilia", "Durata_Ore": 24.0},
        {"Gruppo": 1, "Utenza": "Pirolo", "Durata_Ore": 18.0},
        {"Gruppo": 1, "Utenza": "BONFANTE", "Durata_Ore": 10.0},
        {"Gruppo": 1, "Utenza": "TESSAGLI RID", "Durata_Ore": 14.0},
        {"Gruppo": 1, "Utenza": "RONCOLE RID", "Durata_Ore": 16.0},

        {"Gruppo": 2, "Utenza": "Cividale Nord A", "Durata_Ore": 48.0},
        {"Gruppo": 2, "Utenza": "Cividale Nord Vecchia", "Durata_Ore": 12.0},
        {"Gruppo": 2, "Utenza": "Gruppo Bocchette", "Durata_Ore": 20.0},
        
        {"Gruppo": 3, "Utenza": "Belvedere Nord", "Durata_Ore": 12.0},
        {"Gruppo": 3, "Utenza": "Spineca", "Durata_Ore": 10.0},
        {"Gruppo": 3, "Utenza": "Madonna Lame", "Durata_Ore": 15.0},

        {"Gruppo": 4, "Utenza": "OSSOLA 2 RID", "Durata_Ore": 12.0},
        {"Gruppo": 4, "Utenza": "AGRARIA RID", "Durata_Ore": 8.0},
        {"Gruppo": 4, "Utenza": "MANZOGLIO RID", "Durata_Ore": 36.0},
        
        {"Gruppo": 5, "Utenza": "BREDA 3", "Durata_Ore": 12.0},
        {"Gruppo": 5, "Utenza": "BREDA 4", "Durata_Ore": 12.0},
        {"Gruppo": 5, "Utenza": "DELMONCELLO", "Durata_Ore": 16.0},
    ])

# 3. Tabella modificabile
st.subheader("📝 Tabellone Canali, Durate e Gruppi")
st.info("Modifica i dati, specialmente il 'Gruppo' e la 'Durata_Ore', per cambiare la sequenza e la sovrapposizione.")

df_modificato = st.data_editor(
    st.session_state.df_canali,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Gruppo": st.column_config.NumberColumn("Gruppo (1, 2, ...)", min_value=1, step=1),
        "Utenza": st.column_config.TextColumn("Nome Canale / Utenza", required=True),
        "Durata_Ore": st.column_config.NumberColumn("Durata Turno (Ore)", min_value=0.5, step=0.5, format="%.1f h"),
    }
)
st.session_state.df_canali = df_modificato

# 4. Funzione di calcolo con CICLI e GRUPPI
def calcola_turnazione_gruppi(df, start_stagione, end_stagione):
    turni_totali = []
    
    # Dizionario per tenere traccia del tempo di fine per ogni gruppo
    fine_per_gruppo = {gruppo: start_stagione for gruppo in df['Gruppo'].unique()}

    # Continua a generare turni finché non superiamo la fine della stagione
    while min(fine_per_gruppo.values()) < end_stagione:
        for gruppo_id in sorted(df['Gruppo'].unique()):
            df_gruppo = df[df['Gruppo'] == gruppo_id]
            
            # Il tempo di inizio per questo ciclo del gruppo è la fine del ciclo precedente dello stesso gruppo
            tempo_corrente = fine_per_gruppo[gruppo_id]
            
            for idx, row in df_gruppo.iterrows():
                if tempo_corrente >= end_stagione: break

                fine_turno = tempo_corrente + timedelta(hours=float(row['Durata_Ore']))
                turni_totali.append({
                    "Utenza": row['Utenza'],
                    "Inizio": tempo_corrente,
                    "Fine": fine_turno,
                    "Gruppo": f"Gruppo {gruppo_id}"
                })
                tempo_corrente = fine_turno
            
            # Aggiorna il tempo di fine per il prossimo ciclo di questo gruppo
            fine_per_gruppo[gruppo_id] = tempo_corrente
        
    return pd.DataFrame(turni_totali)


# Calcoliamo il nuovo cronoprogramma
df_cronoprogramma = pd.DataFrame()
if not df_modificato.empty and df_modificato['Durata_Ore'].sum() > 0:
    df_cronoprogramma = calcola_turnazione_gruppi(df_modificato, data_ora_start, datetime.combine(data_fine_stagione, datetime.min.time()))

st.markdown("---")

# 5. Grafico di Gantt Interattivo
st.subheader("📊 Grafico Temporale Interattivo (Gantt)")

if not df_cronoprogramma.empty:
    fig = px.timeline(
        df_cronoprogramma, x_start="Inizio", x_end="Fine", y="Utenza", color="Gruppo",
        labels={"Utenza": "Canale", "Gruppo": "Gruppo di Turnazione"},
        title="Programmazione Ciclica Canali per Gruppo"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=max(400, len(df_modificato["Utenza"].unique()) * 35),
        xaxis=dict(title="Calendario Turnazione", tickformat="%d %b")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aggiungi almeno un'utenza con durata > 0 per visualizzare il grafico.")

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
