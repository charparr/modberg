import streamlit as st
from modberg import *

st.title("MODIFIED BERGGREN FROST DEPTH CALCULATOR")

st.header("ENTER LOCATION AND TIME PERIOD TO RETREIVE MEAN ANNUAL TEMPERATURE")
lat = st.number_input("latitude in Alaska", 51.229, 71.3526, 65.0)
lon = st.number_input("longitude in Alaska", -179.1506, -129.9795, -147.0)
period = st.radio(
    "era for which to retreive the mean annual temperature",
    ("1910-2009", "2040-2070", "2070-2100"),
)

st.header("ENTER SOIL PARAMETERS")
is_frozen = st.radio(
    "Is the soil frozen or unfrozen? This information is used to compute the average specfic heat for the soil by modifing a constant.",
    ("Frozen", "Unfrozen", "Uncertain - use an average constant value for most soils."),
)
wc_pct = st.slider("Soil water content (percent)", 1, 50, 15)
dry_ro = st.slider("soil dry density (pounds per cubic foot)", 50, 250, 100)
d = st.slider("length of freezing duration (days)", 1, 365, 100)
nFI = st.slider("surface freezing index (°F • days)", 100, 9000, 750)
k_avg = st.slider(
    "thermal conductivity of soil, average of frozen and unfrozen (BTU/hr • ft • °F)",
    0.01,
    0.99,
    0.75,
)

mat = get_mat_from_api(lat, lon, period)

mb = compute_modified_bergrenn(dry_ro, wc_pct, is_frozen, mat, 32, d, nFI, k_avg, 0.17)

st.success(f"COMPUTED FROST DEPTH (FT.): {mb}")
