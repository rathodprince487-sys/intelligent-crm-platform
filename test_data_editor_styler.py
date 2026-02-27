import streamlit as st
import pandas as pd

df = pd.DataFrame({"Status": ["HOT", "COLD"]})

# 1. Styler with apply and hide index
styled_df = df.style.apply(lambda x: ["background-color: red" if v == "HOT" else "background-color: blue" for v in x], axis=1)

# Streamlit documentation says if you want to hide index, use `hide_index=True`
edited = st.data_editor(styled_df, hide_index=True, key="ed_1", use_container_width=True)

# 2. What if we use Styler.hide?
styled_df_2 = df.style.apply(lambda x: ["background-color: red" if v == "HOT" else "background-color: blue" for v in x], axis=1).hide(axis="index")
edited2 = st.data_editor(styled_df_2, key="ed_2", use_container_width=True)

st.write("Does 2 render properly?")
