import streamlit as st
from pathlib import Path
import pandas as pd
import math
import altair as alt
import plotly.graph_objects as go
import numpy as np


avarni_file_path = Path(__file__).parent / "data" / "Avarni_Flight-Distance-Emissions-Calculator.xlsm"
# template_data = pd.read_excel(avarni_file_path, sheet_name="Flight Calculation Sheet", header=2, index_col=1, usecols="A:E")
# template_csv = template_data.to_csv(encoding="utf-8")
sample_data = Path(__file__).parent / "data" / "sample data.csv"
sample_df = pd.read_csv(sample_data)
sample_csv = sample_df.to_csv(index=False, encoding="utf-8-sig")

template = pd.DataFrame(columns=["Origin", "Destination", "Class", "Num Passengers", "Return?"])
template_csv = template.to_csv(index=False, encoding="utf-8-sig")

from data import airports, emission_factors
def get_coordinate(origin, destination):
    try:
        airports_indexed = airports.set_index('Lookup')
        origin_row = airports_indexed.loc[[origin]] if origin in airports_indexed.index else None
        dest_row = airports_indexed.loc[[destination]] if destination in airports_indexed.index else None

        if origin_row is None or dest_row is None:
            st.error(f"Airport code not found: {origin} or {destination}")
            return None, None, None, None

        origin_lat = origin_row["Lat"].values[0]
        origin_lon = origin_row["Lon"].values[0]
        dest_lat = dest_row["Lat"].values[0]
        dest_lon = dest_row["Lon"].values[0]

        return origin_lat, origin_lon, dest_lat, dest_lon
    except Exception as e:
        st.error(f"Error getting coordinates for {origin} → {destination}: {e}")
        return None, None, None, None



def get_emission_factor(fly_class):
    emission_factors_indexed = emission_factors.set_index("Class")
    try:
        return emission_factors_indexed.at[fly_class, "Factor CO2e Value"]
    except KeyError:
        st.error(f"Invalid class selected: {fly_class}")
        return None


def calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon, is_return=False):
    R = 6371  # Radius of Earth in kilometers
    origin_lat, origin_lon, dest_lat, dest_lon = map(math.radians, [origin_lat, origin_lon, dest_lat, dest_lon])
    d_lat = dest_lat - origin_lat
    d_lon = dest_lon - origin_lon
    a = math.sin(d_lat / 2)**2 + math.cos(origin_lat) * math.cos(dest_lat) * math.sin(d_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance * 2 if is_return else distance


tab1, tab2 = st.tabs(["Upload Data", "Visualize Emissions"])

with tab1:
    st.header("Upload Data")
    st.caption("Use the template to fill in your data. The template is prefilled with some data already as an example.")
    st.download_button(
        label="Template",
        data=template_csv,
        file_name="business_travel_template.csv",
        type="primary",
        icon=":material/download:"
    )
    st.download_button("Sample data", sample_csv, file_name="sample data.csv", type="tertiary", icon=":material/download:")

    uploaded_files = st.file_uploader(
        label="Upload your business activity file here",
        type="csv",
        accept_multiple_files=True,
        help="You can upload multiple files. Make sure columns match the template. Extra columns for tags are fine."
    )

    if uploaded_files:
        with st.spinner("Please wait while the calculation is running"):
            st.session_state["files"] = uploaded_files
            dataframes = []
            for file in uploaded_files:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, encoding="utf-8")
                except UnicodeDecodeError:
                    file.seek(0)
                    df = pd.read_csv(file, encoding="latin1")  # fallback for Excel-exported files
                except Exception as e:
                    st.error(f"Could not read {file.name}: {e}")
                    continue  # skip this file
                
                df['filename'] = file.name  # optional: keep track of which file data came from
                dataframes.append(df)
                
                with st.expander(file.name, icon=":material/description:"):
                    st.dataframe(df)

            if dataframes:
                business_data = pd.concat(dataframes, ignore_index=True)

                distances = []
                emission_factors_list = []
                emissions = []

                for _, row in business_data.iterrows():
                    origin = row["Origin"]
                    destination = row["Destination"]
                    fly_class = row["Class"]
                    num_passengers = row.get("Num Passengers", 1)
                    is_return = (row.get("Return?") == "Return")

                    origin_lat, origin_lon, dest_lat, dest_lon = get_coordinate(origin, destination)
                    emission_factor = get_emission_factor(fly_class)

                    if all(val is not None and not pd.isna(val) for val in [origin_lat, origin_lon, dest_lat, dest_lon, emission_factor]):
                        dist = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon, is_return=is_return)
                        pkm = dist * num_passengers
                        emission = pkm * emission_factor

                        distances.append(dist)
                        emission_factors_list.append(emission_factor)
                        emissions.append(emission)
                    else:
                        distances.append(None)
                        emission_factors_list.append(None)
                        emissions.append(None)

                # ---- Merge additional airport + emissions metadata ----

                # Airports
                airports_origin = airports.rename(columns=lambda x: f"Origin_{x}")
                airports_dest = airports.rename(columns=lambda x: f"Destination_{x}")

                # Emission Factors
                ef_renamed = emission_factors.rename(columns=lambda x: f"EF_{x}")
                business_data = business_data.merge(
                    ef_renamed,
                    left_on="Class",
                    right_on="EF_Class",
                    how="left"
                )

                business_data['Distance_km'] = distances
                business_data["Passenger_distance_pkm"] = business_data['Distance_km'] * business_data['Num Passengers']
                business_data["Emissions"] = emissions
                business_data["Origin_Lat"] = business_data.apply(lambda row: get_coordinate(row["Origin"], row["Destination"])[0], axis=1)
                business_data["Origin_Lon"] = business_data.apply(lambda row: get_coordinate(row["Origin"], row["Destination"])[1], axis=1)
                business_data["Destination_Lat"] = business_data.apply(lambda row: get_coordinate(row["Origin"], row["Destination"])[2], axis=1)
                business_data["Destination_Lon"] = business_data.apply(lambda row: get_coordinate(row["Origin"], row["Destination"])[3], axis=1)


                st.subheader("Processed Data")
                st.caption(f"{len(business_data)} data rows loaded (excluding the header row)")
                st.dataframe(business_data)
                st.session_state["business_data"] = business_data




