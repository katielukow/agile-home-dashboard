from datetime import datetime as dtime
from datetime import timedelta

import plotly.graph_objects as go
import pytz
import streamlit as st

from agile_home_dashboard import get_current_cost, get_current_time, load_css
from utils import cp, fit_kettle_efficiency, kettle_energy, kettle_timing

load_css()

# Get kettle efficiency
kettle_efficiency = fit_kettle_efficiency()


def calculate_kettle_cost(current_price, next_price, init_temp, mass):
    """
    Calculates the kettle cost
    """
    energy = kettle_energy(init_temp, cp, mass / 1000, kettle_efficiency)
    cost_now = energy / (3600) * current_price / 100
    cost_next = energy / (3600) * next_price / 100

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
            <div style="display: flex; justify-content: center;padding-bottom:20px;">
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
        <div style="display: flex; justify-content: center;padding-bottom:20px;">
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

    col3, col4 = st.columns(2, gap="small")
    with col3:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;padding-bottom:20px;">
                <div style="{st.session_state.col_format};
                height: {h};
                width: {w};">
                    <strong>Current Kettle Cost</strong><br>
                    <span style="font-size: 1.5em;">{cost_now * 100:.2f}p</span>
                    <span style="font-size: 1em;">Valid until {current_cost_row.iloc[0]["valid_to"].strftime("%H:%M")}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;padding-bottom:20px;">
                <div style="{st.session_state.col_format};
                height: {h};
                width: {w};">
                    <strong>Next Kettle Cost</strong><br>
                    <span style="font-size: 1.5em;">{cost_next * 100:.2f}p</span>
                    <span style="font-size: 1em;">Valid from {next_cost_row["valid_from"].strftime("%H:%M")} to {next_cost_row["valid_to"].strftime("%H:%M")} </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_cheapest_time(df, forward_time):
    target_start = dtime.now(pytz.timezone("Europe/London"))
    current_window = (
        dtime.now(pytz.timezone("Europe/London")).minute // 30
    ) * 30  # round down to the nearest 30 minutes for to include current price
    target_start = target_start.replace(minute=current_window, second=0, microsecond=0)
    target_end = dtime.now(pytz.timezone("Europe/London")) + timedelta(
        hours=forward_time
    )

    df_time = df[
        (df["valid_from"] <= target_end) & (df["valid_from"] >= target_start)
    ].copy()

    if df_time.empty:
        return None
    else:
        return df_time.loc[df_time["value_inc_vat"].idxmin()]


# Function to plot kettle timing
def plot_kettle_timing():
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
            title="Volume [mL]",
            title_font=dict(color=st.session_state.font),
            tickfont=dict(color=st.session_state.font),
        ),
        yaxis=dict(
            title="Time [s]",
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
                    <span style="font-size: 1.1em;">Amount of water [mL]:</span><br>
                </div>
                """,
            unsafe_allow_html=True,
        )

        mass = st.number_input(
            "Amount of water [mL]",
            min_value=0,
            max_value=10000,
            value=550,
            label_visibility="collapsed",
        )

        st.markdown(
            f"""
                <div style="
                    color: {st.session_state.font};
                    border-radius: 10px;
                    margin-bottom: 10px;">
                    <span style="font-size: 1.1em;">Initial Temperature [C]:</span><br>
                </div>
                """,
            unsafe_allow_html=True,
        )

        init_temperature = st.number_input(
            "Initial Temperature [C]",
            min_value=0.0,
            max_value=1e8,
            value=15.0,
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
        ) = calculate_kettle_cost(current_price, next_price, init_temperature, mass)

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
        st.write("Select the length of time in the future to optimize the kettle boil.")
        col1, col2, col3 = st.columns([2, 1, 1], vertical_alignment="center")
        with col1:
            forward_time = st.number_input(
                "Forward time [hr]:", value=1.0, step=0.5, label_visibility="collapsed"
            )
        with col2:
            cheapest_time = get_cheapest_time(st.session_state.df, forward_time)
            st.markdown(
                f"""
                    <div style="display: flex; justify-content: center;padding-bottom:15px;">
                        <div style="{st.session_state.col_format};
                        height: {"40px"};
                        width: {"95%"};">
                            <span style="font-size: 1.2em;">{cheapest_time["valid_from"].strftime("%H:%M")} </span>
                        </div>
                    </div>
                    """,
                unsafe_allow_html=True,
            )
        with col3:
            cheap_price = cheapest_time["value_inc_vat"]
            cost_cheap, _ = calculate_kettle_cost(
                cheap_price, next_price, init_temperature, mass
            )
            st.markdown(
                f"""
                    <div style="display: flex; justify-content: center;padding-bottom:15px;">
                        <div style="{st.session_state.col_format};
                        height: {"40px"};
                        width: {"95%"};">
                            <span style="font-size: 1.2em;">{(cost_now - cost_cheap) * 100:.2f}p </span>
                        </div>
                    </div>
                    """,
                unsafe_allow_html=True,
            )
        plot_kettle_timing()
    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
