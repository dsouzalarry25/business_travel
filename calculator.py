import streamlit as st
from pathlib import Path
import pandas as pd
from ui.layout import set_page_config
import math
from data import airports
from data import emission_factors
import altair as alt

avarni_file_path = Path(__file__).parent / "data" / "Avarni_Flight-Distance-Emissions-Calculator.xlsm"
template_data = pd.read_excel(avarni_file_path, sheet_name="Flight Calculation Sheet", header=2, index_col=1, usecols="A:E")
template_csv = template_data.to_csv()

def get_coordinate(origin, destination):
    airports_indexed = airports.set_index('Lookup')
    try:
        origin_lat = airports_indexed.at[origin, 'Lat']
        origin_lon = airports_indexed.at[origin, 'Lon']
        dest_lat = airports_indexed.at[destination, 'Lat']
        dest_lon = airports_indexed.at[destination, 'Lon']
    except KeyError:
        st.error(f"Airport code not found: {origin} or {destination}")
        return None, None, None, None
    return origin_lat, origin_lon, dest_lat, dest_lon

def get_emission_factor(fly_class):
    emission_factors_indexed = emission_factors.set_index("Class")
    try:
        emission_factor = emission_factors_indexed.at[fly_class, "Factor CO2e Value"]
    except KeyError:
        st.error(f"Invalid class selected {fly_class}")
        return None
    return emission_factor

def calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon, is_return=False):
    """
    Calculate the great-circle distance between two points on the Earth
    specified by latitude and longitude using the Haversine formula.

    Parameters:
        origin_lat (float): Latitude of the origin point in degrees
        origin_lon (float): Longitude of the origin point in degrees
        dest_lat (float): Latitude of the destination point in degrees
        dest_lon (float): Longitude of the destination point in degrees
        is_return (bool): If True, multiply the distance by 2 (return trip)

    Returns:
        float: Distance between the two points in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    # Convert degrees to radians
    origin_lat = math.radians(origin_lat)
    origin_lon = math.radians(origin_lon)
    dest_lat = math.radians(dest_lat)
    dest_lon = math.radians(dest_lon)

    # Differences
    d_lat = dest_lat - origin_lat
    d_lon = dest_lon - origin_lon

    # Haversine formula
    a = math.sin(d_lat / 2)**2 + math.cos(origin_lat) * math.cos(dest_lat) * math.sin(d_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    if is_return:
        distance *= 2

    return distance




tab1, tab2 = st.tabs(["Upload Data", "Visualize Emissions"])

with tab1:
    st.header("Upload Data")
    st.caption("Use the template to fill in your data. The template is prefilled with some data already as an example.")
    st.download_button(label="Download template", data=template_csv, file_name="business_travel_template.csv", type="primary", icon=":material/download:")


    uploaded_files = st.file_uploader(
        label="Upload your business activity file here. Make sure you fill the **Origin** and **Destination** columns with values that are valid. Use the values given in the '**Lookup**' column in the '**Background data** > **Airports**' page",
        type="csv",
        accept_multiple_files=True,
        help="You can upload multiple files, and the app will merge them by aligning columns with the same names. Please ensure your files use the exact column names as in the template. It's perfectly fine to include additional columns with tagging information to enable deeper analysis of your emissions later on."
    )


    if uploaded_files:
        if len(uploaded_files) > 1:
            business_data = []
            for file in uploaded_files:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, encoding="utf-8")
                    df['filename'] = file.name  # Add filename column here
                    business_data.append(df)
                    with st.expander(file.name, icon=":material/description:"):
                        st.dataframe(df)  # Show the single dataframe for this file here
                except Exception as e:
                    st.error(f"Error occurred when trying to read the CSV file '{file.name}': {e}")

            if business_data:
                business_data = pd.concat(business_data, ignore_index=True)
                with st.expander("**Merged data**", icon=":material/database_upload:"):
                    st.dataframe(business_data)

        else:
            # Single file uploaded, read the first file in the list
            file = uploaded_files[0]
            try:
                file.seek(0)
                business_data = pd.read_csv(file, encoding="utf-8")
                with st.expander(file.name, icon=":material/database_upload:"):
                    st.dataframe(business_data)
            except Exception as e:
                st.error(f"Error occurred when trying to read the CSV file '{file.name}': {e}")


        distances = []
        emission_factors_list = []
        emissions = []

        for _, row in business_data.iterrows():
            origin = row["Origin"]
            destination = row["Destination"]
            fly_class = row["Class"]
            
            origin_lat, origin_lon, dest_lat, dest_lon = get_coordinate(origin, destination)
            emission_factor = get_emission_factor(fly_class)
            
            is_return = (row.get("Return?") == "Return")

            dist = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon, is_return=is_return)
            pkm = dist * row["Num Passengers"]
            emission = pkm * emission_factor if emission_factor is not None else None

            distances.append(dist)
            emission_factors_list.append(emission_factor)


        business_data['Distance_km'] = distances
        business_data["Passenger_distance_pkm"] = business_data['Distance_km'] * business_data['Num Passengers']
        business_data["Emission factor"] = emission_factors_list
        business_data["Emissions"] = business_data['Passenger_distance_pkm'] * business_data['Emission factor']


        st.write("Business data with distances:")
        st.dataframe(business_data)
        st.session_state["business_data"] = business_data


with tab2:
    st.header("Dashboard")

    if "business_data" in st.session_state:
        df = st.session_state["business_data"]

        st.subheader("Summary Statistics")
        st.metric("Total Emissions (kg CO₂e)", f"{df['Emissions'].sum():,.2f}")
        st.metric("Total Distance (km)", f"{df['Distance_km'].sum():,.2f}")

        st.subheader("Emissions by Travel Class (Bar Chart)")
        st.bar_chart(df.groupby("Class")["Emissions"].sum())

        st.subheader("Emissions by Route (Top 10)")
        df["Route"] = df["Origin"] + " ➝ " + df["Destination"]
        st.bar_chart(df.groupby("Route")["Emissions"].sum().sort_values(ascending=False).head(10))

        st.subheader("Emissions by Class (Pie Chart)")
        pie_data = df.groupby("Class")["Emissions"].sum().reset_index()
        pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=40).encode(
            theta=alt.Theta(field="Emissions", type="quantitative"),
            color=alt.Color(field="Class", type="nominal"),
            tooltip=["Class", "Emissions"]
        )
        st.altair_chart(pie_chart, use_container_width=True)

        st.subheader("Custom Visualization")

        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

        x_axis = st.selectbox("Select X-axis", options=categorical_columns + numeric_columns)
        y_axis = st.selectbox("Select Y-axis", options=numeric_columns)

        chart_type = st.radio("Chart Type", ["Bar", "Line", "Scatter"])

        if chart_type == "Bar":
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X(x_axis, type='ordinal' if x_axis in categorical_columns else 'quantitative'),
                y=alt.Y(y_axis, type='quantitative'),
                tooltip=[x_axis, y_axis]
            )
        elif chart_type == "Line":
            chart = alt.Chart(df).mark_line().encode(
                x=alt.X(x_axis, type='ordinal' if x_axis in categorical_columns else 'quantitative'),
                y=alt.Y(y_axis, type='quantitative'),
                tooltip=[x_axis, y_axis]
            )
        else:  # Scatter
            chart = alt.Chart(df).mark_circle(size=60).encode(
                x=alt.X(x_axis, type='quantitative' if x_axis in numeric_columns else 'ordinal'),
                y=alt.Y(y_axis, type='quantitative'),
                tooltip=[x_axis, y_axis]
            ).interactive()

        st.altair_chart(chart, use_container_width=True)

    else:
        st.warning("No data available. Please upload files in the Calculator tab first.")

