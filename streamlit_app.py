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
        position = st.sidebar.selectbox("Position wählen", ["Alle"] + positionen)
        min_potenzial = st.sidebar.slider("Minimales Potenzial", 0, 100, 70)
        max_alter = st.sidebar.slider("Maximales Alter", 15, 40, 25)

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

        # Haupt-Filter anwenden
        df_filtered = df.copy()
        if position != "Alle":
            df_filtered = df_filtered[df_filtered["Position"] == position]

        df_filtered = df_filtered[
            (df_filtered["Beste Pot Bewertung"] >= min_potenzial) &
            (df_filtered["Alter"] <= max_alter)
        ]

        # Weitere optionale Filter
        st.sidebar.header("💰 Realistische Spieler")
        max_wert = st.sidebar.slider("Maximaler Marktwert (€)", 0, int(df["Wert"].max()), 2000000)
        max_gehalt = st.sidebar.slider("Maximales Gehalt (€)", 0, int(df["Gehalt"].max()), 50000)
        max_zufriedenheit = st.sidebar.slider("Max. Zufriedenheit", 1, 10, 6)

        df_filtered = df_filtered[
            (df_filtered["Wert"] <= max_wert) &
            (df_filtered["Gehalt"] <= max_gehalt) &
            (df_filtered["Zufriedenheit"] <= max_zufriedenheit)
        ]

        # Favoriten-Auswahl
        st.subheader(f"⚽ Gefundene Spieler: {len(df_filtered)}")
        favoriten = st.multiselect("⭐ Spieler als Favoriten markieren", df_filtered["Name"].tolist())
        df_filtered["Favorit"] = df_filtered["Name"].isin(favoriten)

        # Spieler-Tabelle
        st.dataframe(
            df_filtered.sort_values(by=["Favorit", "Scouting-Score"], ascending=[False, False]),
            use_container_width=True
        )

        # Spieler im Detail
        st.subheader("📋 Spieler im Detail")
        namen = df_filtered["Name"].dropna().unique().tolist()
        ausgewählt = st.selectbox("Spieler auswählen", namen)

        spieler = df_filtered[df_filtered["Name"] == ausgewählt].iloc[0]

        st.markdown(f"""
        **Name:** {spieler['Name']}  
        **Nation:** {spieler['Nation']}  
        **Verein:** {spieler['Verein']}  
        **Position:** {spieler['Position']}  
        **Alter:** {int(spieler['Alter'])}  
        **Bewertung:** {int(spieler['Beste Bewertung'])}  
        **Potenzial:** {int(spieler['Beste Pot Bewertung'])}  
        **Zufriedenheit:** {int(spieler['Zufriedenheit'])}  
        **Wert:** {int(spieler['Wert'])} €  
        **Gehalt:** {int(spieler['Gehalt'])} €  
        **Score:** {spieler['Scouting-Score']:.1f}  
        **Favorit:** {"✅" if spieler["Favorit"] else "—"}
        """)

    except Exception as e:
        st.error(f"❌ Fehler beim Einlesen oder Verarbeiten der Datei: {e}")
else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")
