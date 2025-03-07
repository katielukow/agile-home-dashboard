from datetime import timedelta

import pandas as pd
import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time, load_css

load_css()


def calculate_total_cost(dishwasher_time, df, current_time):
    """
    Calculate the total electricity cost for running a dishwasher.

    This function computes the cost by breaking the dishwasher runtime into
    half-hour segments and applying the appropriate electricity price for each segment.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing electricity price data.
    current_time : datetime
        The starting time for the calculation.
    dishwasher_time : int or float
        The total runtime of the dishwasher in minutes.

    Returns:
    --------
    float
        The total cost of electricity for running the dishwasher.
        Cost is calculated as (price * time_in_minutes).
    """
    total_cost = 0
    remaining_time = dishwasher_time

    while remaining_time > 0:
        current_price = get_current_cost(df, current_time)[0]
        time_to_next_half_hour = 30 - current_time.minute % 30
        time_slice = min(remaining_time, time_to_next_half_hour)

        # Compute costs, decrement remaining time
        total_cost += current_price * time_slice  # / 6000
        remaining_time -= time_slice

        # Shift current time
        current_time += timedelta(minutes=time_slice)

    return total_cost


def display_washer_timing(end_time, end_at):
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px;">
            <div>
                <strong>Dryer must end by:</strong>
            </div>
            <div>
                <strong>{}</strong>
            </div>
            <div>
                <strong>Set total dryer time to:</strong>
            </div>
            <div>
                <strong>{:.2f} hours</strong>
            </div>
        </div>
        """.format(end_time.strftime("%d-%m-%y %H:%M"), end_at),
        unsafe_allow_html=True,
    )


def main():
    st.title("Dishwasher Pricing on Octopus Agile")

    if st.session_state.df is not None:
        toggle = st.toggle("Select time manually", False)
        current_time = get_current_time(toggle, st.session_state.df)
        remaining_time = current_time
        dishwasher_time = st.text_input("Enter time (HH:MM):", value="03:47")

        try:
            hours, minutes = map(int, dishwasher_time.split(":"))
            dishwasher_time = hours * 60 + minutes
        except ValueError:
            st.error("Invalid time format. Please use HH:MM format.")

        dish_costs = pd.DataFrame(columns=["time", "cost"])

        while (
            remaining_time + timedelta(minutes=dishwasher_time)
            <= st.session_state.df["valid_to"].max()
        ):
            cost = calculate_total_cost(
                dishwasher_time, st.session_state.df, remaining_time
            )
            dish_costs = pd.concat(
                [dish_costs, pd.DataFrame({"time": [remaining_time], "cost": [cost]})]
            )
            remaining_time += timedelta(minutes=30)

        dish_costs.reset_index(drop=True, inplace=True)
        min_cost_loc = dish_costs["cost"].idxmin()
        delay = dish_costs.loc[min_cost_loc]["time"] - current_time

        st.write(f"Delay the dishwasher: {delay.total_seconds() / 3600} hours")

    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
