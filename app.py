import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# --- Configurazione Pagina ---
st.set_page_config(page_title="Gestione Turni Irrigui - Navarolo", layout="wide")

# --- Dati Iniziali ---
def get_initial_data():
    """Restituisce il DataFrame iniziale con l'elenco dei canali."""
    return pd.DataFrame([
        {"Gruppo": 1, "Utenza": "Corte Emilia", "Durata_Ore": 24.0, "Portata_ls": 120},
        {"Gruppo": 1, "Utenza": "Pirolo", "Durata_Ore": 18.0, "Portata_ls": 90},
        {"Gruppo": 1, "Utenza": "BONFANTE", "Durata_Ore": 10.0, "Portata_ls": 85},
        {"Gruppo": 2, "Utenza": "Cividale Nord A", "Durata_Ore": 48.0, "Portata_ls": 100},
        {"Gruppo": 2, "Utenza": "Cividale Nord Vecchia", "Durata_Ore": 12.0, "Portata_ls": 70},
        {"Gruppo": 2, "Utenza": "Gruppo Bocchette", "Durata_Ore": 20.0, "Portata_ls": 110},
        {"Gruppo": 3, "Utenza": "Belvedere Nord", "Durata_Ore": 12.0, "Portata_ls": 65},
        {"Gruppo": 3, "Utenza": "Spineca", "Durata_Ore": 10.0, "Portata_ls": 60},
        {"Gruppo": 4, "Utenza": "OSSOLA 2 RID", "Durata_Ore": 12.0, "Portata_ls": 80},
        {"Gruppo": 4, "Utenza": "MANZOGLIO RID", "Durata_Ore": 36.0, "Portata_ls": 150},
        {"Gruppo": 5, "Utenza": "BREDA 3", "Durata_Ore": 12.0, "Portata_ls": 50},
        {"Gruppo": 5, "Utenza": "BREDA 4", "Durata_Ore": 12.0, "Portata_ls": 40},
    ])

# --- Inizializzazione Stato ---
if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()

# --- Interfaccia Utente ---
st.title("🌊 Consorzio Navarolo: Gestione Turni Irrigui")
st.write("Modifica i dati nella tabella: il programma ricalcolerà i turni per l'intera stagione.")
st.markdown("---")

# 1. Parametri di Partenza
st.sidebar.header("⚙️ Parametri Stagione")
data_inizio = st.sidebar.date_input("Data inizio:", datetime(2026, 4, 1).date())
ora_inizio = st.sidebar.time_input("Ora inizio:", datetime(2026, 4, 1, 8, 0).time())
data_fine = st.sidebar.date_input("Data fine:", datetime(2026, 9, 22).date())
data_ora_start = datetime.combine(data_inizio, ora_inizio)
data_ora_end = datetime.combine(data_fine, datetime.min.time())

# Pulsante di Reset
if st.sidebar.button("♻️ Ripristina dati originali"):
    st.session_state.df_canali = get_initial_data()
    st.rerun()

# 2. Tabella Interattiva
st.subheader("📝 Tabellone Canali, Durate e Gruppi (Modificabile)")
st.info("I canali con lo stesso 'Gruppo' andranno in sequenza. Gruppi diversi irrigheranno in contemporanea.")

edited_df = st.data_editor(
    st.session_state.df_canali,
    num_rows="dynamic",
    use_container_width=True,
    column_order=["Gruppo", "Utenza", "Durata_Ore", "Portata_ls"],
    column_config={
        "Gruppo": st.column_config.NumberColumn("Gruppo", min_value=1, step=1, required=True),
        "Utenza": st.column_config.TextColumn("Utenza", required=True),
        "Durata_Ore": st.column_config.NumberColumn("Durata (Ore)", min_value=0.1, step=0.5, format="%.1f h", required=True),
        "Portata_ls": st.column_config.NumberColumn("Portata (l/s)"),
    },
    key="editor_principale"
)

# 3. Logica di Calcolo
turni = []
if not edited_df.empty:
    df_valid = edited_df.dropna(subset=['Gruppo', 'Durata_Ore']).copy()
    df_valid['Gruppo'] = pd.to_numeric(df_valid['Gruppo'], errors='coerce').astype('Int64')
    df_valid['Durata_Ore'] = pd.to_numeric(df_valid['Durata_Ore'], errors='coerce')
    df_valid = df_valid.dropna(subset=['Gruppo', 'Durata_Ore'])

    if not df_valid.empty and df_valid['Durata_Ore'].sum() > 0:
        gruppi_unici = sorted(df_valid['Gruppo'].unique())
        fine_per_gruppo = {g: data_ora_start for g in gruppi_unici}
        
        attivo = True
        while attivo:
            attivo = False
            for g in gruppi_unici:
                df_gruppo = df_valid[df_valid['Gruppo'] == g]
                corrente = fine_per_gruppo[g]
                
                if corrente < data_ora_end:
                    attivo = True
                    for _, row in df_gruppo.iterrows():
                        durata = float(row['Durata_Ore'])
                        if durata <= 0 or corrente >= data_ora_end: continue
                        
                        fine_turno = corrente + timedelta(hours=durata)
                        turni.append({
                            "Gruppo": f"Gruppo {g}",
                            "Utenza": row['Utenza'],
                            "Inizio": corrente,
                            "Fine": min(fine_turno, data_ora_end),
                        })
                        corrente = fine_turno
                    fine_per_gruppo[g] = corrente

df_risultato = pd.DataFrame(turni)

# 4. Visualizzazione Grafico
st.markdown("---")
st.subheader("📊 Grafico Temporale Interattivo (Gantt)")
if not df_risultato.empty:
    fig = px.timeline(
        df_risultato, x_start="Inizio", x_end="Fine", y="Utenza", color="Gruppo",
        title="Programmazione Ciclica Fino a Fine Stagione"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=max(450, len(edited_df["Utenza"].unique()) * 30), xaxis_title="Calendario della Stagione")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nessun dato valido da visualizzare. Assicurati di aver inserito almeno un 'Gruppo' e una 'Durata (Ore)' nella tabella.")

# 5. Tabella Finale e Download
if not df_risultato.empty:
    st.markdown("---")
    st.subheader("📅 Dettaglio Orari Calcolati")
    df_show = df_risultato.copy()
    df_show["Inizio"] = df_show["Inizio"].dt.strftime('%d/%m/%Y %H:%M')
    df_show["Fine"] = df_show["Fine"].dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(df_show, use_container_width=True, height=350)

    csv = df_risultato.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica Orari Completi (Excel / CSV)",
        data=csv,
        file_name="orari_irrigazione_completi.csv",
        mime="text/csv"
    )

