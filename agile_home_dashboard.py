import base64
from datetime import datetime, timedelta

import pandas as pd
import pytz
import requests
import streamlit as st


def fetch_data(api_key):
    if api_key is None:
        st.write("Please enter an API key.")
        return None

    url = "https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-H/standard-unit-rates/"

    # Encode the API key for Basic Authentication
    auth_header = base64.b64encode(f"{api_key}:".encode()).decode("utf-8")

    # Set up the headers
    headers = {
        "Authorization": f"Basic {auth_header}",
    }

    # Make the request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Parse the results
        results = data.get("results", [])

        # Create a DataFrame for easier manipulation
        df = pd.DataFrame(results)

        # Convert valid_from and valid_to to datetime
        df["valid_from"] = pd.to_datetime(df["valid_from"])
        df["valid_to"] = pd.to_datetime(df["valid_to"])

        # Sort by time
        df = df.sort_values(by="valid_from")
        return df

    else:
        st.write(f"Failed to fetch data. Status code: {response.status_code}")
        st.write(response.text)
        return None


def get_current_time(toggle, df):
    if toggle:
        col1, col2 = st.columns([1, 3])  # Adjust the column widths as needed

        # Day toggle in the first column
        with col1:
            day_toggle = st.radio("Select day:", options=["Today", "Tomorrow"], index=0)

        # Determine the selected date
        selected_date = (
            datetime.now(pytz.UTC).date()
            if day_toggle == "Today"
            else datetime.now(pytz.UTC).date() + timedelta(days=1)
        )

        # Filter DataFrame based on the selected date
        df = df[df["valid_from"].dt.date == selected_date]

        if not df.empty:
            # Define slider bounds
            start_time = df["valid_from"].min().to_pydatetime()
            end_time = df["valid_from"].max().to_pydatetime()

            # Slider in the second column
            with col2:
                selected_time = st.slider(
                    "Select time:",
                    min_value=start_time,
                    max_value=end_time,
                    value=start_time,
                    format="HH:mm",
                    step=timedelta(minutes=1),
                )

            combined_datetime = datetime.combine(selected_date, selected_time.time())
        else:
            st.warning(f"No data available for {day_toggle.lower()}!")
            return None

        combined_datetime = datetime.combine(selected_date, selected_time.time())
        return pd.to_datetime(pytz.UTC.localize(combined_datetime))

    return datetime.now(pytz.UTC)


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
