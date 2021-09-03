import streamlit as st
from modberg import *

st.title("MODIFIED BERGGREN CALCULATOR")


# selection = st.selectbox(
#     "Select your age group",
#     ["10-17", "18-34", "35-44", "45-54", "55-64", "65-74", "75-79"],
# )

st.header("ENTER YOUR LOCATION HERE")
lat = st.number_input("latitude in Alaska", 51.229, 71.3526, 65.0)
lon = st.number_input("longitude in Alaska", -179.1506, -129.9795, -147.0)
is_frozen = st.radio("Is the soil frozen or unfrozen?", ("Frozen", "Unfrozen"))


st.header("ENTER YOUR PARAMETERS HERE")
wc_pct = st.slider("Soil water content (percent)", 1, 99, 15)
dry_ro = st.slider("soil dry density (pounds per cubic foot)", 1, 300, 100)
d = st.slider("length of freezing (or thawing) duration (days)", 1, 300, 100)
nFI = st.slider("surface freezing (or thawing) index (deg. F * days)", 1, 1000, 750)
k_avg = st.slider(
    "thermal conductivity of soil, average of frozen and unfrozen (BTU/hr • ft • °F)",
    0.01,
    0.99,
    0.75,
)

mat = get_mat_from_api(lat, lon)


mb = compute_modified_bergrenn(144, dry_ro, wc_pct, mat, 32, d, nFI, k_avg)

st.success(f"COMPUTED FROST DEPTH (FT.): {mb}")
