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

        # Spalten bereinigen und in Zahlen umwandeln
        df["Beste Pot Bewertung"] = pd.to_numeric(df["Beste Pot Bewertung"], errors="coerce")
        df["Beste Bewertung"] = pd.to_numeric(df["Beste Bewertung"], errors="coerce")
        df["Alter"] = pd.to_numeric(df["Alter"], errors="coerce")
        df["Wert"] = pd.to_numeric(df["Wert"], errors="coerce")
        df["Gehalt"] = pd.to_numeric(df["Gehalt"], errors="coerce")
        df["Zufriedenheit"] = pd.to_numeric(df["Zufriedenheit"], errors="coerce")

        df = df.dropna(subset=["Beste Pot Bewertung", "Beste Bewertung", "Alter"])

        # Sidebar-Filter
        st.sidebar.header("🔍 Filter")
        positionen = sorted(df["Position"].dropna().unique())
        position = st.sidebar.selectbox
