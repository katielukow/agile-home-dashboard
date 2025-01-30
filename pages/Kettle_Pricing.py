import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time, load_css

load_css()


def calculate_kettle_cost(current_price, next_price, run_time, power):
    cost_now = ((run_time / 3600) * current_price * power) / 100
    cost_next = ((run_time / 3600) * next_price * power) / 100
    return cost_now, cost_next


# Function to display kettle costs
def display_kettle_costs(
    current_price, next_price, cost_now, cost_next, current_cost_row, next_cost_row
):
    col1, col2 = st.columns(2, gap="small")
    w = "95%"
    h = "120px"
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <div style="{st.session_state.col_format};
                    height: {h};
                    width: {w};">
                    <strong>Current Energy Cost</strong><br>
                    <span style="font-size: 1.5em;">{current_price:.4f} p/kWh</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div style="display: flex; justify-content: center;">
            <div style="{st.session_state.col_format};
            height: {h};
            width: {w};">
                <strong>Next Energy Cost</strong><br>
                <span style="font-size: 1.5em;">{next_price:.4f} p/kWh</span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="small")
    with col3:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <div style="{st.session_state.col_format};
                height: {h};
                width: {w};">
                    <strong>Current Kettle Cost</strong><br>
                    <span style="font-size: 1.5em;">£{cost_now:.4f}</span>
                    <span style="font-size: 1em;">Valid until {current_cost_row.iloc[0]["valid_to"].strftime("%H:%M")}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <div style="{st.session_state.col_format};
                height: {h};
                width: {w};">
                    <strong>Next Kettle Cost</strong><br>
                    <span style="font-size: 1.5em;">£{cost_next:.4f}</span>
                    <span style="font-size: 1em;">Valid from {next_cost_row["valid_from"].strftime("%H:%M")} to {next_cost_row["valid_to"].strftime("%H:%M")} </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Function to plot kettle timing
def plot_kettle_timing():
    kettle_timing = pd.DataFrame(
        {
            "Volume [mL]": [600, 550, 350, 1100, 637, 804, 600, 570, 500, 830],
            "Time [s]": [137, 135, 98, 237, 148, 178, 150, 125, 130, 205],
            "Starting Temp [C]": [18, 18, 12, 12, 15, 11, 16, 13, 12, 10],
        }
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=kettle_timing["Volume [mL]"],
            y=kettle_timing["Time [s]"],
            mode="markers",
            marker=dict(size=12, color=st.session_state.marker),
        )
    )

    fig.update_layout(
        plot_bgcolor=st.session_state.bg_color,
        font=dict(
            color=st.session_state.font,
            size=14,
        ),
        title=dict(
            text="Kettle Timing Plot",
            font=dict(color=st.session_state.font),
        ),
        xaxis=dict(
            title="Time",
            title_font=dict(color=st.session_state.font),
            tickfont=dict(color=st.session_state.font),
        ),
        yaxis=dict(
            title="Price [p/kWh]",
            title_font=dict(color=st.session_state.font),
            tickfont=dict(color=st.session_state.font),
        ),
    )
    st.plotly_chart(fig)


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
    st.title("Kettle Pricing on Octopus Agile")
    if st.session_state.df is not None:
        st.markdown(
            f"""
                <div style="
                    color: {st.session_state.font};
                    border-radius: 10px;
                    margin-bottom: 10px;">
                    <span style="font-size: 1.1em;">Kettle run time [s]:</span><br>
                </div>
                """,
            unsafe_allow_html=True,
        )

        run_time = st.number_input(
            "Kettle run time [s]:",
            min_value=0,
            max_value=10000,
            value=137,
            label_visibility="collapsed",
        )

        st.markdown(
            f"""
                <div style="
                    color: {st.session_state.font};
                    border-radius: 10px;
                    margin-bottom: 10px;">
                    <span style="font-size: 1.1em;">Kettle power [kW]:</span><br>
                </div>
                """,
            unsafe_allow_html=True,
        )

        power = st.number_input(
            "Kettle power [kW]:",
            min_value=0.0,
            max_value=1e8,
            value=2.1,
            label_visibility="collapsed",
        )

        # Toggle for manual time selection
        toggle = st.toggle("Select time manually", False)
        current_time = get_current_time(toggle, st.session_state.df)
        current_price, next_price, current_cost_row, next_cost_row = get_current_cost(
            st.session_state.df, current_time
        )

        (
            cost_now,
            cost_next,
        ) = calculate_kettle_cost(current_price, next_price, run_time, power)

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

        st.markdown("##")
        plot_kettle_timing()
    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
