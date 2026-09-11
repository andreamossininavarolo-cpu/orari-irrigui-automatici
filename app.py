import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Turni Navarolo", layout="wide")
st.title("🌊 Turni Irrigui")

# --- Dati Iniziali ---
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

# --- Menu Laterale ---
st.sidebar.header("⚙️ Impostazioni")
d_inizio = st.sidebar.date_input("Inizio:", datetime(2026, 4, 1).date())
t_inizio = st.sidebar.time_input("Ora:", datetime(2026, 4, 1, 8, 0).time())
d_fine = st.sidebar.date_input("Fine:", datetime(2026, 9, 22).date())
ciclo_giorni = st.sidebar.number_input("Ciclo (Giorni):", min_value=1, value=14)

start_stagione = datetime.combine(d_inizio, t_inizio)
end_stagione = datetime.combine(d_fine, datetime.min.time())

if st.sidebar.button("♻️ Reset Dati"):
    st.session_state.df_canali = get_initial_data()
    st.rerun()

# --- Tabella Interattiva Mobile-Friendly ---
st.subheader("📝 Modifica Canali")
edited_df = st.data_editor(
    st.session_state.df_canali,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True, # Nasconde i numeri di riga per salvare spazio!
    column_config={
        "Gr.": st.column_config.NumberColumn("Gr.", min_value=1, step=1, width="small", required=True),
        "Canale": st.column_config.TextColumn("Canale", width="medium", required=True),
        "Ore": st.column_config.NumberColumn("Ore", min_value=0.1, step=0.5, format="%.1f", width="small", required=True),
        "l/s": st.column_config.NumberColumn("l/s", width="small"),
    }
)
st.session_state.df_canali = edited_df

# --- Calcolo Turnazione ---
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
                            "Gruppo": f"Gr. {int(g)}",
                            "Canale": row['Canale'],
                            "Inizio": corrente,
                            "Fine": min(fine_turno, end_stagione),
                            "l/s": row.get('l/s', 0)
                        })
                    corrente = fine_turno
                inizio_ciclo += timedelta(days=ciclo_giorni)

df_risultato = pd.DataFrame(turni)

# --- Visualizzazione ---
st.markdown("---")
if not df_risultato.empty:
    st.subheader("📊 Grafico (Usa 2 dita per zoomare)")
    
    fig = px.timeline(
        df_risultato, 
        x_start="Inizio", 
        x_end="Fine", 
        y="Canale", 
        color="Gruppo",
        hover_data={"Gruppo": True, "Inizio": "|%d/%m %H:%M", "Fine": "|%d/%m %H:%M"}
    )
    
    fig.update_yaxes(autorange="reversed", title_text="", tickfont=dict(size=10))
    
    # Ottimizzazioni Asse X per Mobile
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='LightGray', 
        tickformat="%d/%m", # Formato data più corto
        tickangle=-45,      # Inclina le date per non sovrapporle
        rangeslider_visible=False # Su mobile usiamo il Pinch-to-Zoom (due dita)
    )
    
    fig.update_layout(
        height=max(400, len(edited_df['Canale'].unique()) * 45),
        margin=dict(t=10, b=10, l=0, r=0), # Margini azzerati ai lati
        legend=dict(
            orientation="h", # Legenda orizzontale
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title=""
        )
    )
    # Nascondiamo la fastidiosa barra degli strumenti fluttuante
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.subheader("📅 Orari")
    df_show = df_risultato.copy()
    # Formato più compatto anche per la tabella finale
    df_show["Inizio"] = df_show["Inizio"].dt.strftime('%d/%m %H:%M')
    df_show["Fine"] = df_show["Fine"].dt.strftime('%d/%m %H:%M')
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    csv = df_risultato.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica CSV", data=csv, file_name="orari.csv", mime="text/csv")
else:
    st.warning("Inserisci dati validi per generare il programma.")
