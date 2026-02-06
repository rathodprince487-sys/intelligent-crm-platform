import sys
print("Sys Path:")
for p in sys.path:
    print(p)
try:
    import streamlit_keyup
    print("SUCCESS: streamlit_keyup imported")
except ImportError as e:
    print(f"FAILURE: {e}")
