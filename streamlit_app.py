import streamlit as st
import pandas as pd

st.set_page_config(page_title="Genie Scout Web-App", layout="wide")
st.title("🧠 Genie Scout Web-App")

# Excel-Datei laden
@st.cache_data
def load_data():
    return pd.read_excel("Spielerdaten_Export.xlsx")

df = load_data()

# Spaltennamen bereinigen (für Sicherheit)
df.columns = df.columns.str.strip()

# Filterbereich in der Sidebar
st.sidebar.header("🔍 Filter")
positionen = sorted(df["Position"].dropna().unique())
position = st.sidebar.selectbox("Position wählen", ["Alle"] + positionen)
min_potenzial = st.sidebar.slider("Minimales Potenzial", 0, 100, 70)
max_alter = st.sidebar.slider("Maximales Alter", 15, 40, 25)

# Daten filtern
df_filtered = df.copy()
if position != "Alle":
    df_filtered = df_filtered[df_filtered["Position"] == position]

df_filtered = df_filtered[
    (df_filtered["Beste Pot Bewertung"] >= min_potenzial) &
    (df_filtered["Alter"] <= max_alter)
]

# Ergebnisse anzeigen
st.subheader(f"⚽ Gefundene Spieler: {len(df_filtered)}")
st.dataframe(df_filtered.sort_values(by="Beste Pot Bewertung", ascending=False), use_container_width=True)
