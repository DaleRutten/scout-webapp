import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Genie Scout Web-App", layout="wide")
st.title("🧠 Genie Scout Web-App")

# Datei-Upload
uploaded_file = st.file_uploader("📂 Excel-Datei aus Genie Scout hochladen", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Prozentwerte aus z. B. "73.2% (M)" extrahieren
    def extract_percentage(s):
        if isinstance(s, str):
            match = re.search(r"([\d.]+)%", s)
            return float(match.group(1)) if match else None
        return None

    df["Potenzial"] = df["Beste Pot Bewertung"].apply(extract_percentage)
    df["Bewertung"] = df["Beste Bewertung"].apply(extract_percentage)

    # Spalten umwandeln
    df["Alter"] = pd.to_numeric(df["Alter"], errors="coerce")
    df["Wert"] = pd.to_numeric(df["Wert"], errors="coerce")
    df["Gehalt"] = pd.to_numeric(df["Gehalt"], errors="coerce")
    df["Zufriedenheit"] = pd.to_numeric(df["Zufriedenheit"], errors="coerce")
    df = df.dropna(subset=["Potenzial", "Bewertung", "Alter"])

    # Score berechnen
    st.sidebar.header("📈 Score-Gewichtung")
    w_pot = st.sidebar.slider("Potenzial", 0.0, 1.0, 0.6)
    w_akt = st.sidebar.slider("Bewertung", 0.0, 1.0, 0.3)
    w_alt = st.sidebar.slider("Alter (negativ)", 0.0, 1.0, 0.1)

    df["Score"] = (
        df["Potenzial"] * w_pot +
        df["Bewertung"] * w_akt -
        df["Alter"] * w_alt
    )

    # Positionssuche (Freitext)
    st.sidebar.header("📌 Positionssuche")
    pos_filter =_
