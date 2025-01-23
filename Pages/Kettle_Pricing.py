import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go
# from Home import api_key


# Function to get the current or selected time
def get_current_time(toggle):
    if toggle:
        selected_time = st.time_input("Select time:", "12:00")
        combined_datetime = datetime.combine(
            datetime.now(pytz.UTC).date(), selected_time
        )
        return pd.to_datetime(pytz.UTC.localize(combined_datetime))
    return datetime.now(pytz.UTC)


# Function to calculate kettle cost
def calculate_kettle_cost(df, current_time, run_time, power):
    current_cost_row = df[
        (df["valid_from"] <= current_time) & (df["valid_to"] > current_time)
    ]
    if current_cost_row.empty:
        return None, None, None, None

    next_cost_row = df.iloc[df.index.get_loc(current_cost_row.index[0]) + 1]
    current_price = current_cost_row.iloc[0]["value_inc_vat"]
    next_price = next_cost_row["value_inc_vat"]

    cost_now = ((run_time / 3600) * current_price * power) / 100
    cost_next = ((run_time / 3600) * next_price * power) / 100

    return (
        current_price,
        next_price,
        cost_now,
        cost_next,
        current_cost_row,
        next_cost_row,
    )


# Function to display kettle costs
def display_kettle_costs(
    current_price, next_price, cost_now, cost_next, current_cost_row, next_cost_row
):
    st.write(f"Current energy cost: £{current_price:.4f} p/kWh")
    st.write(f"Next energy cost: £{next_price:.4f} p/kWh")

    st.write(
        f"The kettle costs £{cost_now:.4f} until {current_cost_row.iloc[0]['valid_to'].strftime('%H:%M')}."
    )

    color = "green" if cost_next <= cost_now else "red"
    st.markdown(
        f'<p style="color:{color};">The kettle will cost £{cost_next:.4f} '
        f"from {next_cost_row['valid_from'].strftime('%H:%M')} "
        f"to {next_cost_row['valid_to'].strftime('%H:%M')}. </p>",
        unsafe_allow_html=True,
    )


# Function to plot kettle timing
def plot_kettle_timing():
    kettle_timing = pd.DataFrame(
        {
            "Volume [mL]": [600, 550, 350, 1100, 637],
            "Time [s]": [137, 135, 98, 237, 148],
            "Starting Temp [C]": [18, 18, 12, 12, 15],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=kettle_timing["Volume [mL]"],
            y=kettle_timing["Time [s]"],
            mode="markers",
            marker=dict(size=12, color="blue"),
        )
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title="Kettle Timing Plot",
        xaxis_title="Volume [mL]",
        yaxis_title="Time [s]",
    )
    st.plotly_chart(fig)


# Main application logic
def main():
    st.title("Kettle Pricing on Octopus Agile")

    st.write("How much does the kettle cost right now?")

    # Inputs for kettle power and run time
    run_time = st.number_input(
        "Kettle run time [s]:", min_value=0, max_value=2000, value=137
    )
    power = st.number_input(
        "Kettle power [kW]:", min_value=0.0, max_value=3.0, value=2.1
    )

    # Toggle for manual time selection
    toggle = st.toggle("Select time manually", False)
    current_time = get_current_time(toggle)

    # Calculate and display costs
    (
        current_price,
        next_price,
        cost_now,
        cost_next,
        current_cost_row,
        next_cost_row,
    ) = calculate_kettle_cost(st.session_state.df, current_time, run_time, power)

    if current_price is not None:
        display_kettle_costs(
            current_price,
            next_price,
            cost_now,
            cost_next,
            current_cost_row,
            next_cost_row,
        )
    else:
        st.write("No pricing data available for the current time.")

    # Plot kettle timing
    plot_kettle_timing()


# Run the application
if __name__ == "__main__":
    main()
