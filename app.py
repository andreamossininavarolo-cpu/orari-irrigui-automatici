import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Configurazione della pagina
st.set_page_config(page_title="Gestione Turni Irrigui - Navarolo", layout="wide")

st.title("🌊 Consorzio Navarolo: Gestione Turni Irrigui Automatici")
st.write("Modifica i dati nella tabella: il programma ricalcolerà i turni a cascata per l'intera stagione.")
st.markdown("---")

# --- Parametri di Partenza ---
st.sidebar.header("⚙️ Parametri Stagione")
data_inizio = st.sidebar.date_input("Data inizio:", datetime(2026, 4, 1).date())
ora_inizio = st.sidebar.time_input("Ora inizio:", datetime(2026, 4, 1, 8, 0).time())
data_fine = st.sidebar.date_input("Data fine:", datetime(2026, 9, 22).date())

data_ora_start = datetime.combine(data_inizio, ora_inizio)
data_ora_end = datetime.combine(data_fine, datetime.min.time())

# --- Dati di base (Elenco completo PDF) ---
def get_initial_data():
    return pd.DataFrame([
        {"Gruppo": 1, "Utenza": "Corte Emilia", "Durata_Ore": 24.0, "Portata_ls": 120},
        {"Gruppo": 1, "Utenza": "Pirolo", "Durata_Ore": 18.0, "Portata_ls": 90},
        {"Gruppo": 1, "Utenza": "BONFANTE", "Durata_Ore": 10.0, "Portata_ls": 85},
        {"Gruppo": 1, "Utenza": "TESSAGLI RID", "Durata_Ore": 14.0, "Portata_ls": 70},
        {"Gruppo": 1, "Utenza": "RONCOLE RID", "Durata_Ore": 16.0, "Portata_ls": 90},
        
        {"Gruppo": 2, "Utenza": "Cividale Nord A", "Durata_Ore": 48.0, "Portata_ls": 100},
        {"Gruppo": 2, "Utenza": "Cividale Nord Vecchia", "Durata_Ore": 12.0, "Portata_ls": 70},
        {"Gruppo": 2, "Utenza": "Gruppo Bocchette", "Durata_Ore": 20.0, "Portata_ls": 110},
        
        {"Gruppo": 3, "Utenza": "Belvedere Nord", "Durata_Ore": 12.0, "Portata_ls": 65},
        {"Gruppo": 3, "Utenza": "Spineca", "Durata_Ore": 10.0, "Portata_ls": 60},
        {"Gruppo": 3, "Utenza": "Madonna Lame", "Durata_Ore": 15.0, "Portata_ls": 80},
        
        {"Gruppo": 4, "Utenza": "OSSOLA 2 RID", "Durata_Ore": 12.0, "Portata_ls": 80},
        {"Gruppo": 4, "Utenza": "AGRARIA RID", "Durata_Ore": 8.0, "Portata_ls": 50},
        {"Gruppo": 4, "Utenza": "MANZOGLIO RID", "Durata_Ore": 36.0, "Portata_ls": 150},
        
        {"Gruppo": 5, "Utenza": "BREDA 3", "Durata_Ore": 12.0, "Portata_ls": 50},
        {"Gruppo": 5, "Utenza": "BREDA 4", "Durata_Ore": 12.0, "Portata_ls": 40},
        {"Gruppo": 5, "Utenza": "DELMONCELLO", "Durata_Ore": 16.0, "Portata_ls": 75},
    ])

# Inizializziamo la memoria dell'app
if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()

# Pulsante anti-panico per ripristinare la tabella
if st.sidebar.button("♻️ Ripristina dati originali"):
    st.session_state.df_canali = get_initial_data()
    st.rerun()

# --- Tabella Interattiva ---
st.subheader("📝 Tabellone Canali, Durate e Gruppi (Modificabile)")
st.info("I canali con lo stesso 'Gruppo' andranno in sequenza. Gruppi diversi irrigheranno in contemporanea.")

