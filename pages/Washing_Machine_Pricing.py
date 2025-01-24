import streamlit as st
from datetime import datetime, timedelta
import pytz


def calculate_drying_cost(dry_time, power, df):
    costs = df[["value_inc_vat", "valid_from", "valid_to"]].copy()

    # Calculate the drying cost for each price window
    costs["drying_cost"] = costs["value_inc_vat"] * power

    # Define the rolling window size (convert hours to 30-minute intervals)
    window_size = int(dry_time * 2)  # 1 hour = 2 intervals (30 min each)
    costs["rolling_sum"] = costs["drying_cost"].rolling(window=window_size).sum()

    # Find the index of the minimum rolling cost
    min_index = costs["rolling_sum"].idxmin()

    # Extract the optimal end time
    end_time = costs.loc[min_index, "valid_to"]

    # Calculate the hours remaining from now until the optimal end time
    time_difference = end_time - datetime.now(pytz.UTC)
    end_at = round(
        time_difference.total_seconds() / 3600, 1
    )  # Round to 2 decimal places

    return end_time, end_at


def main():
    st.title("Washing Machine Pricing on Octopus Agile")

    if st.session_state.df is not None:
        # wash_time = st.number_input("Washing run time [hr]:", value=1.5)
        dry_time = st.number_input("Drying run time [hr]:", value=3.0)
        power = st.number_input("Washing machine power [kW]:", value=2.0)

        if st.session_state.df["valid_from"].max().date() != datetime.now(
            pytz.UTC
        ).date() + timedelta(days=1):
            st.warning("Data for tomorrow not available yet.")

        end_time, end_at = calculate_drying_cost(dry_time, power, st.session_state.df)

        st.write(
            f"The washing machine must end at {end_time.time()} if the dryer runs for {dry_time} hours."
        )
        st.write(f"Set the machine to end in {end_at} hours.")

    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
