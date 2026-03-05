import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD"]})
df.index = [5, 6]

styled_df = df.style.apply(lambda x: ["" for i in x], axis=1)

st.data_editor(styled_df, num_rows="dynamic", hide_index=True, column_config={"_index": None})
