import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Genie Scout Web-App", layout="wide")
st.title("🧠 Genie Scout Web-App")

# Datei-Upload
uploaded_file = st.file_uploader("📂 Excel-Datei aus Genie Scout hochladen", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        # Hilfsfunktion: Prozentwert aus Text wie "73.2% (M)" extrahieren
        def extract_percentage(s):
            if isinstance(s, str):
                match = re.search(r"([\d.]+)%", s)
                return float(match.group(1)) if match else None
            return None

        # Prozentwerte extrahieren
        df["Potenzial"] = df["Beste Pot Bewertung"].apply(extract_percentage)
        df["Bewertung"] = df["Beste Bewertung"].apply(extract_percentage)

        # Weitere Umwandlungen
        df["Alter"] = pd.to_numeric(df["Alter"], errors="coerce")
        df["Wert"] = pd.to_numeric(df["Wert"], errors="coerce")
        df["Gehalt"] = pd.to_numeric(df["Gehalt"], errors="coerce")
        df["Zufriedenheit"] = pd.to_numeric(df["Zufriedenheit"], errors="coerce")

        df = df.dropna(subset=["Potenzial", "Bewertung", "Alter"])

        # Score berechnen
