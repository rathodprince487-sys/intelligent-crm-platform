import streamlit as st
import pandas as pd

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({"Notes": ["AAA", "BBB"]})

def color_row(row):
    return ["background-color: yellow" for _ in row]

st.write("With .hide(axis='index')")
styled = st.session_state.df.style.apply(color_row, axis=1).hide(axis="index")

edited = st.data_editor(styled, key="editor_styled", num_rows="dynamic")
st.write("Changes:", edited)
