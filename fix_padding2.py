import re

with open('app.py', 'r') as f:
    text = f.read()

css_inject = '''
        /* Compress whitespace at the top of the app globally */
        .block-container {
            padding-top: 1rem !important;
            margin-top: -10px !important;
        }
        /* Compress the Streamlit header space */
        header[data-testid="stHeader"] {
            height: 2.5rem !important;
            min-height: 2.5rem !important;
        }
'''

# Add css injection into the first st.markdown(""" 
if '/* Compress whitespace at the top of the app globally */' not in text:
    text = text.replace('st.markdown("""', 'st.markdown("""\n' + css_inject, 1)

with open('app.py', 'w') as f:
    f.write(text)

print('Injected!')
