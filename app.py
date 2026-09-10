import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Configurazione della pagina ottimizzata per PC e Mobile
st.set_page_config(
    page_title="Gestione Canalette - Consorzio Navarolo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titolo principale dell'applicazione
st.title("🌊 Consorzio Navarolo: Gestione Orari Irrigazione")
st.write("Modifica le durate o i nomi nella tabella sotto: l'intero programma a cascata si ricalcolerà all'istante!")

st.markdown("---")

# 1. Impostazione dei parametri di partenza nella barra laterale
st.sidebar.header("📅 Parametri di Partenza")
data_inizio = st.sidebar.date_input("Data inizio turno:", datetime(2026, 4, 1).date())
ora_inizio = st.sidebar.time_input("Ora inizio turno:", datetime(2026, 4, 1, 8, 0).time())

# Uniamo data e ora in un unico oggetto datetime
data_ora_start = datetime.combine(data_inizio, ora_inizio)

# 2. Inizializzazione dello Stato dei Dati (Database simulato in memoria)
if 'df_canali' not in st.session_state:
    # Carichiamo i canali principali del Camparo Matteo Storti presi dal PDF
    st.session_state.df_canali = pd.DataFrame([
        {"Utenza": "Corte Emilia", "Durata_Ore": 24.0, "Portata_ls": 120},
        {"Utenza": "Cividale Nord A", "Durata_Ore": 48.0, "Portata_ls": 100},
        {"Utenza": "OSSOLA 2 RID", "Durata_Ore": 12.0, "Portata_ls": 80},
        {"Utenza": "MANZOGLIO RID", "Durata_Ore": 36.0, "Portata_ls": 150},
        {"Utenza": "BREDA 3 / BREDA 4", "Durata_Ore": 24.0, "Portata_ls": 90},
    ])

# 3. Tabella modificabile (Data Editor)
st.subheader("📝 Tabellone di Inserimento Dati")
st.info("💡 Fai doppio clic su qualsiasi cella della tabella per modificare il nome o la durata in ore. Puoi anche aggiungere nuove utenze in fondo.")

# Editor interattivo di Streamlit
df_modificato = st.data_editor(
    st.session_state.df_canali,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Utenza": st.column_config.TextColumn("Nome Canale / Utenza", required=True),
        "Durata_Ore": st.column_config.NumberColumn("Durata Turno (Ore)", min_value=1.0, max_value=240.0, step=0.5, format="%.1f h"),
        "Portata_ls": st.column_config.NumberColumn("Portata (l/s)", min_value=0, step=10)
    }
)

# Salviamo lo stato aggiornato
st.session_state.df_canali = df_modificato

# 4. Funzione di ricalcolo a cascata automatico
def calcola_calendario_cascata(df, start_time):
    risultati = []
    tempo_corrente = start_time
    
    for idx, row in df.iterrows():
        # Calcoliamo la fine sommando la durata inserita dall'utente
        fine_turno = tempo_corrente + timedelta(hours=float(row['Durata_Ore']))
        risultati.append({
            "Utenza": row['Utenza'],
            "Inizio": tempo_corrente,
            "Fine": fine_turno,
            "Durata (Ore)": row['Durata_Ore'],
            "Portata (l/s)": row['Portata_ls']
        })
        # Il turno successivo riparte esattamente al termine di questo
        tempo_corrente = fine_turno
        
    return pd.DataFrame(risultati)

# Calcoliamo le date aggiornate
df_cronoprogramma = calcola_calendario_cascata(df_modificato, data_ora_start)

st.markdown("---")

# 5. Grafico di Gantt Interattivo (Plotly)
st.subheader("📊 Grafico Temporale Interattivo (Gantt)")

if not df_cronoprogramma.empty:
    fig = px.timeline(
        df_cronoprogramma,
        x_start="Inizio",
        x_end="Fine",
        y="Utenza",
        color="Utenza",
        labels={"Utenza": "Canale"},
        title="Progressione Temporale Erogazione"
    )
    
    # Ottimizzazioni per renderlo chiaro e invertire l'asse Y per avere il primo canale in alto
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            title="Calendario Turnazione",
            tickformat="%d %b %H:%M" # Formato data/ora leggibile (es: 01 Apr 08:00)
        )
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nessuna utenza inserita. Aggiungi righe nella tabella sopra.")

st.markdown("---")

# 6. Tabellone Finale Formattato e Pulsante di Esportazione
st.subheader("📅 Calendario Turni Calcolato")

if not df_cronoprogramma.empty:
    # Formattiamo le date per la lettura umana nella tabella finale
    df_visualizzabile = df_cronoprogramma.copy()
    df_visualizzabile["Inizio"] = df_visualizzabile["Inizio"].dt.strftime('%d/%m/%Y %H:%M')
    df_visualizzabile["Fine"] = df_visualizzabile["Fine"].dt.strftime('%d/%m/%Y %H:%M')
    
    st.dataframe(df_visualizzabile, use_container_width=True)
    
    # Esportazione rapida in formato CSV compatibile al 100% con Excel
    csv_data = df_cronoprogramma.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica Orari Aggiornati (Excel / CSV)",
        data=csv_data,
        file_name=f"orario_irrigazione_navarolo_{data_inizio}.csv",
        mime="text/csv"
    )
