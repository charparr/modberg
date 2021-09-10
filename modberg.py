import numpy as np
import requests
import pandas as pd

"""
The design of pavement structures in cold climates must account for the changes in soil properties due to the influence of freezing and thawing cycles. The calculation of frost depth is a fundamental step during the design and evaluation of pavement structures by the U.S. Department of Defense (DoD). The DoD uses the modified Berggren (ModBerg) equation to compute the frost penetration depth.
The Unified Facilities Criteria (UFC) 3-130-06 includes a methodology to manually compute the frost depth. The Pavement-Transportation Computer Assisted Structural Engineering (PCASE) software incorporates a more comprehensive numerical solution of the ModBerg equation, which in some instances predicts values slightly different than the manual solution described in the UFC.
A module implementing the Modified Berggren equation to compute frost depth below the surface using climate projections for the mean annual temperature input.
Assumptions:
    A single layer of homogenous soil.
"""


def compute_volumetric_latent_heat_of_fusion(dry_ro, wc_pct):
    """Compute the amount of heat required to melt all the ice (or freeze all the pore water) in a unit volume of soil or rock.
    Args:
        lhof_h2o: gravimetric latent heat of fusion of water (144 BTUs per lb)
        dry_ro: soil dry density (lbs per cubic foot)
        wc_pct: percent water content (percent)

    Returns:
        L: volumetric latent heat of fusion (BTUs per cubic foot)
    """
    L = 144 * dry_ro * (wc_pct / 100)
    return L


def compute_average_volumetric_specific_heat(c_soil, dry_ro, wc_pct, **kwargs):
    """Compute the quantity of heat required to change the temperature of a unit volume by one degree F.
    Args:
        c_soil: specific heat of soil solids (0.17 for most soils)
        dry_ro: soil dry density (lbs per cubic foot)
        wc_pct: percent water content (percent)
        is_frozen: "frozen" or "unfrozen" soil condition

    Returns:
        c: volumetric specific heat (Btus per cubic foot) * °F
    """
    is_frozen = kwargs.get("is_frozen", None)
    di = {"frozen": 0.5, "unfrozen": 1.0}
    try:
        frozen_mod = di[is_frozen.lower()]
    except:
        frozen_mod = 0.75
    c = dry_ro * (c_soil + (frozen_mod * (wc_pct / 100)))
    return round(c, 2)


def compute_thermal_ratio(mat, t_freeze, d, nFI):
    """Compute the the thermal ratio.
    The thermal ratio is a function of the initial temperature differential and the average temperature differential.
    Args:
        mat: mean annual ground or surface temperature (°F)
        t_freeze: freezing temperature (32 °F)
        d: length of freezing duration (days)
        nFI: surface freezing index (°F • days)

    Returns:
        thermal_ratio: dimensionless
    """
    v_s = nFI / d
    v_o = mat - t_freeze
    thermal_ratio = v_o / v_s
    return round(thermal_ratio, 3)


def compute_fusion_parameter(nFI, d, c, L):
    """Compute the fusion parameter.

    Args:
        nFI: surface freezing index (°F • days)
        d: length of freezing or thawing duration (days)
        c: volumetric specific heat ((BTUs per cubic foot) * °F)
        L: volumetric latent heat of fusion (BTUs per cubic foot)

    Returns:
        mu: (dimensionless)
    """
    mu = (nFI / d) * (c / L)
    return round(mu, 3)


def compute_coeff(mu, thermal_ratio):
    """Compute the Lambda coeffcient (dimensionless).
    Citation: H. P. Aldrich and H. M. Paynter, “Analytical Studies of Freezing and Thawing of Soils,” Arctic Construction and Frost Effects Laboratory, Corps of Engineers, U.S. Army, Boston, MA, First Interim Technical Report 42, Jun. 1953.

    lc1 is likely to overestimate frost depth for high latitudes
    lc2 is likely to underestimate frost depth for high latitudes
    lc_mean is a middle ground

    Args:
        mu: the fusion parameter (dimensionless)
        thermal_ratio (dimensionless)

    Returns
        lc1: a lambda coeffcient value (dimensionless).
    """
    lc1 = 1.0 / (np.sqrt(1 + (mu * (thermal_ratio + 0.5))))
    lc2 = 0.707 / (np.sqrt(1 + (mu * (thermal_ratio + 0.5))))
    lc_mean = round(np.mean([lc1, lc2]), 2)
    return round(lc1, 2)


def compute_depth_of_freezing(coeff, mat, k_avg, nFI, L):
    """Compute the depth to which 32 °F temperatures will penetrate into the soil mass.

    Args:
        coeff: the lambda coeffcient (dimensionless)
        mat: mean annual temperature (°F)
        k_avg: thermal conductivity of soil, average of frozen and unfrozen (BTU/hr • ft • °F)
        nFI: surface freezing index (°F • days)
        L: volumetric latent heat of fusion (BTUs per cubic foot)
    Returns:
        x: frost depth (feet)
    """
    x = coeff * np.sqrt((48 * k_avg * nFI) / L)
    return round(x, 2)


def compute_modified_bergrenn(
    dry_ro, wc_pct, is_frozen, mat, t_freeze, d, nFI, k_avg, c_soil=0.17
):
    """
    Args:
    lhof_h2o: gravimetric latent heat of fusion of water (BTUs per lb)
    dry_ro: soil dry density (lbs per cubic foot)
    wc_pct: water content (percent)
    mat: mean annual temperature (°F)
    t_freeze: freezing temperature (°F)
    d: length of freezing duration (days)
    nFI: surface freezing index (°F • days)
    k_avg: thermal conductivity of soil, average of frozen and unfrozen (BTU/hr • ft • °F)
    """

    L = compute_volumetric_latent_heat_of_fusion(dry_ro, wc_pct)
    c = compute_average_volumetric_specific_heat(
        c_soil, dry_ro, wc_pct, is_frozen=is_frozen
    )
    thermal_ratio = compute_thermal_ratio(mat, t_freeze, d, nFI)
    mu = compute_fusion_parameter(nFI, d, c, L)
    lambda_coeff = compute_coeff(mu, thermal_ratio)
    frost_depth = compute_depth_of_freezing(lambda_coeff, mat, k_avg, nFI, L)
    return frost_depth


def get_mat_from_api(lat, lon, period):
    """Query the SNAP Data API for mean annual temperature using the IEM Webapp Endpoint."""

    time_di = {
        "1910-2009": "1910-2009",
        "2040-2070": "2040_2070",
        "2070-2100": "2070_2100",
    }
    api_url = f"http://snap-data.io/iem/point/{lat}/{lon}"
    resp = requests.get(api_url).json()[time_di[period]]
    df = pd.json_normalize(resp, sep="_")
    di = df.to_dict()
    all_tas = []
    for k in di.keys():
        if "tas" in k:
            all_tas.append(di[k][0])
        else:
            pass
    iem_mat_degC = np.mean(all_tas)
    iem_mat_degF = (iem_mat_degC * 1.8) + 32
    return iem_mat_degF
