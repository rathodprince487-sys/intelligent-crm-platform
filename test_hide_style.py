import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD"]})

def crm_style(val, col):
    if val == "HOT": return "background-color: red !important; color: white !important;"
    if val == "COLD": return "background-color: blue; color: white;"
    return ""

styled_df = df.style.apply(lambda x: [crm_style(x[c], c) for c in x.index], axis=1).hide(axis="index")

st.data_editor(styled_df)
