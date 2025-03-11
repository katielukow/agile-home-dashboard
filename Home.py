import os
from datetime import datetime, time, timedelta

import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st
import toml

from agile_home_dashboard import fetch_data, get_current_cost, load_css
from utils import cp, kappa, kettle_energy


# Load the TOML file
def load_config(file_path=".streamlit/config.toml"):
    return toml.load(file_path)


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
# is: https://energy-stats.uk/octopus-tracker-southern-england/
url = "https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-H/standard-unit-rates/"
url_tracker_e = "https://api.octopus.energy/v1/products/SILVER-24-10-01/electricity-tariffs/E-1R-SILVER-24-10-01-H/standard-unit-rates/"
url_tracker_g = "https://api.octopus.energy/v1/products/SILVER-24-10-01/gas-tariffs/G-1R-SILVER-24-10-01-H/standard-unit-rates/"

st.session_state.df = None


def get_color(value):
    if value < 0:
        return "#e7e1ff"

    thresholds = [5, 7, 10, 15, 20, 25, 30]
    colors = [
        "#fdbbc1",
        "#ff9a9f",
        "#666c90",
        "#aa7515",
        "#f7c8a2",
        "#1a2ee8",
        "#332d58",
        "#1e1f57",
    ]

    for i, threshold in enumerate(thresholds):
        if value < threshold:
            return colors[i]

    return colors[-1]  # Default for value >= 30


def plot_info(df, title):
    fig = go.Figure()
    colors = [get_color(v) for v in df["value_inc_vat"]]

    fig.add_trace(
        go.Bar(
            x=df["valid_from"],
            y=df["value_inc_vat"],
            marker=dict(color=colors),
            name="Price [p/kWh]",
        )
    )
    fig.update_layout(
        plot_bgcolor=st.session_state.bg_color,
        font=dict(color=st.session_state.font, size=14),
        title=dict(text=title, font=dict(color=st.session_state.font)),
        xaxis=dict(
            title="Time",
            title_font=dict(color=st.session_state.font),
            tickfont=dict(color=st.session_state.font),
        ),
        yaxis=dict(
            title="Price [p/kWh]",
            title_font=dict(color=st.session_state.font),
            tickfont=dict(color=st.session_state.font),
        ),
    )
    st.plotly_chart(fig)


def plot_data():
    col1, col2 = st.columns([0.15, 0.85], vertical_alignment="center")

    with col1:
        day_to_plot = st.radio("Select day:", options=["Today", "Tomorrow"], index=0)

    with col2:
        if st.session_state.df is None:
            st.write(f"No data available for {day_to_plot.lower()}.")
        else:
            target_date = datetime.now(pytz.UTC).date()
            if day_to_plot == "Tomorrow":
                target_date += pd.Timedelta(days=1)

            df_filtered = st.session_state.df[
                st.session_state.df["valid_from"].dt.date == target_date
            ]

            if df_filtered.empty:
                st.write(f"No data available for {day_to_plot.lower()}.")
            else:
                plot_info(df_filtered, "Agile Pricing")


# """
# Get the optimal time to make coffee either this morning or tomorrow morning.
# Uses the date as tomorrow if it is after 10am, otherwise use today. Default mass, temperature is 650ml, 17degC to represent two cups of coffee at winter room temp.
# """


def get_optimal_coffee_time(df, current_time):
    coffee_day = (
        current_time.date() + timedelta(days=1)
        if current_time.hour > 10
        else current_time.date()
    )

    mass = 650
    init_temp = 17
    energy = kettle_energy(init_temp, cp, mass / 1000, kappa)

    target_start, target_end = (
        datetime.combine(coffee_day, t).replace(tzinfo=df["valid_from"].dt.tz)
        if df["valid_from"].dt.tz is not None
        else datetime.combine(coffee_day, t)
        for t in (time(7, 30), time(9, 30))
    )

    df_coffee = df[(df["valid_to"] <= target_end) & (df["valid_from"] >= target_start)]

    if df_coffee.empty:
        return None

    df_coffee["cost"] = round(energy / (3600) * df_coffee["value_inc_vat"] / 100, 4)
    return df_coffee.loc[df_coffee["cost"].idxmin()] if df_coffee is not None else None


