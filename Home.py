import streamlit as st
import os
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go
from agile_home_dashboard import fetch_data

# Define the directory for pages
st.set_page_config(
    page_title="Agile Daily Overview",
    # page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""  # Default value
st.session_state.api_key = st.text_input(
    "Enter your Octopus Energy API key:", st.session_state.api_key
)

api_key = st.session_state.api_key
st.session_state.df = fetch_data(api_key)

day_to_plot = st.selectbox("Select a day to plot:", ["Today", "Tomorrow"])
if day_to_plot == "Today":
    if st.session_state.df is None:
        st.write("No data available for today.")
    else:
        df_today = st.session_state.df[
            st.session_state.df["valid_from"].dt.date == datetime.now(pytz.UTC).date()
        ]
        fig_all = go.Figure()
        fig_all.add_trace(
            go.Bar(
                x=df_today["valid_from"],  # Time column
                y=df_today["value_inc_vat"],  # Price column
                marker=dict(color="#3d405b"),  # Optional: Set bar color
                name="Price [p/kWh]",  # Legend name
            )
        )

        fig_all.update_layout(
            plot_bgcolor="rgba(129, 178, 154, 0.2)",  # Set the plot area background to white
            font=dict(
                color="#3d405b",  # Set text color
                size=14,  # Optional: Adjust text size for better visibility
            ),
            title=dict(
                text="Agile Pricing",  # Add a title
                font=dict(color="#3d405b"),  # Set title text color
            ),
            xaxis=dict(
                title="Time",  # Label the x-axis
                title_font=dict(color="#3d405b"),  # X-axis title color
                tickfont=dict(color="#3d405b"),  # X-axis tick color
            ),
            yaxis=dict(
                title="Price [p/kWh]",  # Label the y-axis
                title_font=dict(color="#3d405b"),  # Y-axis title color
                tickfont=dict(color="#3d405b"),  # Y-axis tick color
            ),
        )
        st.plotly_chart(fig_all)
elif day_to_plot == "Tomorrow":
    tomorrow_date = (datetime.now(pytz.UTC) + pd.Timedelta(days=1)).date()
    df_tom = st.session_state.df[
        st.session_state.df["valid_from"].dt.date == tomorrow_date
    ]

    if df_tom.empty:
        st.write("No data available for tomorrow.")
    else:
        fig_all = go.Figure()
        fig_all.add_trace(
            go.Bar(
                x=df_tom["valid_from"],  # Time column
                y=df_tom["value_inc_vat"],  # Price column
                marker=dict(color="#3d405b"),  # Optional: Set bar color
                name="Price [p/kWh]",  # Legend name
            )
        )

        fig_all.update_layout(
            plot_bgcolor="rgba(129, 178, 154, 0.2)",  # Set the plot area background to white
            font=dict(
                color="#3d405b",  # Set text color
                size=14,  # Optional: Adjust text size for better visibility
            ),
            title=dict(
                text="Agile Pricing",  # Add a title
                font=dict(color="#3d405b"),  # Set title text color
            ),
            xaxis=dict(
                title="Time",  # Label the x-axis
                title_font=dict(color="#3d405b"),  # X-axis title color
                tickfont=dict(color="#3d405b"),  # X-axis tick color
            ),
            yaxis=dict(
                title="Price [p/kWh]",  # Label the y-axis
                title_font=dict(color="#3d405b"),  # Y-axis title color
                tickfont=dict(color="#3d405b"),  # Y-axis tick color
            ),
        )
        st.plotly_chart(fig_all)

# st.cache_data.clear()
# file_path = os.path.join(PAGES_DIR, '1_All_Data.py')


# st.write(pd.DataFrame(kettle_timing))
PAGES_DIR = "Pages"


# Function to load a module from a file
def load_module(module_name, filepath):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Get a list of pages
page_files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".py")]
pages = {
    f.replace(".py", "").replace("_", " ").title(): os.path.join(PAGES_DIR, f)
    for f in page_files
}

# main_page = '0 Trip Visualisation'
# load_module(main_page, pages[main_page]).app()
