import streamlit as st
from datetime import datetime, timedelta
import pytz
from agile_home_dashboard import get_current_time


def calculate_drying_cost(dry_time, power, df, current_time):
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
    time_difference = end_time - current_time
    end_at = round(
        time_difference.total_seconds() / 3600, 1
    )  # Round to 2 decimal places

    return end_time, end_at


def display_washer_timing(end_time, end_at):
    # st.write(
    #                 f"The washing machine must end by {end_time.time()} if the dryer runs for {dry_time} hours."
    #             )
    #             st.write(f"Set the machine to end in {end_at} hours.")
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
    st.title("Washing Machine Pricing on Octopus Agile")

    if st.session_state.df is not None:
        toggle = st.toggle("Select time manually", False)
        current_time = get_current_time(toggle, st.session_state.df)
        if current_time is not None:
            wash_time = st.number_input("Washing run time [hr]:", value=2.5)
            dry_time = st.number_input("Drying run time [hr]:", value=3.0)
            power = st.number_input("Washing machine power [kW]:", value=2.0)

            forward_df = st.session_state.df[
                st.session_state.df["valid_from"]
                > current_time + timedelta(hours=wash_time)
            ]

            if st.session_state.df["valid_from"].max().date() != datetime.now(
                pytz.UTC
            ).date() + timedelta(days=1):
                st.warning("Data for tomorrow not available yet.")

            if (
                current_time + timedelta(hours=wash_time + dry_time)
                > st.session_state.df["valid_from"].max()
            ):
                st.warning("Not enough data available for the selected washing time.")
            else:
                end_time, end_at = calculate_drying_cost(
                    dry_time, power, forward_df, current_time
                )
                display_washer_timing(end_time, end_at)

        else:
            st.markdown("##")
    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
