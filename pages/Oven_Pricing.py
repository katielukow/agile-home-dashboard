import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time


def main():
    st.title("Washing Machine Pricing on Octopus Agile")

    if st.session_state.df is not None:
        toggle = st.toggle("Select time manually", False)
        current_time = get_current_time(toggle, st.session_state.df)
        # wash_time = st.number_input("Washing run time [hr]:", value=1.5)
        # temp = st.number_input("Oven Temperature [C]:", value=170)
        bake_time = st.number_input("Total Bake Time [min]:", value=20)
        oven_power = 2.5  # kW
        current_price, next_price, current_cost_row, next_cost_row = get_current_cost(
            st.session_state.df, current_time
        )
        cost = oven_power * bake_time / 60 * current_price / 100

        st.write(f"The oven will cost approximate £{cost:.4f} to run.")

    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
