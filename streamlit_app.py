import pandas as pd
import streamlit as st

# Titel der App
st.title("Genie Scout Web-App")

# Datei hochladen
uploaded_file = st.file_uploader("📂 Excel-Datei aus Genie Scout hochladen", type=["xlsx"])

if uploaded_file:
    # Daten laden
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Entfernen von Leerzeichen in den Spaltennamen

    # Überprüfe die Spaltennamen und zeige sie an
    st.write("Verfügbare Spalten:")
    st.write(df.columns)

    # Berechnung von CA und PA auf Basis vorhandener Attribute
    try:
        # Dynamische Berechnung von CA und PA, auch wenn die Namen nicht genau passen
        # Beispiel: CA = Durchschnitt aus verschiedenen technischen Attributen
        ca_columns = ["Ballkontrolle", "Abschluss", "Pässe", "Flanken", "Dribbling"]
        pa_columns = ["Konzentration", "Aggressivität", "Teamwork", "Flair", "Kondition"]

        # Nur die Spalten verwenden, die in der Excel-Datei existieren
        available_ca_columns = [col for col in ca_columns if col in df.columns]
        available_pa_columns = [col for col in pa_columns if col in df.columns]

        # Berechne CA und PA nur, wenn mindestens eine passende Spalte vorhanden ist
        if available_ca_columns:
            df["CA"] = df[available_ca_columns].mean(axis=1)
        else:
            st.warning("Es konnten keine passenden Spalten für CA gefunden werden!")

        if available_pa_columns:
            df["PA"] = df[available_pa_columns].mean(axis=1)
        else:
            st.warning("Es konnten keine passenden Spalten für PA gefunden!")

    except Exception as e:
        st.error(f"Ein Fehler trat auf: {e}")
        st.stop()

    # Überprüfe, ob CA und PA jetzt in der DataFrame existieren
    if "CA" not in df.columns or "PA" not in df.columns:
        st.error("Die Spalten 'CA' oder 'PA' konnten nicht berechnet werden.")
        st.stop()

    # Sidebar Filter
    st.sidebar.header("Filtern nach Attributen")
    min_age = st.sidebar.slider("Minimales Alter", 16, 40, 18)
    max_age = st.sidebar.slider("Maximales Alter", 18, 40, 30)
    min_value = st.sidebar.number_input("Minimale Marktwert (€)", 0, int(df['Wert'].max()), 1000000)
    max_value = st.sidebar.number_input("Maximale Marktwert (€)", 1000000, int(df['Wert'].max()), 50000000)
    min_ca = st.sidebar.slider("Minimale Aktuelle Fähigkeit (CA)", 0, 200, 120)  # Aktuelle Fähigkeit
    max_ca = st.sidebar.slider("Maximale Aktuelle Fähigkeit (CA)", 0, 200, 150)  # Aktuelle Fähigkeit
    min_pa = st.sidebar.slider("Minimales Potenzielles Potenzial (PA)", 0, 200, 130)  # Potenzielles Potenzial
    max_pa = st.sidebar.slider("Maximales Potenzielles Potenzial (PA)", 0, 200, 180)  # Potenzielles Potenzial

    # Nationalitäten-Filter (alphabetisch sortiert)
    nation_filter = st.sidebar.multiselect("Nationalität", sorted(df["Nation"].unique()))

    # Ligen-Filter (alphabetisch sortiert und ergänzt mit Fußball Manager 2024 Ligen)
    liga_filter = st.sidebar.multiselect("Liga", sorted([
        "Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", 
        "Eredivisie", "Primeira Liga", "Brasileirão", "MLS", "Argentinian Primera División",
        "J-League", "A-League", "Saudi Pro League", "Chinese Super League"
    ]))

    # EU-Bürger Filter
    eu_citizens = st.sidebar.checkbox("Nur EU-Bürger", False)

    # Daten filtern
    filtered_df = df[
        (df["Alter"] >= min_age) & 
        (df["Alter"] <= max_age) &
        (df["Wert"] >= min_value) & 
        (df["Wert"] <= max_value) &
        (df["CA"] >= min_ca) & 
        (df["CA"] <= max_ca) & 
        (df["PA"] >= min_pa) & 
        (df["PA"] <= max_pa)
    ]

    if nation_filter:
        filtered_df = filtered_df[filtered_df["Nation"].isin(nation_filter)]

    if liga_filter:
        filtered_df = filtered_df[filtered_df["Verein"].isin(liga_filter)]

    if eu_citizens:
        # Hier wird angenommen, dass es eine Spalte 'EU' gibt, die angibt, ob ein Spieler EU-Bürger ist
        filtered_df = filtered_df[filtered_df['EU'] == 1]

    # Daten anzeigen
    st.write(f"Gefundene Spieler: {len(filtered_df)}")
    st.dataframe(filtered_df)

    # Erweiterte Filterung: Vertragsdetails, Reputation etc.
    st.sidebar.header("Vertragsdetails")
    contract_status = st.sidebar.selectbox("Vertragsstatus", ["Verlässt aufgrund des Bosman-Urts", "Aktiv", "Auslaufend"])
    filtered_df = filtered_df[filtered_df["Vertrag"] == contract_status]

    # Zusatzoptionen: Spieler suchen, die die Bosman-Regel erfüllen
    bosman_rule = st.sidebar.checkbox("Nur Bosman-Spieler (Verlassen aufgrund des Bosman-Urts)", False)
    if bosman_rule:
        filtered_df = filtered_df[filtered_df["Vertrag"] == "Verlässt aufgrund des Bosman-Urts"]

    # Spielerpositionen-Filter: Sortiert nach der üblichen Aufstellung
    st.sidebar.header("Spieler-Positionen")
    positions = ["TW", "IV", "ZDM", "ZOM", "ZM", "LM", "RM", "LF", "RF", "ST"]  # Torwart, Verteidiger, Mittelfeld, Stürmer
    position_filter = st.sidebar.multiselect("Positionen", positions, default=positions)

    filtered_df = filtered_df[filtered_df["Position"].isin(position_filter)]

    # Spieler sortieren
    st.sidebar.header("Sortieren nach:")
    sort_by = st.sidebar.selectbox("Sortiere nach", ["Wert", "CA", "PA", "Alter", "Aktuelle Fähigkeit"])
    ascending = st.sidebar.checkbox("Aufsteigend sortieren", True)

    # Daten sortieren
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

    # Anzeige der Tabelle mit gefilterten Spielern
    st.dataframe(filtered_df)

    # Spielerprofil (detallierte Ansicht, falls angeklickt)
    player_details = st.selectbox("Wählen Sie einen Spieler aus für detaillierte Ansicht:", filtered_df["Name"].unique())
    selected_player = filtered_df[filtered_df["Name"] == player_details]

    # Anzeige des Spielerprofils
    if not selected_player.empty:
        st.write("### Spielerprofil:")
        st.write(selected_player.iloc[0][["Name", "Nation", "Position", "Wert", "Vertrag", "CA", "PA"]])
        st.write("### Technische Attribute:")
        st.write(selected_player.iloc[0][["Flanken", "Abschluss", "Ballkontrolle", "Pässe", "Tackling"]])
        st.write("### Mentale Attribute:")
        st.write(selected_player.iloc[0][["Aggressivität", "Konzentration", "Nervenstärke", "Teamwork", "Flair"]])
        st.write("### Physische Attribute:")
        st.write(selected_player.iloc[0][["Sprintgeschwindigkeit", "Ausdauer", "Kraft", "Flexibilität", "Balance"]])
        st.write("### Vertrag Details:")
        st.write(selected_player.iloc[0][["Vertrag", "Vertragsdetails", "Vertragsart"]])

else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")
