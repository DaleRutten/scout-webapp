import pandas as pd
import streamlit as st

# Titel der App
st.title("Genie Scout Web-App")

# Laden der Daten
@st.cache
def load_data():
    return pd.read_excel("Spielerdaten_Export.xlsx")

# Daten laden
df = load_data()

# Sidebar Filter
st.sidebar.header("Filtern nach Attributen")
min_age = st.sidebar.slider("Minimales Alter", 16, 40, 18)
max_age = st.sidebar.slider("Maximales Alter", 18, 40, 30)
min_value = st.sidebar.number_input("Minimale Marktwert (€)", 0, int(df['Wert'].max()), 1000000)
max_value = st.sidebar.number_input("Maximale Marktwert (€)", 1000000, int(df['Wert'].max()), 50000000)
min_potential = st.sidebar.slider("Minimales Potential", 0, 200, 130)
max_potential = st.sidebar.slider("Maximales Potential", 0, 200, 180)

# Positionen-Filter
position_filter = st.sidebar.multiselect("Positionen wählen", df["Position"].unique())

# Nationalität-Filter
nation_filter = st.sidebar.multiselect("Nationalität", df["Nation"].unique())

# EU-Bürger Filter
eu_citizens = st.sidebar.checkbox("Nur EU-Bürger", False)

# Daten filtern
filtered_df = df[
    (df["Alter"] >= min_age) & 
    (df["Alter"] <= max_age) &
    (df["Wert"] >= min_value) & 
    (df["Wert"] <= max_value) &
    (df["Potential"] >= min_potential) & 
    (df["Potential"] <= max_potential)
]

if position_filter:
    filtered_df = filtered_df[filtered_df["Position"].isin(position_filter)]

if nation_filter:
    filtered_df = filtered_df[filtered_df["Nation"].isin(nation_filter)]

if eu_citizens:
    # Hier wird angenommen, dass es eine Spalte 'EU' gibt, die angibt, ob ein Spieler EU-Bürger ist
    filtered_df = filtered_df[filtered_df['EU'] == 1]

# Daten anzeigen
st.write(f"Gefundene Spieler: {len(filtered_df)}")
st.dataframe(filtered_df)

# Erweiterte Filterung: Vertragsdetails, Reputation etc.
st.sidebar.header("Vertragsdetails")
contract_status = st.sidebar.selectbox("Vertragsstatus", ["Verlassen aufgrund des Bosman-Urts", "Aktiv", "Auslaufend"])
filtered_df = filtered_df[filtered_df["Vertrag"] == contract_status]

# Zusatzoptionen: Spieler suchen, die die Bosman-Regel erfüllen
bosman_rule = st.sidebar.checkbox("Nur Bosman-Spieler (Verlassen aufgrund des Bosman-Urts)", False)
if bosman_rule:
    filtered_df = filtered_df[filtered_df["Vertrag"] == "Verlässt aufgrund des Bosman-Urts"]

# Spielerposition
st.sidebar.header("Spieler-Positionen")
position_1 = st.sidebar.selectbox("Position 1", df["Position"].unique())
position_2 = st.sidebar.selectbox("Position 2", df["Position"].unique())
filtered_df = filtered_df[filtered_df["Position"].isin([position_1, position_2])]

# Spieler sortieren
st.sidebar.header("Sortieren nach:")
sort_by = st.sidebar.selectbox("Sortiere nach", ["Wert", "Potential", "Alter", "Wert pro Jahr", "Aktuelle Fähigkeit"])
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
    st.write(selected_player.iloc[0][["Name", "Nation", "Position", "Wert", "Vertrag", "Aktuelle Fähigkeit", "Potential"]])
    st.write("### Technische Attribute:")
    st.write(selected_player.iloc[0][["Flanken", "Abschluss", "Ballkontrolle", "Pässe", "Tackling"]])
    st.write("### Mentale Attribute:")
    st.write(selected_player.iloc[0][["Aggressivität", "Konzentration", "Nervenstärke", "Teamwork", "Flair"]])
    st.write("### Physische Attribute:")
    st.write(selected_player.iloc[0][["Sprintgeschwindigkeit", "Ausdauer", "Kraft", "Flexibilität", "Balance"]])
    st.write("### Vertrag Details:")
    st.write(selected_player.iloc[0][["Vertrag", "Vertragsdetails", "Vertragsart"]])

# Zusätzliche Grafiken oder Darstellungen könnten hier hinzugefügt werden.
