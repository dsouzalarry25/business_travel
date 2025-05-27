import streamlit as st
from ui.layout import set_page_config

set_page_config()

pages =[
    st.Page("about.py", title="About", icon=":material/info:"),
    st.Page("calculator.py", title="Calculation", icon=":material/calculate:"),
    st.Page("data.py", title="Background data", icon=":material/database:")
]

pg = st.navigation(pages)
pg.run()