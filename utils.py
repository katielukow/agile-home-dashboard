import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import minimize

# Defaults
cp = 4.19298  # mean value between 0C - 100C

# Kettle observations
kettle_timing = pd.DataFrame(
    {
        "Volume [mL]": [600, 550, 350, 1100, 637, 804, 600, 570, 500, 830, 627],
        "Time [s]": [137, 135, 98, 237, 148, 178, 150, 125, 130, 205, 153],
        "Starting Temp [C]": [18, 18, 12, 12, 15, 11, 16, 13, 12, 10, 15],
    }
)


def kettle_energy(init_temp, cp, m, kappa):
    """First-principles kettle model"""
    return (100.0 - init_temp) * cp * m * kappa


@st.cache_data
def fit_kettle_efficiency():
    """
    Identifies kettle efficiency parameter `kappa`

    Returns
    -------
    kappa : float
    """
    temperature = kettle_timing["Starting Temp [C]"].mean()
    volume_ml = kettle_timing["Volume [mL]"].to_numpy() / 1000
    time_s = kettle_timing["Time [s]"].to_numpy()

    def kettle_fit(kappa):
        W = kettle_energy(temperature, cp, volume_ml, kappa)
        residuals = W / 2.1 - time_s
        return np.sum(residuals**2)

    result = minimize(kettle_fit, x0=np.array([1.0]))
    return result.x[0]
