import streamlit as st
from modberg import *

st.title("MODIFIED BERGGREN FROST DEPTH CALCULATOR")
st.subheader("Alaska Climate Change Edition")

st.subheader("Retrieve the mean annual temperature (°F)")
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("latitude in Alaska", 51.229, 71.3526, 65.0)
with col2:
    lon = st.number_input("longitude in Alaska", -179.1506, -129.9795, -147.0)
period = st.radio(
    "era for which to retrieve the mean annual temperature",
    ("1910-2009", "2040-2070", "2070-2100"),
)
mat = get_mat_from_api(lat, lon, period)
mat_str = f"Mean Annual Temperature: {mat}°F"
st.subheader(mat_str)

col1, col2 = st.columns(2)
with col1:
    st.header("CLIMATE PARAMETERS")
    FI = st.slider("air freezing index (°F • days)", 100, 9000, 2500, step=10)
    n = st.slider("n factor converting air to surface freezing index", 0.1, 1.0, 0.75)
    d = st.slider("length of freezing duration (days)", 30, 300, 160)
    nFI = n * FI
    magt = mat  # may be assumed to be the mat...?

with col2:
    st.header("SOIL PARAMETERS")
    wc_pct = st.slider("water content (percent)", 1, 50, 15)
    dry_ro = st.slider("dry unit weight (pounds per cubic foot)", 20, 135, 100)
    k_avg = st.slider(
        "average thermal conductivity (BTU/(ft•hr•°F))",
        0.01,
        2.0,
        0.78,
    )

mb = compute_modified_bergrenn(
    dry_ro,
    wc_pct,
    mat,
    magt,
    d,
    nFI,
    k_avg,
)

st.success(f"COMPUTED FROST DEPTH (FT.): {mb}")
