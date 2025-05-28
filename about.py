import streamlit as st

st.title("Scope 3 Business Travel Emissions Calculator")


st.write("""
#### This application enables organizations to efficiently estimate the greenhouse gas emissions associated with business air travel.

---
             
The original emissions calculation methodology through an excel based tool was publicly shared by **Misha**, and forms the core logic for this tool. Emissions are calculated based on great-circle distances between airports and travel class-specific emission factors from DEFRA — the UK Government’s 2024 conversion factors, a globally recognized standard.
         
**Original Methodology Contributor**: [Misha Cajic](https://www.linkedin.com/in/misha-cajic/) - [Avarni](https://www.avarni.co/)
         
---
         
This streamlit implementation by **Larry** builds on that foundation, expanding the user interface and adding features like multi-file upload and emissions visualization.
         
**Webapp Developer**: [Larry Dsouza](https://larry-dsouza.framer.website/)
        """)

col1, col2 = st.columns([0.1, 1])
with col1:
    st.badge(
        "Disclaimer:",
        color="red"
    )
with col2: 
    st.caption("This Streamlit app is a conversion of the original Excel-based tool. While I developed the app interface and logic, I have not independently verified the emission factors or calculation methodology. Please consult the original tool for reference. The app has been tested to ensure that results match those produced by the original Excel tool.")

with st.popover("View Larry's contributions"):
    st.markdown("""
- Integrated flight and emissions data from the original Excel file, including airport coordinates and class-based emission factors.
- Built the upload feature to accept multiple CSVs, while also providing clean templates and sample files to help users get started quickly.
- The data pipeline automatically processes user uploads and calculates emissions for each route.
- Rewrote the core logic to calculate flight distances using the Haversine formula (great-circle distance).
- Created an interactive dashboard that shows:
  - Summary metrics like total emissions, distance, and passenger kilometers.
  - Emissions by travel class and top routes.
  - Custom charts where users can explore their data with different axes and aggregation types.
- Built a global flight path map:
  - Flight lines are color-coded.
  - Line thickness represents emissions magnitude.
  - Hover text shows flight route and emissions detail.
- Used session state to manage data across tabs, ensuring a smooth user experience.
- The app is structured around two main tabs: one for uploading data and one for visualizing the results.
- Added safeguards and error messages to make sure the app handles messy or inconsistent data gracefully.
---
This project shows how a spreadsheet tool can evolve into a more dynamic, transparent, and shareable web application using modern Python tools like Streamlit, Plotly, and Altair.
""")
    
st.divider()

"""#### How to Use the Business Travel Emissions Calculator"""

with st.expander("View tool instructions"):
    st.markdown("""
    

    ##### 1. **Prepare Your Flight Data**  
    Export your business travel data from your expense or travel booking system. Make sure each row includes at least:
    - ***Origin*** and ***Destination*** (IATA code like `SYD` or city name like `Sydney`)
        - Use the accepted values available in the **Lookup** column given in this app under **Background data** > **Airports** table
    - ***Class*** (`Economy`, `Business`, etc.)
        - Use the accepted values available in the **Class** column given in this app under **Background data** > **Emission Factors** table
        - If travel class is unknown, enter `Average`
    - ***Num_Passengers*** per booking
        - For individual trips, enter `1` under **Num Passengers**
    - ***Return_trip*** (optional)
        - If the booking includes a return flight, add the value `Return` for that row. If omitted, the app assumes one-way travel.

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
