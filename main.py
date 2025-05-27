import streamlit as st

pages =[
    st.Page("about.py", title="About"),
    st.Page("calculator.py", title="Calculator"),
    st.Page("data.py", title="Background data")
]

pg = st.navigation(pages)
pg.run()