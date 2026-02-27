import streamlit as st
import pandas as pd

st.write("Dynamic")
df = pd.DataFrame({"A": [1,2], "B": [3,4]})
st.data_editor(df, num_rows="dynamic", hide_index=True)

st.write("Fixed")
st.data_editor(df, num_rows="fixed", hide_index=True)
