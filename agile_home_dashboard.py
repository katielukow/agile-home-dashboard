from datetime import datetime as dtime
from datetime import time, timedelta

import pandas as pd
import pytz
import requests
import streamlit as st

london_timezone = pytz.timezone("Europe/London")

diff = dtime.combine(
    dtime.now(london_timezone).date(),
    time(16, 10),
    tzinfo=london_timezone,
) - dtime.now(london_timezone)


@st.cache_data(ttl=diff)
def fetch_data(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            df = pd.DataFrame(results)

            df["valid_from"] = pd.to_datetime(df["valid_from"], utc=True)
            df["valid_to"] = pd.to_datetime(df["valid_to"], utc=True)

            # Convert to London time zone
            df["valid_from"] = df["valid_from"].dt.tz_convert(london_timezone)
            df["valid_to"] = df["valid_to"].dt.tz_convert(london_timezone)

            return df.sort_values(by="valid_from")
        else:
            st.write(f"Failed to fetch data. Status code: {response.status_code}")
            st.write(response.text)
            return None
    except Exception as e:
        st.write(f"Error fetching data: {str(e)}")
        return None


def get_current_time(toggle, df):
    if not toggle:
        return dtime.now(london_timezone)
    else:
        col1, col2 = st.columns([1, 3])  # Adjust the column widths as needed

        # Day toggle in the first column
        with col1:
            day_toggle = st.radio("Select day:", options=["Today", "Tomorrow"], index=0)

        # Determine the selected date
        selected_date = (
            dtime.now(london_timezone).date()
            if day_toggle == "Today"
            else dtime.now(london_timezone).date() + timedelta(days=1)
        )

        # Filter DataFrame based on the selected date
        df = df[df["valid_from"].dt.date == selected_date]

        if not df.empty:
            start_time = df["valid_from"].min().to_pydatetime()
            end_time = df["valid_from"].max().to_pydatetime()

            if "selected_time" not in st.session_state:
                st.session_state.selected_time = dtime.now(london_timezone)

            with col2:
                selected_time = st.slider(
                    "Select time:",
                    min_value=start_time,
                    max_value=end_time,
                    value=st.session_state.selected_time,
                    format="HH:mm",
                    step=timedelta(minutes=5),
                )

            combined_datetime = dtime.combine(selected_date, selected_time.time())
            return pd.to_datetime(pytz.UTC.localize(combined_datetime))

        else:
            st.warning(f"No data available for {day_toggle.lower()}!")
            return None


def get_current_cost(df, current_time):
    current_cost_row = df[
        (df["valid_from"] <= current_time) & (df["valid_to"] > current_time)
    ]
    current_price = current_cost_row.iloc[0]["value_inc_vat"]
    if current_cost_row.empty:
        return None, None, None, None

    if current_cost_row.index[0] == df.index[-1]:
        next_cost_row = current_cost_row
        next_price = 0
    else:
        next_cost_row = df.iloc[df.index.get_loc(current_cost_row.index[0]) + 1]
        next_price = next_cost_row["value_inc_vat"]

    return current_price, next_price, current_cost_row, next_cost_row


def load_css():
    st.markdown(
        f"""
        <style>
        /* Change the text color in the input field */
        div[data-baseweb="input"] input {{
            color: white;
            background-color: {st.session_state.textBoxColor};
        }}

        /* Style the +/- buttons at the end of number input */
        div[data-testid="stNumberInput"] button {{
            color: white;
            background-color: {st.session_state.textBoxColor};
        }}

        /* Optional: Change hover effect for buttons */
        div[data-testid="stNumberInput"] button:hover {{
            background-color: {st.session_state.textBoxColor};
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.col_format = f"background-color: {st.session_state.primary_color}; color: white; text-align: center; padding: 20px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-direction: column;"
