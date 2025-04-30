import streamlit as st
import pandas as pd

st.set_page_config(page_title="Genie Scout Web-App", layout="wide")
st.title("🧠 Genie Scout Web-App")

# Datei-Upload im Browser
uploaded_file = st.file_uploader("📂 Lade deine Excel-Datei hoch (aus Genie Scout)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    try:
        # Spalten bereinigen und in Zahlen umwandeln
        numeric_columns = ["Beste Pot Bewertung", "Beste Bewertung", "Alter", "Wert", "Gehalt", "Zufriedenheit"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["Beste Pot Bewertung", "Beste Bewertung", "Alter"])

        # Sidebar-Filter: Basissuche
        st.sidebar.header("🔍 Grundlegende Filter")
        positionen = sorted(df["Position"].dropna().unique())
        position = st.sidebar.selectbox("Position wählen", ["Alle"] + positionen)
        min_potenzial = st.sidebar.slider("Minimales Potenzial", 0, 100, 70)
        max_alter = st.sidebar.slider("Maximales Alter", 15, 40, 25)

        # Erweiterte Modi-Auswahl
        st.sidebar.header("🎯 Scouting-Modus")
        modus = st.sidebar.selectbox("Was suchst du?", [
            "Alle realistischen Spieler",
            "Top-Talente (jung & hohes Potenzial)",
            "Schnäppchen (niedriger Wert & unzufrieden)",
            "Soforthilfe (hohe Bewertung)",
            "Eigene Auswahl"
        ])

        # Dynamische Einstellungen
        max_wert = st.sidebar.slider("Maximaler Marktwert (€)", 0, int(df["Wert"].max()), 2000000)
        max_gehalt = st.sidebar.slider("Maximales Gehalt (€)", 0, int(df["Gehalt"].max()), 50000)
        max_zufriedenheit = st.sidebar.slider("Max. Zufriedenheit", 1, 10, 6)

        # Scouting-Score Gewichtung
        st.sidebar.header("📈 Score-Gewichtung")
        w_pot = st.sidebar.slider("Gewichtung Potenzial", 0.0, 1.0, 0.6)
        w_akt = st.sidebar.slider("Gewichtung Bewertung", 0.0, 1.0, 0.3)
        w_alt = st.sidebar.slider("Gewichtung Alter (negativ)", 0.0, 1.0, 0.1)

        df["Scouting-Score"] = (
            df["Beste Pot Bewertung"] * w_pot +
            df["Beste Bewertung"] * w_akt -
            df["Alter"] * w_alt
        )

        # Modus-Spezifische Filter anwenden
        df_filtered = df.copy()
        if position != "Alle":
            df_filtered = df_filtered[df_filtered["Position"] == position]

        if modus == "Top-Talente (jung & hohes Potenzial)":
            df_filtered = df_filtered[(df_filtered["Alter"] <= 21) & (df_filtered["Beste Pot Bewertung"] >= 75)]
        elif modus == "Schnäppchen (niedriger Wert & unzufrieden)":
            df_filtered = df_filtered[(df_filtered["Wert"] <= max_wert) & (df_filtered["Zufriedenheit"] <= max_zufriedenheit)]
        elif modus == "Soforthilfe (hohe Bewertung)":
            df_filtered = df_filtered[df_filtered["Beste Bewertung"] >= 75]
        elif modus == "Alle realistischen Spieler":
            df_filtered = df_filtered[
                (df_filtered["Beste Pot Bewertung"] >= min_potenzial) &
                (df_filtered["Alter"] <= max_alter) &
                (df_filtered["Wert"] <= max_wert) &
                (df_filtered["Gehalt"] <= max_gehalt) &
                (df_filtered["Zufriedenheit"] <= max_zufriedenheit)
            ]
        else:
            df_filtered = df_filtered[(df_filtered["Beste Pot Bewertung"] >= min_potenzial) & (df_filtered["Alter"] <= max_alter)]

        # Favoriten-Auswahl
        st.subheader(f"⚽ Gefundene Spieler: {len(df_filtered)}")
        favoriten = st.multiselect("⭐ Spieler als Favoriten markieren", df_filtered["Name"].tolist())
        df_filtered["Favorit"] = df_filtered["Name"].isin(favoriten)

        st.dataframe(
            df_filtered.sort_values(by=["Favorit", "Scouting-Score"], ascending=[False, False]),
            use_container_width=True
        )

        # Detailansicht eines Spielers
        st.subheader("📋 Spieler im Detail")
        namen = df_filtered["Name"].dropna().unique().tolist()
        ausgewählt = st.selectbox("Spieler auswählen", namen)
        spieler = df_filtered[df_filtered["Name"] == ausgewählt].iloc[0]

        def safe(val, unit="", digits=0):
            if pd.isna(val): return "–"
            if isinstance(val, float) and digits: return f"{val:.{digits}f}{unit}"
            if isinstance(val, (int, float)): return f"{int(val)}{unit}"
            return str(val)

        st.markdown(f"""
        **Name:** {safe(spieler['Name'])}  
        **Nation:** {safe(spieler['Nation'])}  
        **Verein:** {safe(spieler['Verein'])}  
        **Position:** {safe(spieler['Position'])}  
        **Alter:** {safe(spieler['Alter'])}  
        **Bewertung:** {safe(spieler['Beste Bewertung'])}  
        **Potenzial:** {safe(spieler['Beste Pot Bewertung'])}  
        **Zufriedenheit:** {safe(spieler['Zufriedenheit'])}  
        **Wert:** {safe(spieler['Wert'], ' €')}  
        **Gehalt:** {safe(spieler['Gehalt'], ' €')}  
        **Score:** {safe(spieler['Scouting-Score'], '', 1)}  
        **Favorit:** {'✅' if spieler.get('Favorit', False) else '—'}
        """)

    except Exception as e:
        st.error(f"❌ Fehler beim Einlesen oder Verarbeiten der Datei: {e}")
else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")

