import streamlit as st

pages =[
    st.Page("about.py", title="About", icon=":material/info:"),
    st.Page("calculator.py", title="Calculation", icon=":material/calculate:"),
    st.Page("data.py", title="Background data", icon=":material/database:")
]

pg = st.navigation(pages)
pg.run()