edited_df = st.data_editor(
    st.session_state.df_canali,
    num_rows="dynamic",
    use_container_width=True,
    column_order=["Gruppo", "Utenza", "Durata_Ore", "Portata_ls"],
    key="editor_principale"
)
st.session_state.df_canali = edited_df

# --- Calcolo Turnazione (Ciclo Continuo) ---
turni = []

# Ci assicuriamo che i dati siano validi e puliti
if not edited_df.empty and 'Gruppo' in edited_df.columns:
    df_valid = edited_df.dropna(subset=['Gruppo', 'Durata_Ore']).copy()
    df_valid['Gruppo'] = pd.to_numeric(df_valid['Gruppo'], errors='coerce')
    df_valid['Durata_Ore'] = pd.to_numeric(df_valid['Durata_Ore'], errors='coerce')
    df_valid = df_valid.dropna(subset=['Gruppo', 'Durata_Ore'])

    if not df_valid.empty and df_valid['Durata_Ore'].sum() > 0:
        gruppi_unici = sorted(df_valid['Gruppo'].unique())
        # Tracciamo quando finisce ogni gruppo per far ripartire il ciclo
        fine_per_gruppo = {g: data_ora_start for g in gruppi_unici}

        attivo = True
        while attivo:
            attivo = False
            for g in gruppi_unici:
                df_gruppo = df_valid[df_valid['Gruppo'] == g]
                corrente = fine_per_gruppo[g]

                # Se siamo ancora dentro la stagione, continuiamo a programmare
                if corrente < data_ora_end:
                    attivo = True
                    for _, row in df_gruppo.iterrows():
                        durata = float(row['Durata_Ore'])
                        if durata <= 0: 
                            continue
                            
                        fine_turno = corrente + timedelta(hours=durata)
                        
                        # Tronca se andiamo oltre la fine della stagione
                        if corrente >= data_ora_end: 
                            break
                        
                        turni.append({
                            "Gruppo": f"Gruppo {int(g)}",
                            "Utenza": row['Utenza'],
                            "Inizio": corrente,
                            "Fine": min(fine_turno, data_ora_end), # Non superare la data di fine
                            "Portata (l/s)": row.get('Portata_ls', 0)
                        })
                        corrente = fine_turno
                    
                    # Aggiorniamo la data di fine di questo ciclo per questo gruppo
                    fine_per_gruppo[g] = corrente

df_risultato = pd.DataFrame(turni)

# --- Visualizzazione Grafico ---
st.markdown("---")
st.subheader("📊 Grafico Temporale Interattivo (Gantt)")

if not df_risultato.empty:
    fig = px.timeline(
        df_risultato, 
        x_start="Inizio", 
        x_end="Fine", 
        y="Utenza", 
        color="Gruppo",
        title="Programmazione Ciclica Fino a Fine Stagione"
    )
    fig.update_yaxes(autorange="reversed")
    
    # Adatta l'altezza dinamicamente in base a quanti canali ci sono
    altezza = max(450, len(edited_df["Utenza"].unique()) * 30)
    fig.update_layout(height=altezza, xaxis_title="Calendario della Stagione")
    st.plotly_chart(fig, use_container_width=True)

    # --- Tabella Finale e Download ---
    st.subheader("📅 Dettaglio Orari Calcolati")
    df_show = df_risultato.copy()
    df_show["Inizio"] = df_show["Inizio"].dt.strftime('%d/%m/%Y %H:%M')
    df_show["Fine"] = df_show["Fine"].dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(df_show, use_container_width=True, height=350)

    # Esportazione in CSV leggibile da Excel
    csv = df_risultato.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica Orari Completi (Excel / CSV)", 
        data=csv, 
        file_name="orari_irrigazione_completi.csv", 
        mime="text/csv"
    )
else:
    st.warning("Assicurati di aver inserito dati validi (almeno un Gruppo e una Durata in ore) nella tabella superiore.")
