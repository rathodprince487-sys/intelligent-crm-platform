import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD", "WARM", "HOT", "COLD", "WARM"]})
# We use index 5, 6, 7...
df.index = [5, 6, 7, 8, 9, 10]

def style_row(row):
    return ["background-color: lightgreen;"]

styled_df = df.style.apply(style_row, axis=1)

# Will this render the index?
st.data_editor(styled_df, hide_index=True)
