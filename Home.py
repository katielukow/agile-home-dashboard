import os
from datetime import datetime, time, timedelta

import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st
import toml

from agile_home_dashboard import fetch_data, get_current_cost, load_css


# Load the TOML file
def load_config(file_path=".streamlit/config.toml"):
    return toml.load(file_path)


st.set_page_config(
    page_title="Agile Daily Overview",
    # page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded",
)

config = load_config()
colors = config["theme"]
st.session_state.bg_color = colors["backgroundColor"]
st.session_state.font = colors["textColor"]
st.session_state.marker = "#7DBDF5"
st.session_state.textBoxColor = "#2A69A1"
st.session_state.textColor = "#B5146A"
st.session_state.primary_color = colors["primaryColor"]

load_css()

# Website to find the correct url for different tarrifs
# https://energy-stats.uk/octopus-tracker-southern-england/
url = "https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-H/standard-unit-rates/"
url_tracker_e = "https://api.octopus.energy/v1/products/SILVER-24-10-01/electricity-tariffs/E-1R-SILVER-24-10-01-H/standard-unit-rates/"
url_tracker_g = "https://api.octopus.energy/v1/products/SILVER-24-10-01/gas-tariffs/G-1R-SILVER-24-10-01-H/standard-unit-rates/"


def plot_data():
    col1, col2 = st.columns([0.15, 0.85], vertical_alignment="center")

    with col1:
        day_to_plot = st.radio("Select day:", options=["Today", "Tomorrow"], index=0)
    with col2:
        if day_to_plot == "Today":
            if st.session_state.df is None:
                st.write("No data available for today.")
            else:
                df_today = st.session_state.df[
                    st.session_state.df["valid_from"].dt.date
                    == datetime.now(pytz.UTC).date()
                ]
                fig_all = go.Figure()
                fig_all.add_trace(
                    go.Bar(
                        x=df_today["valid_from"],  # Time column
                        y=df_today["value_inc_vat"],  # Price column
                        marker=dict(
                            color=st.session_state.marker
                        ),  # Optional: Set bar color
                        name="Price [p/kWh]",  # Legend name
                    )
                )

                fig_all.update_layout(
                    plot_bgcolor=st.session_state.bg_color,  # Set the plot area background to white
                    font=dict(
                        color=st.session_state.font,  # Set text color
                        size=14,  # Optional: Adjust text size for better visibility
                    ),
                    title=dict(
                        text="Agile Pricing",  # Add a title
                        font=dict(color=st.session_state.font),  # Set title text color
                    ),
                    xaxis=dict(
                        title="Time",  # Label the x-axis
                        title_font=dict(
                            color=st.session_state.font
                        ),  # X-axis title color
                        tickfont=dict(color=st.session_state.font),  # X-axis tick color
                    ),
                    yaxis=dict(
                        title="Price [p/kWh]",  # Label the y-axis
                        title_font=dict(
                            color=st.session_state.font
                        ),  # Y-axis title color
                        tickfont=dict(color=st.session_state.font),  # Y-axis tick color
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
                        marker=dict(
                            color=st.session_state.marker
                        ),  # Optional: Set bar color
                        name="Price [p/kWh]",  # Legend name
                    )
                )

                fig_all.update_layout(
                    plot_bgcolor=st.session_state.bg_color,  # Set the plot area background to white
                    font=dict(
                        color=st.session_state.font,  # Set text color
                        size=14,  # Optional: Adjust text size for better visibility
                    ),
                    title=dict(
                        text="Agile Pricing",  # Add a title
                        font=dict(color=st.session_state.font),  # Set title text color
                    ),
                    xaxis=dict(
                        title="Time",  # Label the x-axis
                        title_font=dict(
                            color=st.session_state.font
                        ),  # X-axis title color
                        tickfont=dict(color=st.session_state.font),  # X-axis tick color
                    ),
                    yaxis=dict(
                        title="Price [p/kWh]",  # Label the y-axis
                        title_font=dict(
                            color=st.session_state.font
                        ),  # Y-axis title color
                        tickfont=dict(color=st.session_state.font),  # Y-axis tick color
                    ),
                )
                st.plotly_chart(fig_all)


def get_optimal_coffee_time(df, current_time):
    # Get the date for tomorrow if it is after 10am, otherwise use today
    coffee_day = (
        current_time.date() + timedelta(days=1)
        if current_time.hour > 10
        else current_time.date()
    )

    target_start = datetime.combine(coffee_day, time(7, 0))
    target_end = datetime.combine(coffee_day, time(10, 0))

    if df["valid_from"].dt.tz is not None:  # If DataFrame timestamps have timezone info
        target_start = target_start.replace(tzinfo=df["valid_from"].dt.tz)
        target_end = target_end.replace(tzinfo=df["valid_from"].dt.tz)

    df_coffee = df[(df["valid_to"] <= target_end) & (df["valid_from"] > target_start)]

    if df_coffee.empty:
        return None
    else:
        return (
            df_coffee.loc[df_coffee["value_inc_vat"].idxmin()]["valid_from"]
            if df_coffee is not None
            else None
        )


def display_current_costs(current_time, coffee_time):
    cost_now, cost_next, current_row, next_row = get_current_cost(
        st.session_state.df, current_time
    )
    tracker_now, tracker_next, current_row_e, next_row_e = get_current_cost(
        st.session_state.df_tracker_e, current_time
    )

    col1, col2, col3 = st.columns(3, gap="small")
    w = "95%"
    h = "120px"
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <div style="{st.session_state.col_format};
                    height: {h};
                    width: {w};">
                    <strong>Current Energy Cost</strong><br>
                    <span style="font-size: 1.5em;">{cost_now:.4f} p/kWh</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if coffee_time is not None:
        with col2:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>The best time to make coffee is</strong><br>
                        <span style="font-size: 1.5em;">{coffee_time.strftime("%H:%M")}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        with col2:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>The best time to make coffee is:</strong><br>
                        <span style="font-size: 1.5em;">Data not available yet</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if tracker_next is not None:
        tracker_delta = (tracker_next - tracker_now) / tracker_now * 100
        symb = "&uarr;" if tracker_delta > 0 else "&darr;"
        with col3:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>Tomorrow's Tracker Trend</strong><br>
                        <span style="font-size: 1.5em;">{symb} {tracker_delta:.1f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        with col3:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>Tomorrow's Tracker Trend</strong><br>
                        <span style="font-size: 1.5em;">Data not available yet</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Function to load a module from a file
def load_module(module_name, filepath):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""  # Default value

    st.session_state.api_key = st.text_input(
        "Enter your Octopus Energy API key:", st.session_state.api_key
    )

    api_key = st.session_state.api_key
    st.session_state.df = fetch_data(api_key, url)
    st.session_state.df_tracker_e = fetch_data(api_key, url_tracker_e)

    st.markdown(" ")  # Add some space between the input field and the plot
    coffee_time = get_optimal_coffee_time(st.session_state.df, datetime.now(pytz.UTC))
    display_current_costs(datetime.now(pytz.UTC), coffee_time)

    plot_data()


# Run the application
if __name__ == "__main__":
    main()

# Get a list of pages
PAGES_DIR = "pages"
page_files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".py")]
pages = {
    f.replace(".py", "").replace("_", " ").title(): os.path.join(PAGES_DIR, f)
    for f in page_files
}

# main_page = '0 Trip Visualisation'
# load_module(main_page, pages[main_page]).app()