def display_current_costs(current_time):
    cost_now, cost_next, current_row, next_row = get_current_cost(
        st.session_state.df, current_time
    )
    tracker_now, tracker_next, current_row_e, next_row_e = get_current_cost(
        st.session_state.df_tracker_e, current_time
    )

    coffee_best = get_optimal_coffee_time(st.session_state.df, datetime.now(pytz.UTC))
    col1, col2, col3, col4 = st.columns(4, gap="small")

    w = "95%"
    h = "120px"
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <div style="{st.session_state.col_format};
                    height: {h};
                    width: {w};">
                    <strong>Current Price</strong><br>
                    <span style="font-size: 1.3em;">{cost_now:.2f} p/kWh</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if current_time.hour < 16:
            only_today = st.session_state.df[
                (st.session_state.df["valid_from"].dt.date == current_time.date())
            ]
            off_peak = (only_today["valid_from"].dt.hour < 16) | (
                only_today["valid_from"].dt.hour >= 19
            )
            data = only_today[off_peak]

            av_price = data["value_inc_vat"].mean()

            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>Today's Average Off-Peak Price</strong><br>
                        <span style="font-size: 1.3em;">{av_price:.2f} p/kWh</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            only_tom = st.session_state.df[
                (
                    st.session_state.df["valid_from"].dt.date
                    == current_time.date() + timedelta(days=1)
                )
            ]
            off_peak = (only_tom["valid_from"].dt.hour < 16) | (
                only_tom["valid_from"].dt.hour >= 19
            )
            data = only_tom[off_peak]
            av_price = data["value_inc_vat"].mean()

            if av_price is None:
                st.markdown(
                    f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>Tomorrow's Average Off-Peak Price</strong><br>
                        <span style="font-size: 1.3em;">not available yet</span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center;">
                        <div style="{st.session_state.col_format};
                            height: {h};
                            width: {w};">
                            <strong>Tomorrow's Average Off-Peak Price</strong><br>
                            <span style="font-size: 1.3em;">{av_price:.2f} p/kWh</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if coffee_best is not None:
        with col3:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>The best time to make coffee is:</strong><br>
                        <span style="font-size: 1.3em;">{coffee_best["valid_from"].strftime("%H:%M")}</span>
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
                        <strong>The best time to make coffee is:</strong><br>
                        <span style="font-size: 1.3em;">Data not available yet</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if tracker_next is not None:
        with col4:
            tracker_delta = (tracker_next - tracker_now) / tracker_now * 100
            symb = "&uarr;" if tracker_delta > 0 else "&darr;"
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>Tomorrow's Tracker Trend</strong><br>
                        <span style="font-size: 1.3em;">{symb} {abs(tracker_delta):.1f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        with col4:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <div style="{st.session_state.col_format};
                        height: {h};
                        width: {w};">
                        <strong>Tomorrow's Tracker Trend</strong><br>
                        <span style="font-size: 1.3em;">Data not available</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(
                "Refresh tracker data",
                on_click=fetch_data.clear(st.session_state.df_tracker_e),
            )


# Function to load a module from a file
def load_module(module_name, filepath):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clear_input():
    st.session_state.temp = st.session_state.api_key
    st.session_state.api_key = ""


def main():
    if "temp" not in st.session_state:
        st.session_state.temp = ""  # Default value

    st.text_input(
        "Enter your Octopus Energy API key:", key="api_key", on_change=clear_input
    )

    api_key = st.session_state["temp"]

    if st.session_state.df is None:
        st.session_state.df = fetch_data(api_key, url)
        st.session_state.df_tracker_e = fetch_data(api_key, url_tracker_e)

    st.markdown(" ")  # Add some space between the input field and the plot
    if st.session_state.df is not None:
        display_current_costs(datetime.now(pytz.UTC))

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
