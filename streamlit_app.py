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
        """Extrahiert den Prozentsatz aus der Bewertung und Potenzialspalte"""
        if isinstance(s, str):
            match = re.search(r"([\d.]+)%", s)
            return float(match.group(1)) if match else None
        return None

    # Potenzial- und Bewertungsprozentsatz extrahieren
    df["Potenzial%"] = df["Beste Pot Bewertung"].apply(extract_percentage)
    df["Bewertung%"] = df["Beste Bewertung"].apply(extract_percentage)

    # Berechnung von CA und PA auf Basis von Genie Scout:
    df["Potenzial"] = (df["Potenzial%"] / 100) * 200  # Potenzial skaliert auf 200
    df["Bewertung"] = (df["Bewertung%"] / 100) * 200  # Bewertung skaliert auf 200

    # Andere relevante Daten umwandeln
    for col in ["Alter", "Wert", "Gehalt", "Zufriedenheit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Potenzial", "Bewertung", "Alter"])

    # 🎯 Scouting-Modi
    st.sidebar.header("🎯 Scouting-Modus")
    modus = st.sidebar.selectbox("Modus wählen", ["Manuell", "Top-Talente", "Schnäppchen", "Soforthilfe"])
    if modus == "Top-Talente":
        df = df[(df["Alter"] <= 21) & (df["Potenzial"] >= 150)]
    elif modus == "Schnäppchen":
        df = df[(df["Wert"] <= 1_000_000) & (df["Zufriedenheit"] <= 50)]
    elif modus == "Soforthilfe":
        df = df[(df["Bewertung"] >= 130) & (df["Alter"] <= 30)]

    # 📏 Eigene Filter
    st.sidebar.header("📏 Eigene Anforderungen")
    min_ca = st.sidebar.number_input("Minimale aktuelle Stärke (CA)", 0, 200, 0)
    min_pa = st.sidebar.number_input("Minimales Potenzial (PA)", 0, 200, 0)
    max_age = st.sidebar.number_input("Maximales Alter", 0, 100, 100)
    df = df[(df["Bewertung"] >= min_ca) & (df["Potenzial"] >= min_pa) & (df["Alter"] <= max_age)]

    # 💰 Realismusfilter
    st.sidebar.header("💰 Realismusfilter")
    max_gehalt = st.sidebar.number_input("Max. Gehalt (€)", 0, 2_000_000, 50000)
    max_wert = st.sidebar.number_input("Max. Marktwert (€)", 0, 500_000_000, 2_000_000)
    max_zufr = st.sidebar.number_input("Max. Zufriedenheit", 0, 100, 60)
    df = df[(df["Gehalt"] <= max_gehalt) & (df["Wert"] <= max_wert) & (df["Zufriedenheit"] <= max_zufr)]

    # 🧪 Attributfilter
    st.sidebar.header("🧪 Attribut-Filter")
    attr_cols = [col for col in df.columns if df[col].dtype in ["int64", "float64"]
                 and col not in ["Potenzial", "Bewertung", "Alter", "Wert", "Gehalt", "Zufriedenheit", "Score"]]
    selected_attrs = st.sidebar.multiselect("Attribute auswählen", attr_cols)
    for attr in selected_attrs:
        min_val = st.sidebar.number_input(f"Min. {attr}", 1, 20, 10)
        df = df[df[attr] >= min_val]

    # 📌 Positionsfilter
    st.sidebar.header("📌 Positionsfilter")
    pos_filter = st.sidebar.text_input("Position enthält (z. B. ST, DM, RL)", "").upper()
    if pos_filter:
        df = df[df["Position"].str.contains(pos_filter, na=False)]

    # 📈 Score zur Sortierung
    st.sidebar.header("📈 Score-Gewichtung (optional)")
    w_pot = st.sidebar.number_input("Gewichtung Potenzial", 0.0, 1.0, 0.6)
    w_akt = st.sidebar.number_input("Gewichtung Bewertung", 0.0, 1.0, 0.3)
    w_alt = st.sidebar.number_input("Gewichtung Alter (negativ)", 0.0, 1.0, 0.1)
    df["Score"] = df["Potenzial"] * w_pot + df["Bewertung"] * w_akt - df["Alter"] * w_alt

    # ⭐ Favoriten
    st.subheader(f"⚽ Gefundene Spieler: {len(df)}")
    favoriten = st.multiselect("⭐ Favoriten markieren", df["Name"].tolist())
    df["Favorit"] = df["Name"].isin(favoriten)

    # Spalten sortieren wie Genie Scout
    anzeige_cols = [
        "Name", "Position", "Verein", "Alter", "Bewertung", "Potenzial",
        "Wert", "Gehalt", "Zufriedenheit", "Nation", "Score", "Favorit"
    ]
    anzeige_cols = [col for col in anzeige_cols if col in df.columns]
    rest = [col for col in df.columns if col not in anzeige_cols]
    df_sorted = df[anzeige_cols + rest]

    st.dataframe(df_sorted.sort_values(by=["Favorit", "Score"], ascending=[False, False]), use_container_width=True)

    # 📋 Detailansicht
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
        **Aktuelle Stärke (CA):** {safe(s['Bewertung'])}  
        **Potenzial (PA):** {safe(s['Potenzial'])}  
        **Zufriedenheit:** {safe(s['Zufriedenheit'])}  
        **Marktwert:** {safe(s['Wert'], ' €')}  
        **Gehalt:** {safe(s['Gehalt'], ' €')}  
        **Score:** {safe(s['Score'], '', 1)}  
        **Favorit:** {"✅" if s.get("Favorit") else "—"}
        """)

else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")
