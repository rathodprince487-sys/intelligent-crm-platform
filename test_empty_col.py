import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD"], "Priority": ["WARM", "HOT"]})
st.data_editor(df, num_rows="dynamic")
