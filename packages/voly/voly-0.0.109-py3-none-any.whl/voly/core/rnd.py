"""
This module handles calculating risk-neutral densities from
fitted volatility models and converting to probability functions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError
from voly.models import SVIModel
from voly.formulas import bs, d1, d2, get_domain
from scipy import stats


# Breeden-Litzenberger Method
@catch_exception
def breeden(domain_params, s, r, o, t, return_domain):
    LM = get_domain(domain_params, s, r, o, t, 'log_moneyness')
    M = get_domain(domain_params, s, r, o, t, 'moneyness')
    R = get_domain(domain_params, s, r, o, t, 'returns')
    K = get_domain(domain_params, s, r, o, t, 'strikes')
    D = get_domain(domain_params, s, r, o, t, 'delta')

    c = bs(s, K, r, o, t, option_type='call')
    c1 = np.gradient(c, K)
    c2 = np.gradient(c1, K)

    rnd_k = np.maximum(np.exp(r * t) * c2, 0)
    rnd_lm = rnd_k * K

    dx = LM[1] - LM[0]
    total_area = np.sum(rnd_lm * dx)
    pdf_lm = rnd_lm / total_area
    pdf_k = pdf_lm / K
    pdf_m = pdf_k * s
    pdf_r = pdf_lm / (1 + R)

    pdf_d1 = stats.norm.pdf(d1(s, K, r, o, t, option_type='call'))
    dd_dK = pdf_d1 / (o * np.sqrt(t) * K)
    pdf_d = pdf_k / dd_dK

    cdf = np.cumsum(pdf_lm) * dx
    cdf = cdf / cdf[-1]

    if return_domain == 'log_moneyness':
        x = LM
        pdf = pdf_lm
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'moneyness':
        x = M
        pdf = pdf_m
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'returns':
        x = R
        pdf = pdf_r
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'strikes':
        x = K
        pdf = pdf_k
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'delta':
        sort_idx = np.argsort(D)
        x = D[sort_idx]
        pdf = pdf_d[sort_idx]
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments


# Rookley's Method
@catch_exception
def rookley(domain_params, s, r, o, t, return_domain):
    LM = get_domain(domain_params, s, r, o, t, 'log_moneyness')
    M = get_domain(domain_params, s, r, o, t, 'moneyness')
    R = get_domain(domain_params, s, r, o, t, 'returns')
    K = get_domain(domain_params, s, r, o, t, 'strikes')
    D = get_domain(domain_params, s, r, o, t, 'delta')

    o1 = np.gradient(o, M)
    o2 = np.gradient(o1, M)

    st = np.sqrt(t)
    rt = r * t
    ert = np.exp(rt)

    n_d1 = (np.log(M) + (r + 1 / 2 * o ** 2) * t) / (o * st)
    n_d2 = n_d1 - o * st

    del_d1_M = 1 / (M * o * st)
    del_d2_M = del_d1_M
    del_d1_o = -(np.log(M) + rt) / (o ** 2 * st) + st / 2
    del_d2_o = -(np.log(M) + rt) / (o ** 2 * st) - st / 2

    d_d1_M = del_d1_M + del_d1_o * o1
    d_d2_M = del_d2_M + del_d2_o * o1

    dd_d1_M = (
            -(1 / (M * o * st)) * (1 / M + o1 / o)
            + o2 * (st / 2 - (np.log(M) + rt) / (o ** 2 * st))
            + o1 * (2 * o1 * (np.log(M) + rt) / (o ** 3 * st) - 1 / (M * o ** 2 * st))
    )
    dd_d2_M = (
            -(1 / (M * o * st)) * (1 / M + o1 / o)
            - o2 * (st / 2 + (np.log(M) + rt) / (o ** 2 * st))
            + o1 * (2 * o1 * (np.log(M) + rt) / (o ** 3 * st) - 1 / (M * o ** 2 * st))
    )

    d_c_M = stats.norm.pdf(n_d1) * d_d1_M - 1 / ert * stats.norm.pdf(n_d2) / M * d_d2_M + 1 / ert * stats.norm.cdf(n_d2) / (
                M ** 2)
    dd_c_M = (
            stats.norm.pdf(n_d1) * (dd_d1_M - n_d1 * d_d1_M ** 2)
            - stats.norm.pdf(n_d2) / (ert * M) * (dd_d2_M - 2 / M * d_d2_M - n_d2 * d_d2_M ** 2)
            - 2 * stats.norm.cdf(n_d2) / (ert * M ** 3)
    )

    dd_c_K = dd_c_M * (M / K) ** 2 + 2 * d_c_M * (M / K ** 2)

    rnd_k = np.maximum(ert * s * dd_c_K, 0)
    rnd_lm = rnd_k * K

    dx = LM[1] - LM[0]
    total_area = np.sum(rnd_lm * dx)
    pdf_lm = rnd_lm / total_area
    pdf_k = pdf_lm / K
    pdf_m = pdf_k * s
    pdf_r = pdf_lm / (1 + R)

    pdf_d1 = stats.norm.pdf(d1(s, K, r, o, t, option_type='call'))
    dd_dK = pdf_d1 / (o * np.sqrt(t) * K)
    pdf_d = pdf_k / dd_dK

    cdf = np.cumsum(pdf_lm) * dx
    cdf = cdf / cdf[-1]

    if return_domain == 'log_moneyness':
        x = LM
        pdf = pdf_lm
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'moneyness':
        x = M
        pdf = pdf_m
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'returns':
        x = R
        pdf = pdf_r
        moments = get_all_moments(x, pdf)
        return pdf, cdf, moments
    elif return_domain == 'strikes':
        x = K
        pdf = pdf_k
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments
    elif return_domain == 'delta':
        sort_idx = np.argsort(D)
        x = D[sort_idx]
        pdf = pdf_d[sort_idx]
        moments = get_all_moments(x, pdf)
        return pdf, cdf, x, moments


@catch_exception
def get_all_moments(x, pdf):
    mean = np.trapz(x * pdf, x)  # E[X]
    median = x[np.searchsorted(np.cumsum(pdf * np.diff(x, prepend=x[0])), 0.5)]  # Median (50th percentile)
    mode = x[np.argmax(pdf)]  # Mode (peak of PDF)
    variance = np.trapz((x - mean) ** 2 * pdf, x)  # Var[X] = E[(X - μ)^2]
    std_dev = np.sqrt(variance)  # Standard deviation
    skewness = np.trapz((x - mean) ** 3 * pdf, x) / std_dev ** 3  # Skewness
    kurtosis = np.trapz((x - mean) ** 4 * pdf, x) / std_dev ** 4  # Kurtosis
    excess_kurtosis = kurtosis - 3  # Excess kurtosis (relative to normal dist.)
    q25 = x[np.searchsorted(np.cumsum(pdf * np.diff(x, prepend=x[0])), 0.25)]  # 25th percentile
    q75 = x[np.searchsorted(np.cumsum(pdf * np.diff(x, prepend=x[0])), 0.75)]  # 75th percentile
    iqr = q75 - q25  # Inter-quartile range
    entropy = -np.trapz(pdf * np.log(pdf + 1e-10), x)  # Differential entropy (avoid log(0))

    # Full Z-score areas
    dx = np.diff(x, prepend=x[0])
    z = (x - mean) / std_dev
    o1p = np.sum(pdf[(z > 0) & (z < 1)] * dx[(z > 0) & (z < 1)])
    o2p = np.sum(pdf[(z >= 1) & (z < 2)] * dx[(z >= 1) & (z < 2)])
    o3p = np.sum(pdf[(z >= 2) & (z < 3)] * dx[(z >= 2) & (z < 3)])
    o4p = np.sum(pdf[z >= 3] * dx[z >= 3])
    o1n = np.sum(pdf[(z < 0) & (z > -1)] * dx[(z < 0) & (z > -1)])
    o2n = np.sum(pdf[(z <= -1) & (z > -2)] * dx[(z <= -1) & (z > -2)])
    o3n = np.sum(pdf[(z <= -2) & (z > -3)] * dx[(z <= -2) & (z > -3)])
    o4n = np.sum(pdf[z <= -3] * dx[z <= -3])

    moments = {
        'mean': mean,
        'median': median,
        'mode': mode,
        'variance': variance,
        'std_dev': std_dev,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'excess_kurtosis': excess_kurtosis,
        'q25': q25,
        'q75': q75,
        'iqr': iqr,
        'entropy': entropy,
        'o1p': o1p,
        'o2p': o2p,
        'o3p': o3p,
        'o4p': o4p,
        'o1n': o1n,
        'o2n': o2n,
        'o3n': o3n,
        'o4n': o4n
    }
    return moments


@catch_exception
def get_rnd_surface(model_results: pd.DataFrame,
                    domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                    return_domain: str = 'log_moneyness',
                    method: str = 'rookley') -> Tuple[
    Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray], pd.DataFrame]:
    """
    Generate RND surface from vol smile parameters.

    Works with both regular fit_results and interpolated_results dataframes.

    Parameters:
    - model_results: DataFrame from fit_model() or interpolate_model(). Maturity names or DTM as Index
    - domain_params: Tuple of (min, max, num_points) for the x-domain grid
    - return_domain: Domain for x-axis values ('log_moneyness', 'moneyness', 'returns', 'strikes', 'delta')
    - method: 'rookley' or 'breeden'

    Returns:
    - Tuple containing:
      - pdf_surface: Dictionary mapping maturity/dtm names to PDF arrays of their requested domain
      - cdf_surface: Dictionary mapping maturity/dtm names to CDF arrays
      - x_surface: Dictionary mapping maturity/dtm names to requested x domain arrays
      - moments_df: DataFrame with moments of the distributions using model_results index
    """
    # Check if required columns are present
    required_columns = ['s', 'a', 'b', 'sigma', 'm', 'rho', 't', 'r']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    pdf_surface = {}
    cdf_surface = {}
    x_surface = {}
    all_moments = {}

    # Process each maturity/dtm
    for i in model_results.index:
        # Calculate SVI total implied variance and convert to IV
        params = [
            model_results.loc[i, 'a'],
            model_results.loc[i, 'b'],
            model_results.loc[i, 'sigma'],
            model_results.loc[i, 'rho'],
            model_results.loc[i, 'm']
        ]
        s = model_results.loc[i, 's']
        r = model_results.loc[i, 'r']
        t = model_results.loc[i, 't']

        # Calculate implied volatility
        LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])
        w = np.array([SVIModel.svi(x, *params) for x in LM])
        o = np.sqrt(w / t)

        if method == 'rookley':
            pdf, cdf, x, moments = rookley(domain_params, s, r, o, t, return_domain)
        else:
            pdf, cdf, x, moments = breeden(domain_params, s, r, o, t, return_domain)

        pdf_surface[i] = pdf
        cdf_surface[i] = cdf
        x_surface[i] = x
        all_moments[i] = moments

    # Create a DataFrame with moments using the same index as model_results
    moments = pd.DataFrame(all_moments).T

    # Ensure the index matches the model_results index
    moments.index = model_results.index

    return pdf_surface, cdf_surface, x_surface, moments
