import streamlit as st
from ui.layout import set_page_config

set_page_config()

st.title("🛩️ Business Travel Emissions Calculator")

st.caption("This application enables organizations to efficiently estimate the greenhouse gas emissions associated with business air travel.")
st.write("""
           The original emissions calculation methodology through an excel based tool was publicly shared by **Misha**, and forms the core logic for this tool. Emissions are calculated based on great-circle distances between airports and travel class-specific emission factors from DEFRA — the UK Government’s 2024 conversion factors, a globally recognized standard. The methodology aligns with Scope 3, Category 6 (Business Travel) reporting requirements under frameworks like AASB S2, IFRS S2, California SB 253, and the EU CSRD.
         
**Original Methodology Contributor**: [Misha Cajic](https://www.linkedin.com/in/misha-cajic/)  
         
---
         
This streamlit implementation by **Larry** builds on that foundation, expanding the user interface and adding features like multi-file upload and emissions visualization.
         
**Webapp Developer**: [Larry Dsouza](https://larry-dsouza.framer.website/)
           
--- 
        """)

"""#### How to Use the Business Travel Emissions Calculator"""

with st.expander("View tool instructions"):
    st.markdown("""
    

    ##### 1. **Prepare Your Flight Data**  
    Export your business travel data from your expense or travel booking system. Make sure each row includes at least:
    - ***Origin*** and ***Destination*** (IATA code like `SYD` or city name like `Sydney`)
        - Use the accepted values available in the **Lookup** column given in this app under **Background data** > **Airports** table
    - ***Travel class*** (`Economy`, `Business`, etc.)
        - Use the accepted values available in the **Class** column given in this app under **Background data** > **Emission Factors** table
        - If travel class is unknown, enter `Average`
    - ***Number of passengers*** per booking
        - For individual trips, enter `1` under **Num Passengers**
    - ***Return trip?*** (optional)
        - If the booking includes a return flight, add a `Return?` column with the value `Return` for that row. If omitted, the app assumes one-way travel.

    ##### 2. **Upload and Calculate**  
    Drag and drop your cleaned file into the app under **Calculation** > **Upload Data** tab. The calculator will:
    - Match origin and destination to known airport locations
    - Compute great-circle distances
    - Apply DEFRA 2024 emission factors by class and distance
    - Output emissions in kilograms of CO₂e

    ##### 3. **Explore Emissions Results**  
    Use the interactive dashboard to:
    - View emissions by class and top routes
    - Filter, sort, and visualize data
    - Export results if needed
    """)
