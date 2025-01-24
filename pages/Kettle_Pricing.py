import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from agile_home_dashboard import get_current_time, get_current_cost


def calculate_kettle_cost(current_price, next_price, run_time, power):
    cost_now = ((run_time / 3600) * current_price * power) / 100
    cost_next = ((run_time / 3600) * next_price * power) / 100

    return (cost_now, cost_next)


# Function to display kettle costs
def display_kettle_costs(
    current_price, next_price, cost_now, cost_next, current_cost_row, next_cost_row
):
    st.markdown(
        """
        <div style="text-align: center;">
            <strong>Current Energy Cost</strong><br>
            <span style="font-size: 1.5em; color: black;">{:.4f} p/kWh</span>
        </div>
        """.format(current_price),
        unsafe_allow_html=True,
    )

    # Next energy cost
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px;">
            <strong>Next Energy Cost</strong><br>
            <span style="font-size: 1.5em; color: black;">{:.4f} p/kWh</span>
        </div>
        """.format(next_price),
        unsafe_allow_html=True,
    )

    # Kettle current cost
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px;">
            <strong>Kettle Current Cost</strong><br>
            <span style="font-size: 1.2em; color: black;">£{:.4f}</span><br>
            <small>Valid until {}</small>
        </div>
        """.format(cost_now, current_cost_row.iloc[0]["valid_to"].strftime("%H:%M")),
        unsafe_allow_html=True,
    )

    # Kettle next cost with color coding
    color = "green" if cost_next <= cost_now else "red"
    if next_price == 0:
        color = "black"
        st.markdown(
            """
        <div style="text-align: center; margin-top: 30px;">
            <strong>Kettle Next Cost</strong><br>
            <span style="font-size: 1.2em; color: {};">£{:.4f}</span><br>
            <small>The next kettle cost is not available</small>
        </div>
        """.format(
                color,
                cost_next,
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 30px;">
                <strong>Kettle Next Cost</strong><br>
                <span style="font-size: 1.2em; color: {};">£{:.4f}</span><br>
                <small>From {} to {}</small>
            </div>
            """.format(
                color,
                cost_next,
                next_cost_row["valid_from"].strftime("%H:%M"),
                next_cost_row["valid_to"].strftime("%H:%M"),
            ),
            unsafe_allow_html=True,
        )


# Function to plot kettle timing
def plot_kettle_timing():
    kettle_timing = pd.DataFrame(
        {
            "Volume [mL]": [600, 550, 350, 1100, 637, 804, 600, 570, 500],
            "Time [s]": [137, 135, 98, 237, 148, 178, 150, 125, 130],
            "Starting Temp [C]": [18, 18, 12, 12, 15, 11, 16, 13, 12],
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
        plot_bgcolor=st.session_state.bg_color,  # Set the plot area background to white
        font=dict(
            color=st.session_state.font,  # Set text color
            size=14,  # Optional: Adjust text size for better visibility
        ),
        title=dict(
            text="Kettle Timing Plot",  # Add a title
            font=dict(color=st.session_state.font),  # Set title text color
        ),
        xaxis=dict(
            title="Time",  # Label the x-axis
            title_font=dict(color=st.session_state.font),  # X-axis title color
            tickfont=dict(color=st.session_state.font),  # X-axis tick color
        ),
        yaxis=dict(
            title="Price [p/kWh]",  # Label the y-axis
            title_font=dict(color=st.session_state.font),  # Y-axis title color
            tickfont=dict(color=st.session_state.font),  # Y-axis tick color
        ),
    )
    st.plotly_chart(fig)


# Main application logic
def main():
    st.title("Kettle Pricing on Octopus Agile")
    if st.session_state.df is not None:
        st.write("How much does the kettle cost right now?")

        run_time = st.number_input(
            "Kettle run time [s]:", min_value=0, max_value=2000, value=137
        )
        power = st.number_input(
            "Kettle power [kW]:", min_value=0.0, max_value=1e8, value=2.1
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
        # Plot kettle timing
        plot_kettle_timing()
    else:
        st.error("API key not found.")


# Run the application
if __name__ == "__main__":
    main()
