import numpy as np
import requests
import pandas as pd


def compute_volumetric_latent_heat_of_fusion(lhof_h2o, dry_ro, wc_pct):
    """Compute the amount of heat required to melt all the ice (or freeze all the pore water) in a unit volume of soil or rock.
    Args:
        lhof_h2o: gravimetric latent heat of fusion of water (btus per lb) (144 in most cases)
        dry_ro: soil dry density (pounds per cubic foot)
        wc_pct: percent water content (percent)

    Returns:
        L: volumetric latent heat of fusion (btus per cubic foot)
    """
    L = lhof_h2o * dry_ro * (wc_pct / 100)
    return L


def compute_average_volumetric_specific_heat(c, dry_ro, wc_pct, **kwargs):
    """Compute the quantity of heat required to change the temperature of a unit volume by one degree F.
    Args:
        c: specific heat of soil solids (0.17 for most soils)
        dry_ro: soil dry density (pounds per cubic foot)
        wc_pct: Percent water content
        is_frozen: "frozen" or "unfrozen" soils

    Returns:
        c: volumetric specific heat (btus per cubic foot) * deg. F
    """
    is_frozen = kwargs.get("is_frozen", None)

    di = {"frozen": 0.5, "unfrozen": 1.0}
    try:
        frozen_mod = di[is_frozen]
    except:
        frozen_mod = 0.75

    c = dry_ro * (c + (frozen_mod * (wc_pct / 100)))
    return round(c, 2)


def compute_thermal_ratio(mat, t_freeze, d, nFI):
    """Compute the the thermal ratio.
    The thermal ratio is a function of the initial temperature differential and the average temperature differential.
    Args:
        mat: mean annual ground or surface temperature (deg. F)
        t_freeze: freezing temperature (deg. F) (32 in most cases)
        d: length length of freezing or thawing duration.
        nFI: surface freezing (or thawing) index

    Returns:
        thermal_ratio: dimensionless
    """
    thermal_ratio = (abs(mat - t_freeze) * d) / nFI
    return round(thermal_ratio, 2)


def compute_fusion_parameter(nFI, d, cavg, L):
    """Compute the fusion parameter.

    Args:
        d: length length of freezing or thawing duration (days)
        nFI: surface freezing (or thawing) index
        cavg: volumetric specific heat ( (btus per cubic foot) * deg. F )
        L: volumetric latent heat of fusion (btus per cubic foot)

    Returns:
        mu: the fusion parameter
    """
    mu = (nFI / d) * (cavg / L)
    return round(mu, 2)


def compute_coeff(mu, thermal_ratio):
    lc1 = 1.0 / (np.sqrt(1 + (mu * (thermal_ratio + 0.5))))
    lc2 = 0.707 / (np.sqrt(1 + (mu * (thermal_ratio + 0.5))))
    return round(np.mean([lc1, lc2]), 2)


def compute_depth_of_freezing(coeff, mat, kavg, nFI, L):
    x = coeff * (np.sqrt((mat * kavg * nFI) / L))
    return x


def compute_modified_bergrenn(lhof_h2o, dry_ro, wc_pct, mat, t_freeze, d, nFI, k_avg):

    """
    Args:
    lhof_h2o: gravimetric latent heat of fusion of water (btus per lb)
    dry_ro: soil dry density (pounds per cubic foot)
    wc_pct: water content (percent)
    mat: mean annual ground or surface temperature (deg. F)
    t_freeze: freezing temperature (deg. F)
    d: length of freezing (or thawing) duration (days)
    nFI: surface freezing (or thawing) index (deg. F * days)
    k_avg: thermal conductivity of soil, average of frozen and unfrozen (BTU/hr • ft • °F)
    """

    L = compute_volumetric_latent_heat_of_fusion(lhof_h2o, dry_ro, wc_pct)
    c_avg = 28.2
    thermal_ratio = compute_thermal_ratio(mat, t_freeze, d, nFI)
    mu = compute_fusion_parameter(nFI, d, c_avg, L)
    lambda_coeff = 0.74
    x_freeze = compute_depth_of_freezing(lambda_coeff, mat, k_avg, nFI, L)
    return round(x_freeze, 2)


def get_mat_from_api(lat, lon):

    api_url = f"http://snap-data.io/iem/point/{lat}/{lon}"
    resp = requests.get(api_url).json()["2040_2070"]
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
