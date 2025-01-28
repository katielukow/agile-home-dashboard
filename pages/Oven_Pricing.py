import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time, load_css

load_css()


def display_oven_costs(current_price, next_price, cost_now, current_cost_row):
    col1, col2, col3 = st.columns(3)
    # row2 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="
                background-color: {st.session_state.primary_color};
                color: white;
                text-align: center;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                <strong style="font-size: 1.2em;">Current Energy Cost</strong><br>
                <span style="font-size: 1.4em;">{current_price:.4f} p/kWh</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
                <div style="
                    background-color: {st.session_state.primary_color};
                    color: white;
                    text-align: center;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                    <strong style="font-size: 1.2em;">Current Energy Cost</strong><br>
                    <span style="font-size: 1.4em;">{next_price:.4f} p/kWh</span>
                </div>
                """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
                <div style="
                    background-color: {st.session_state.primary_color};
                    color: white;
                    text-align: center;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                    <strong style="font-size: 1.2em;">Current Oven Cost</strong><br>
                    <span style="font-size: 1.4em;">£{cost_now:.4f}</span>
                </div>
                """,
            unsafe_allow_html=True,
        )


def calculate_kettle_cost(current_price, next_price, run_time, power):
    cost_now = ((run_time / 3600) * current_price * power) / 100
    cost_next = ((run_time / 3600) * next_price * power) / 100
    return cost_now, cost_next


st.markdown(
    """
    <style>
    /* Style for the number input label */
    label[for="total-bake-time"] {
        font-size: 1.5em; /* Increase label font size */
        font-weight: bold; /* Make label bold */
    }

    /* Style for the number input box */
    div[data-baseweb="input"] input {
        font-size: 1.1em; /* Increase font size inside the input box */
        padding: 10px; /* Add padding for a larger input field */
        height: 60px; /* Set height for larger appearance */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("Oven Pricing on Octopus Agile")

    if st.session_state.df is not None:
        toggle = st.toggle("Select time manually", False)
        current_time = get_current_time(toggle, st.session_state.df)

        st.markdown(
            f"""
                <div style="
                    color: {st.session_state.font};
                    border-radius: 10px;
                    padding-bottom: 10px;">
                    <span style="font-size: 1.1em;">Total bake time [min]:</span><br>
                </div>
                """,
            unsafe_allow_html=True,
        )
        bake_time = st.number_input(
            "Total bake time [min]: ", value=20, label_visibility="collapsed"
        )
        oven_power = 2.5  # kW
        current_price, next_price, current_cost_row, _ = get_current_cost(
            st.session_state.df, current_time
        )
        time_to_next_half_hour = 30 - current_time.minute % 30

        if time_to_next_half_hour > bake_time:
            cost = oven_power * (current_price * (bake_time) / 60) / 100  # £
        else:
            cost = (
                oven_power * (current_price * (time_to_next_half_hour) / 60) / 100
                + oven_power
                * (next_price * (bake_time - time_to_next_half_hour) / 60)
                / 100
            )  # £

        display_oven_costs(
            current_price,
            next_price,
            cost,
            current_cost_row,
        )

        # st.write(f"The oven will cost approximate £{cost:.4f} to run.")

    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
