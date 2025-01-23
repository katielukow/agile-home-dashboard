import streamlit as st
import requests
import base64
import pandas as pd


def fetch_data(api_key):
    if api_key is None:
        st.write("Please enter an API key.")
        return None

    url = "https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-H/standard-unit-rates/"

    # Encode the API key for Basic Authentication
    auth_header = base64.b64encode(f"{api_key}:".encode("utf-8")).decode("utf-8")

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
