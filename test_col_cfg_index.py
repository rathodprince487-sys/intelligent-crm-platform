import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD"]})
df.index = [5, 6]
styled_df = df.style.apply(lambda x: ["" for i in x], axis=1)

col_cfg = {
    "_index": None,
    "Status": st.column_config.TextColumn("Status")
}

st.data_editor(styled_df, hide_index=False, column_config=col_cfg)
