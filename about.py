import streamlit as st
from ui.layout import set_page_config

set_page_config()

st.title("Business Travel Emissions")

st.caption("""
           This app is designed to help organisations quickly calculate the emissions associated with business flights.

It takes an origin and a destination as inputs for each flight, as well as the class travelled and number of passengers, and automatically calculates the distance in kilometers between the origin and destination. The class is then used to determine the appropriate emissions factor to use from the 2024 DEFRA conversion factor database published by the UK Government, the de-facto standard database used worldwide for flight emission calculations. You can view the source of the emission factors by following the Factor Source Links in the Emission Factors tab under Data page.

The calculations in this workbook can be used to fulfil the reporting requirements for Scope 3 Category 6: Business Travel, under many reporting frameworks worldwide (AASB S2, IFRS S2, CA SB 253, CSRD).
""")

"""
**Data provider**: Avarni, Sydney, Australia

**App developer**: Larry Dsouza, Germany
"""