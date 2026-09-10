import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Gestione Turni Irrigui", layout="wide")
st.title("🌊 Consorzio Navarolo: Gestione Turni Irrigui")

def get_initial_data():
    return pd.DataFrame([
        {"Gruppo": 1, "Utenza": "Corte Emilia", "Durata_Ore": 24.0, "Portata_ls": 120},
        {"Gruppo": 1, "Utenza": "Pirolo", "Durata_Ore": 18.0, "Portata_ls": 90},
        {"Gruppo": 2, "Utenza": "Cividale Nord A", "Durata_Ore": 48.0, "Portata_ls": 100},
        {"Gruppo": 2, "Utenza": "Cividale Nord Vecchia", "Durata_Ore": 12.0, "Portata_ls": 70},
        {"Gruppo": 3, "Utenza": "OSSOLA 2 RID", "Durata_Ore": 12.0, "Portata_ls": 80},
        {"Gruppo": 3, "Utenza": "MANZOGLIO RID", "Durata_Ore": 36.0, "Portata_ls": 150},
        {"Gruppo": 4, "Utenza": "BREDA 3", "Durata_Ore": 12.0, "Portata_ls": 50},
        {"Gruppo": 4, "Utenza": "BREDA 4", "Durata_Ore": 12.0, "Portata_ls": 40},
    ])

if 'df_canali' not in st.session_state:
    st.session_state.df_canali = get_initial_data()

st.sidebar.header("⚙️ Impostazioni")
d_inizio = st.sidebar.date_input("Data Inizio:", datetime(2026, 4, 1).date())
t_inizio = st.sidebar.time_input("Ora Inizio:", datetime(2026, 4, 1, 8, 0).time())
d_fine = st.sidebar.date_input("Data Fine:", datetime(2026, 9, 22).date())
ciclo_giorni = st.sidebar.number_input("Durata Ciclo (Giorni):", min_value=1, value=14)

start_stagione = datetime.combine(d_inizio, t_inizio)
end_stagione = datetime.combine(d_fine, datetime.min.time())

if st.sidebar.button("♻️ Ripristina Dati Iniziali"):
    st.session_state.df_canali = get_initial_data()
    st.rerun()

st.subheader("📝 Tabellone Canali (Modificabile)")
edited_df = st.data_editor(
    st.session_state.df_canali,
    num_rows="dynamic",
    use_container_width=True,
    column_order=["Gruppo", "Utenza", "Durata_Ore", "Portata_ls"]
)
st.session_state.df_canali = edited_df

turni = []
if not edited_df.empty and 'Gruppo' in edited_df.columns:
    df_valid = edited_df.dropna(subset=['Gruppo', 'Durata_Ore']).copy()
    df_valid['Gruppo'] = pd.to_numeric(df_valid['Gruppo'], errors='coerce')
    df_valid['Durata_Ore'] = pd.to_numeric(df_valid['Durata_Ore'], errors='coerce')
    df_valid = df_valid.dropna()

    if not df_valid.empty and df_valid['Durata_Ore'].sum() > 0:
        for g in sorted(df_valid['Gruppo'].unique()):
            df_g = df_valid[df_valid['Gruppo'] == g]
            inizio_ciclo = start_stagione
            
            while inizio_ciclo < end_stagione:
                corrente = inizio_ciclo
                for _, row in df_g.iterrows():
                    durata = float(row['Durata_Ore'])
                    if durata <= 0: continue
                    fine_turno = corrente + timedelta(hours=durata)
                    
                    if corrente < end_stagione:
                        turni.append({
                            "Gruppo": f"Gruppo {int(g)}",
                            "Utenza": row['Utenza'],
                            "Inizio": corrente,
                            "Fine": min(fine_turno, end_stagione),
                            "Portata (l/s)": row.get('Portata_ls', 0)
                        })
                    corrente = fine_turno
                inizio_ciclo += timedelta(days=ciclo_giorni)

df_risultato = pd.DataFrame(turni)

st.markdown("---")
if not df_risultato.empty:
    st.subheader("📊 Grafico Gantt")
    fig = px.timeline(df_risultato, x_start="Inizio", x_end="Fine", y="Utenza", color="Gruppo")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=max(400, len(edited_df['Utenza'].unique()) * 30))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📅 Tabella Orari")
    df_show = df_risultato.copy()
    df_show["Inizio"] = df_show["Inizio"].dt.strftime('%d/%m/%Y %H:%M')
    df_show["Fine"] = df_show["Fine"].dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(df_show, use_container_width=True)

    csv = df_risultato.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica CSV", data=csv, file_name="orari_stagione.csv", mime="text/csv")
else:
    st.warning("Inserisci dati validi nella tabella per generare il programma.")
