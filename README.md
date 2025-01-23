# agile-home-dashboard

A Streamlit app for Octopus energy agile data analytics for residential applications.
Useful for household application cost predictions, such as timing usage of high-energy
devices (kettle, dishwasher, laundry machine).

## Installation
Currently, this module is installable via navigating to the root directory and running the following:

```bash
pip install -e .
```

#### Developer
Install with optional developer dependencies:
```bash
pip install -e '.[dev]'
```

## Demo
This web app is currently deployed on the [Streamlit Community Cloud](https://agile-home-dashboard.streamlit.app/).

## Usage
For a local development server, run the below streamlit command:

```bash
streamlit run Home.py
```

which creates a local server and hosts the site at `localhost:8501`.
