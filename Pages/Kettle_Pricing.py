import streamlit as st
import os
import numpy as np
import requests
import base64
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go
from Home import df

# st.set_page_config(
#     page_title="Kettle Pricing on Octopus Agile",
#     # page_icon="🏂",
#     layout="wide",
#     initial_sidebar_state="expanded")

st.title('Kettle Pricing on Octopus Agile')
st.write('How much does the kettle cost right now?')

time = st.number_input('Kettle run time [s]:', min_value=0, max_value=2000, value=137)
kettle_power = st.number_input('Kettle power [kW]:', min_value=0.0, max_value=3.0, value=2.1)

toggle = st.toggle('Select time manually', False)

if toggle:
    selected_time = st.time_input('Select time:', '12:00')
    combined_datetime = datetime.combine(datetime.now(pytz.UTC).date(), selected_time)  # Combine date and time
    utc_datetime = pytz.UTC.localize(combined_datetime)  # Localize to UTC
    current_time = pd.to_datetime(utc_datetime)
else:
    current_time = datetime.now(pytz.UTC)

current_cost_row = df[(df['valid_from'] <= current_time) & (df['valid_to'] > current_time)]
next_cost_row = df.iloc[df.index.get_loc(current_cost_row.index[0]) + 1]
 


if not current_cost_row.empty:
    agile_price = current_cost_row.iloc[0]['value_inc_vat']
    agile_next = next_cost_row['value_inc_vat']
    # st.write(f"The current cost is {agile_price} p/kWh.")
else:
    st.write("No pricing data available for the current time.")

cost = ((time / 3600) * agile_price * kettle_power) / 100 # £
cost_next = ((time / 3600) * agile_next * kettle_power) / 100 # £

st.write(f'Current energy cost: £{agile_price:.4f} p/kWh')
st.write(f'Next energy cost: £{agile_next:.4f} p/kWh')

st.write(f'The kettle costs £{cost:.4f} until {current_cost_row.iloc[0]['valid_to'].strftime('%H:%M')}.')

if cost_next > cost:
    color = "red"
elif cost_next <= cost:
    color = "green"

st.markdown(f'<p style="color:{color};">The kettle will cost £{cost_next:.4f} from {next_cost_row['valid_from'].strftime('%H:%M')} to {next_cost_row['valid_to'].strftime('%H:%M')}.  </p>', unsafe_allow_html=True)



# Kettle timing model - to be refined and updated

kettle_timing = pd.DataFrame({'Volume [mL]': [600, 550, 350, 1100, 637], 'Time [s]': [137, 135, 98, 237, 148], 'Starting Temp [C]': [18, 18, 12, 12, 15]})

fig = go.Figure()
fig.add_trace(go.Scatter(x=kettle_timing['Volume [mL]'], 
                         y=kettle_timing['Time [s]'], 
                         mode='markers', 
                         marker=dict(size=12, color='blue')))


fig.update_layout(
    plot_bgcolor='white',  # Set the plot area background to white
    paper_bgcolor='white',  # Set the overall background to white
    title="Kettle Timing Plot",  # Optional: Add a title to the plot
    xaxis_title="Volume [mL]",  # Optional: Label the x-axis
    yaxis_title="Time [s]"  # Optional: Label the y-axis
)
st.plotly_chart(fig)
