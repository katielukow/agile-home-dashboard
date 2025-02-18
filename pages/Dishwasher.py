from datetime import timedelta

import pandas as pd
import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time, load_css

load_css()


def calculate_drying_cost(dishwasher_time, df, current_time):
    current_price, _, _, _ = get_current_cost(df, current_time)
    time_to_next_half_hour = 30 - current_time.minute % 30
    total_cost = 0

    if dishwasher_time <= time_to_next_half_hour:
        total_cost += (current_price * dishwasher_time) / 6000
    else:
        total_cost += (current_price * time_to_next_half_hour) / 6000
        remaining_time = dishwasher_time - time_to_next_half_hour

    while remaining_time > 30:
        current_time += timedelta(minutes=30)
        current_price, _, _, _ = get_current_cost(df, current_time)

        total_cost += (current_price * 30) / 6000
        remaining_time -= 30

    if remaining_time > 0:
        current_time += timedelta(minutes=30)
        current_price, _, _, _ = get_current_cost(df, current_time)
        total_cost += (current_price * remaining_time) / 6000

    # st.write(f"Total cost: £{total_cost:.2f}")

    # # Define the rolling window size
    # window_size = int(dishwasher_time / 30)  # 1 hour = 2 intervals (30 min each)
    # costs["rolling_sum"] = costs["value_inc_vat"].rolling(window=window_size).sum()
    # st.write(window_size)
    # # Find the minimum cost index and end time
    # min_index = costs["rolling_sum"].idxmin()
    # end_time = costs.loc[min_index, "valid_to"]

    # # Calculate the hours remaining from now until the optimal end time
    # time_diff = end_time - current_time
    # end_at = round(time_diff.total_seconds() / 3600, 1)

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
        dishwasher_time = st.text_input("Enter time (HH:MM):", value="03:47")

        try:
            hours, minutes = map(int, dishwasher_time.split(":"))
            dishwasher_time = hours * 60 + minutes
            # st.write(f"Total time dishwasher runs: {dishwasher_time} minutes")
        except ValueError:
            st.error("Invalid time format. Please use HH:MM format.")

        dish_costs = pd.DataFrame(columns=["time", "cost"])

        remaining_time = current_time
        while (
            remaining_time + timedelta(minutes=dishwasher_time)
            <= st.session_state.df["valid_to"].max()
        ):
            cost = calculate_drying_cost(
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
        # if current_time is not None:

        #     # dry_time = st.number_input("Drying run time [hr]:", value=3.0)
        #     power = st.number_input("Washing machine power [kW]:", value=2.0)

        #     forward_df = st.session_state.df[
        #         st.session_state.df["valid_from"]
        #         > current_time
        #     ]

        #     if st.session_state.df["valid_from"].max().date() != dtime.now(
        #         pytz.UTC
        #     ).date() + timedelta(days=1):
        #         st.warning("Data for tomorrow not available yet.")

        #     if (
        #         current_time + timedelta(minutes=dishwasher_time)
        #         > st.session_state.df["valid_from"].max()
        #     ):
        #         st.warning("Not enough data available for the selected washing time.")
        #     else:
        #         end_time, end_at = calculate_drying_cost(
        #             dishwasher_time, forward_df, current_time
        #         )
        #         display_washer_timing(end_time, end_at)

        # else:
        #     st.markdown("##")
    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
