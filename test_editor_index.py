import streamlit as st
import pandas as pd
df = pd.DataFrame({"A": [1, 2]}, index=[10, 20])
styled = df.style.hide(axis="index")
edited = st.data_editor(styled, key="tst")
st.write(edited.index.tolist())
