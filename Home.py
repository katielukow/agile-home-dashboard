import streamlit as st
import os
import numpy as np
import requests
import base64
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go

@st.cache_resource
def fetch_data(api_key): 
    if api_key is None:
        st.write('Please enter an API key.')
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

    
# Define the directory for pages
st.set_page_config(
    page_title="Agile Daily Overview",
    # page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")


api_key = st.text_input('Enter your Octopus Energy API key:', None)


df = fetch_data(api_key)
# st.title('Kettle Pricing on Octopus Agile')

day_to_plot = st.selectbox('Select a day to plot:', ['Today', 'Tomorrow'])
if day_to_plot == 'Today':
    if df is None:
        st.write('No data available for today.')
    else:
        df_today = df[df['valid_from'].dt.date == datetime.now(pytz.UTC).date()]
        fig_all = go.Figure()
        fig_all.add_trace(go.Bar(
            x=df_today['valid_from'],  # Time column
            y=df_today['value_inc_vat'],  # Price column
            marker=dict(color='#3d405b'),  # Optional: Set bar color
            name="Price [p/kWh]"  # Legend name
        ))

        fig_all.update_layout(
        plot_bgcolor='rgba(129, 178, 154, 0.2)',  # Set the plot area background to white
        font=dict(
            color='#3d405b',  # Set text color
            size=14  # Optional: Adjust text size for better visibility
        ),
        title=dict(
            text="Agile Pricing",  # Add a title
            font=dict(color='#3d405b')  # Set title text color
        ),
        xaxis=dict(
            title="Time",  # Label the x-axis
            title_font=dict(color='#3d405b'),  # X-axis title color
            tickfont=dict(color='#3d405b')  # X-axis tick color
        ),
        yaxis=dict(
            title="Price [p/kWh]",  # Label the y-axis
            title_font=dict(color='#3d405b'),  # Y-axis title color
            tickfont=dict(color='#3d405b')  # Y-axis tick color
        )
        )
        st.plotly_chart(fig_all)
elif day_to_plot == 'Tomorrow':
    tomorrow_date = (datetime.now(pytz.UTC) + pd.Timedelta(days=1)).date()
    df_tom = df[df['valid_from'].dt.date == tomorrow_date]

    if df_tom.empty:
        st.write('No data available for tomorrow.')
    else:
        fig_all = go.Figure()
        fig_all.add_trace(go.Bar(
            x=df_tom['valid_from'],  # Time column
            y=df_tom['value_inc_vat'],  # Price column
            marker=dict(color='#3d405b'),  # Optional: Set bar color
            name="Price [p/kWh]"  # Legend name
        ))

        fig_all.update_layout(
        plot_bgcolor='rgba(129, 178, 154, 0.2)',  # Set the plot area background to white
        font=dict(
            color='#3d405b',  # Set text color
            size=14  # Optional: Adjust text size for better visibility
        ),
        title=dict(
            text="Agile Pricing",  # Add a title
            font=dict(color='#3d405b')  # Set title text color
        ),
        xaxis=dict(
            title="Time",  # Label the x-axis
            title_font=dict(color='#3d405b'),  # X-axis title color
            tickfont=dict(color='#3d405b')  # X-axis tick color
        ),
        yaxis=dict(
            title="Price [p/kWh]",  # Label the y-axis
            title_font=dict(color='#3d405b'),  # Y-axis title color
            tickfont=dict(color='#3d405b')  # Y-axis tick color
        )
        )
        st.plotly_chart(fig_all)

# st.cache_data.clear()
# file_path = os.path.join(PAGES_DIR, '1_All_Data.py')


# st.write(pd.DataFrame(kettle_timing))
PAGES_DIR = 'Pages'
# Function to load a module from a file
def load_module(module_name, filepath):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Get a list of pages
page_files = [f for f in os.listdir(PAGES_DIR) if f.endswith('.py')]
pages = {f.replace('.py', '').replace('_', ' ').title(): os.path.join(PAGES_DIR, f) for f in page_files}

# main_page = '0 Trip Visualisation'
# load_module(main_page, pages[main_page]).app()
