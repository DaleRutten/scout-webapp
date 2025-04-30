import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Genie Scout Web-App", layout="wide")
st.title("🧠 Genie Scout Web-App")

uploaded_file = st.file_uploader("📂 Excel-Datei aus Genie Scout hochladen", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    def extract_percentage(s):
        if isinstance(s, str):
            match = re.search(r"([\d.]+)%", s)
            return float(match.group(1)) if match else None
        return None

    df["Potenzial"] = df["Beste Pot Bewertung"].apply(extract_percentage)
    df["Bewertung"] = df["Beste Bewertung"].apply(extract_percentage)

    for col in ["Alter", "Wert", "Gehalt", "Zufriedenheit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Potenzial", "Bewertung", "Alter"])

    # SCOUTING-MODI
    st.sidebar.header("🎯 Scouting-Modus")
    modus = st.sidebar.selectbox("Wähle Modus", ["Manuell", "Top-Talente", "Schnäppchen", "Soforthilfe"])

    if modus == "Top-Talente":
        df = df[(df["Alter"] <= 21) & (df["Potenzial"] >= 80)]
    elif modus == "Schnäppchen":
        df = df[(df["Wert"] < 1_000_000) & (df["Zufriedenheit"] <= 50)]
    elif modus == "Soforthilfe":
        df = df[(df["Bewertung"] >= 75) & (df["Alter"] <= 30)]

    # ATTRIBUTE-FILTER
    st.sidebar.header("🧪 Attribut-Filter")
    attribute_cols = [col for col in df.columns if df[col].dtype in ["int64", "float64"] and col not in ["Potenzial", "Bewertung", "Alter", "Wert", "Gehalt", "Zufriedenheit", "Score"]]
    if attribute_cols:
        selected_attrs = st.sidebar.multiselect("Attribute auswählen", attribute_cols)
        for attr in selected_attrs:
            min_val = st.sidebar.slider(f"Min. {attr}", 1, 20, 10)
            df = df[df[attr] >= min_val]

    # SCORE-BERECHNUNG
    st.sidebar.header("📈 Score-Gewichtung")
    w_pot = st.sidebar.slider("Potenzial", 0.0, 1.0, 0.6)
    w_akt = st.sidebar.slider("Bewertung", 0.0, 1.0, 0.3)
    w_alt = st.sidebar.slider("Alter (negativ)", 0.0, 1.0, 0.1)

    df["Score"] = df["Potenzial"] * w_pot + df["Bewertung"] * w_akt - df["Alter"] * w_alt

    # POSITIONSFILTER
    st.sidebar.header("📌 Positionsfilter")
    pos_filter = st.sidebar.text_input("Position enthält (z. B. ST, DM, RL)", "").upper()
    if pos_filter:
        df = df[df["Position"].str.contains(pos_filter, na=False)]

    # VERTRAGSFILTER
    st.sidebar.header("💰 Vertrags-/Realismusfilter")
    max_gehalt = st.sidebar.number_input("Max. Gehalt (€)", value=50000)
    max_wert = st.sidebar.number_input("Max. Marktwert (€)", value=2_000_000)
    max_zufr = st.sidebar.slider("Max. Zufriedenheit", 0, 100, 60)

    df = df[(df["Gehalt"] <= max_gehalt) & (df["Wert"] <= max_wert) & (df["Zufriedenheit"] <= max_zufr)]

    # FAVORITEN
    st.subheader(f"⚽ Gefundene Spieler: {len(df)}")
    favoriten = st.multiselect("⭐ Favoriten markieren", df["Name"].tolist())
    df["Favorit"] = df["Name"].isin(favoriten)

    # TABELLE
    st.dataframe(df.sort_values(by=["Favorit", "Score"], ascending=[False, False]), use_container_width=True)

    # DETAILANSICHT
    st.subheader("📋 Spieler im Detail")

    def safe(val, unit="", digits=0):
        if pd.isna(val):
            return "–"
        if isinstance(val, float) and digits:
            return f"{val:.{digits}f}{unit}"
        if isinstance(val, (int, float)):
            return f"{int(val)}{unit}"
        return str(val)

    namen = df["Name"].dropna().unique().tolist()
    ausgewählt = st.selectbox("Spieler auswählen", namen)
    spieler = df[df["Name"] == ausgewählt].reset_index(drop=True)

    if not spieler.empty:
        s = spieler.iloc[0]
        st.markdown(f"""
        **Name:** {safe(s['Name'])}  
        **Nation:** {safe(s['Nation'])}  
        **Verein:** {safe(s['Verein'])}  
        **Position:** {safe(s['Position'])}  
        **Alter:** {safe(s['Alter'])}  
        **Bewertung:** {safe(s['Bewertung'], '%', 1)}  
        **Potenzial:** {safe(s['Potenzial'], '%', 1)}  
        **Zufriedenheit:** {safe(s['Zufriedenheit'])}  
        **Wert:** {safe(s['Wert'], ' €')}  
        **Gehalt:** {safe(s['Gehalt'], ' €')}  
        **Score:** {safe(s['Score'], '', 1)}  
        **Favorit:** {"✅" if s.get("Favorit") else "—"}
        """)

else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")
