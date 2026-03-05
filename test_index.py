import streamlit as st
import pandas as pd
df = pd.DataFrame({"Status": ["HOT", "COLD"]})

# Test combinations:
# 1. No styler, hide_index=True (Works)
# 2. Styler, hide_index=True (Fails? Streamlit ignores hide_index for Styler)
# 3. Styler.hide(axis="index"), hide_index=False (Does it break colors?)
# 4. Styler with map instead of apply?

def crm_style(val):
    if val == "HOT": return "background-color: red; color: white;"
    if val == "COLD": return "background-color: blue; color: white;"
    return ""

st.write("1. No styler, hide_index=True")
st.data_editor(df, hide_index=True, num_rows="dynamic")

st.write("2. Styler, hide_index=True")
st.data_editor(df.style.map(crm_style), hide_index=True, num_rows="dynamic")

st.write("3. Styler.hide(axis='index'), hide_index=True")
st.data_editor(df.style.map(crm_style).hide(axis="index"), hide_index=True, num_rows="dynamic")

# 4. Use apply
def style_row(row):
    return [crm_style(v) for v in row]

st.write("4. Styler.apply.hide, hide_index=True")
st.data_editor(df.style.apply(style_row, axis=1).hide(axis="index"), hide_index=True, num_rows="dynamic")

