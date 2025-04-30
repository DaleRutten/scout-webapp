import streamlit as st
import pandas as pd

st.title("Genie Scout Web-App")

@st.cache_data
def load_data():
    return pd.read_excel("Spielerdaten_Export.xlsx")

df = load_data()

position = st.selectbox("Position auswählen", df["Position"].unique())
min_pa = st.slider("Minimales Potential (PA)", min_value=0, max_value=200, value=100)

filtered_df = df[(df["Position"] == position) & (df["PA"] >= min_pa)]

st.dataframe(filtered_df)
