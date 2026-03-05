import streamlit as st
import pandas as pd

df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
styled = df.style.apply(lambda x: ["", ""], axis=1).hide(axis="index")

st.data_editor(styled, num_rows="dynamic", hide_index=True)
