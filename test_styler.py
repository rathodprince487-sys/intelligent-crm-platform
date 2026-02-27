import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD"]})

# Using styled with hide index
def color_status(val):
    return "background-color: red" if val == "HOT" else "background-color: blue"

# 1. Hide on styler
styled = df.style.map(color_status).hide(axis="index")
edited = st.data_editor(styled, key="editor_1", num_rows="dynamic")
st.write(edited)
