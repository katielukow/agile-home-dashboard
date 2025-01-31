import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time, load_css

load_css()


def display_oven_costs(current_price, next_price, cost_now, current_cost_row):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="{st.session_state.col_format}">
                <strong style="font-size: 1.2em;">Current Energy Cost</strong><br>
                <span style="font-size: 1.4em;">{current_price:.4f} p/kWh</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
                <div style="{st.session_state.col_format}">
                    <strong style="font-size: 1.2em;">Next Energy Cost</strong><br>
                    <span style="font-size: 1.4em;">{next_price:.4f} p/kWh</span>
                </div>
                """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
                <div style="{st.session_state.col_format}">
                    <strong style="font-size: 1.2em;">Total Oven Cost</strong><br>
                    <span style="font-size: 1.4em;">£{cost_now:.4f}</span>
                </div>
                """,
            unsafe_allow_html=True,
        )


st.markdown(
    """
    <style>{
        font-size: 1.5em;
        font-weight: bold;
    }

    div[data-baseweb="input"] input {
        font-size: 1.1em;
        padding: 10px;
        height: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
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
                    margin-bottom: 10px;">
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
            cost = oven_power * current_price * (bake_time) / 6000  # £
        else:
            cost = (
                oven_power
                * (
                    current_price * time_to_next_half_hour
                    + next_price * (bake_time - time_to_next_half_hour)
                )
                / 6000
            )  # £

        display_oven_costs(
            current_price,
            next_price,
            cost,
            current_cost_row,
        )

    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
