import streamlit as st
from pathlib import Path
import pandas as pd
from ui.layout import set_page_config
from utils.tables import table

set_page_config()

avarni_file_path = Path(__file__).parent / "data" / "Avarni_Flight-Distance-Emissions-Calculator.xlsm"

tab1, tab2 = st.tabs(["Airports", "Emission Factors"])

with tab1:
    airports = pd.read_excel(avarni_file_path, sheet_name="Airports")
    table(
        data=airports,
        title="Airports",
        subtitle="Details about Airport IATA code, Name, Country and Geographic coordinates. Use the '**Lookup**' column to fill the origin and destination columns in the template.")
    
with tab2:
    emission_factors = pd.read_excel(avarni_file_path, sheet_name="Emission Factors", header=2)
    table(
        data=emission_factors,
        title="Emission Factors",
        subtitle="Source details of the emission factors used in the app")
    






