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

        # Potenzial & Alter als Zahl erzwingen
        df["Beste Pot Bewertung"] = pd.to_numeric(df["Beste Pot Bewertung"], errors="coerce")
        df["Alter"] = pd.to_numeric(df["Alter"], errors="coerce")

        # Ungültige Zeilen rausfiltern
        df = df.dropna(subset=["Beste Pot Bewertung", "Alter"])

        # Sidebar-Filter
