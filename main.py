import streamlit as st
from ui.layout import set_page_config
from pathlib import Path
import pandas as pd

set_page_config()

pages =[
    st.Page("about.py", title="About", icon=":material/info:"),
    st.Page("calculator.py", title="Calculation", icon=":material/calculate:"),
    st.Page("data.py", title="Background data", icon=":material/database:")
]

pg = st.navigation(pages)
pg.run()

avarni_file_path = Path(__file__).parent / "data" / "Avarni_Flight-Distance-Emissions-Calculator.xlsm"
st.session_state.airports = pd.read_excel(avarni_file_path, sheet_name="Airports")
st.session_state.emission_factors = pd.read_excel(avarni_file_path, sheet_name="Emission Factors", header=2)