with tab2:
    st.header("Dashboard")

    if "business_data" in st.session_state and st.session_state["business_data"] is not None:
        df = st.session_state["business_data"]

        st.subheader("Summary Statistics")
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.1,0.1, 0.1])
            with col1:
                st.metric("Total Emissions (kg CO₂e)", f"{df['Emissions'].sum():,.2f}")
            with col2:
                st.metric("Total Distance (km)", f"{df['Distance_km'].sum():,.2f}")
            with col3:
                st.metric("Total Passenger Distance (pkm)", f"{df['Passenger_distance_pkm'].sum():,.2f}")


        col1, col2 = st.columns([0.1,0.1])    
        with col1:
            """#### Emissions by Class (Pie Chart)"""
            pie_data = df.groupby("Class")["Emissions"].sum().reset_index()
            pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Emissions", type="quantitative"),
                color=alt.Color(field="Class", type="nominal"),
                tooltip=["Class", "Emissions"]
                )
            st.altair_chart(pie_chart, use_container_width=True)
        
        
        with col2:
            """#### Emissions by Route (Top 10)"""
            df["Route"] = df["Origin"] + " ➝ " + df["Destination"]
            st.bar_chart(df.groupby("Route")["Emissions"].sum().sort_values(ascending=False).head(10))

        st.divider()
        
        """#### Custom Visualization"""
        # Extract columns
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

        col1, col2, col3 = st.columns([0.1,0.1,0.1])
        with col1:
            x_axis = st.selectbox("Select X-axis", options=categorical_columns + numeric_columns)
        with col2:
            y_axis = st.selectbox("Select Y-axis", options=numeric_columns)
        with col3:
            aggregation = st.selectbox("Aggregation Method", options=["sum", "mean", "median", "min", "max"])

        chart_type = st.radio("Chart Type", ["Bar", "Line", "Scatter"], horizontal=True)

        # Apply aggregation
        if x_axis in df.columns and y_axis in df.columns:
            agg_df = df.groupby(x_axis, dropna=False)[y_axis].agg(aggregation).reset_index()
        else:
            st.warning("Selected columns are not valid.")
            st.stop()

        # Build chart
        if chart_type == "Bar":
            chart = alt.Chart(agg_df).mark_bar().encode(
                x=alt.X(x_axis, type='ordinal' if x_axis in categorical_columns else 'quantitative'),
                y=alt.Y(y_axis, type='quantitative'),
                tooltip=[x_axis, y_axis]
            )
        elif chart_type == "Line":
            chart = alt.Chart(agg_df).mark_line().encode(
                x=alt.X(x_axis, type='ordinal' if x_axis in categorical_columns else 'quantitative'),
                y=alt.Y(y_axis, type='quantitative'),
                tooltip=[x_axis, y_axis]
            )
        else:  # Scatter (no aggregation makes more sense here)
            chart = alt.Chart(df).mark_circle(size=60).encode(
                x=alt.X(x_axis, type='quantitative' if x_axis in numeric_columns else 'ordinal'),
                y=alt.Y(y_axis, type='quantitative'),
                tooltip=[x_axis, y_axis]
            ).interactive()
        st.altair_chart(chart, use_container_width=True)

        st.divider()
        st.subheader("Emissions Trail Map by flight path")

        # Prepare cleaned data
        map_df = df.dropna(subset=["Origin_Lat", "Origin_Lon", "Destination_Lat", "Destination_Lon", "Emissions"]).copy()

        # Normalize emissions for line width scaling (optional)
        emissions_norm = (map_df["Emissions"] - map_df["Emissions"].min()) / (map_df["Emissions"].max() - map_df["Emissions"].min())
        map_df["Line_Width"] = emissions_norm * 5 + 1  # line width between 1–6

        # Initialize figure
        fig = go.Figure()

        # Add each flight route as a curved great circle line
        for _, row in map_df.iterrows():
            lat1, lon1 = row["Origin_Lat"], row["Origin_Lon"]
            lat2, lon2 = row["Destination_Lat"], row["Destination_Lon"]

            # interpolate lat/lon points along great circle
            num_points = 20
            lats = np.linspace(lat1, lat2, num_points)
            lons = np.linspace(lon1, lon2, num_points)

            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lon=lons,
                lat=lats,
                line=dict(width=row["Line_Width"], color="red"),
                hoverinfo="text",
                text=f"{row['Origin']} ➝ {row['Destination']}<br>{row['Emissions']:.2f} kg CO₂e",
                name=""
            ))

        # Add airport bubbles (optional)
        bubble_df = pd.concat([
            map_df[["Origin", "Origin_Lat", "Origin_Lon"]].rename(columns={"Origin": "Airport", "Origin_Lat": "Lat", "Origin_Lon": "Lon"}),
            map_df[["Destination", "Destination_Lat", "Destination_Lon"]].rename(columns={"Destination": "Airport", "Destination_Lat": "Lat", "Destination_Lon": "Lon"})
        ])
        bubble_df = bubble_df.drop_duplicates()

        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lat=bubble_df["Lat"],
            lon=bubble_df["Lon"],
            marker=dict(size=6, color="blue"),
            text=bubble_df["Airport"],
            hoverinfo="text",
            name="Airports"
        ))

        # Layout with modern basemap
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=1.3,
                center={"lat": map_df["Origin_Lat"].mean(), "lon": map_df["Origin_Lon"].mean()},
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=600,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No data available. Please upload files in the **Upload Data** tab first.")

    
