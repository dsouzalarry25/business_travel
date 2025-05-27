import streamlit as st

def table(data, title="Table title", subtitle="Table subtitle"):
    st.subheader(title)
    st.write(subtitle)
    st.caption(f"This table contains {len(data.iloc[:,0])} rows")
    st.dataframe(data)
