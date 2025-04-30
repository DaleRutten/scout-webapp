import streamlit as st
import pandas as pd

st.set_page_config(page_title="Genie Scout Web-App", layout="wide")
st.title("🧠 Genie Scout Web-App")

# Datei-Upload im Browser
uploaded_file = st.file_uploader("📂 Lade deine Excel-Datei hoch (aus Genie Scout)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        # Sidebar-Filter
        st.sidebar.header("🔍 Filter")
        positionen = sorted(df["Position"].dropna().unique())
        position = st.sidebar.selectbox("Position wählen", ["Alle"] + positionen)
        min_potenzial = st.sidebar.slider("Minimales Potenzial", 0, 100, 70)
        max_alter = st.sidebar.slider("Maximales Alter", 15, 40, 25)

        # Filter anwenden
        df_filtered = df.copy()
        if position != "Alle":
            df_filtered = df_filtered[df_filtered["Position"] == position]

        df_filtered = df_filtered[
            (df_filtered["Beste Pot Bewertung"] >= min_potenzial) &
            (df_filtered["Alter"] <= max_alter)
        ]

        st.subheader(f"⚽ Gefundene Spieler: {len(df_filtered)}")
        st.dataframe(df_filtered.sort_values(by="Beste Pot Bewertung", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Fehler beim Einlesen der Datei: {e}")
else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")
