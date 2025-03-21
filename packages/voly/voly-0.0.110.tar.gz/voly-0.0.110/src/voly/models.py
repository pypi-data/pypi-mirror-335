"""
Volatility models for the Voly package.
"""

import numpy as np
from typing import Tuple, Dict, List, Optional, Union

class SVIModel:
    """
    Stochastic Volatility Inspired (SVI) model.

    This class provides methods for calculating implied volatility using the
    SVI parameterization, as well as its derivatives and related functions.
    """

    # Default initial parameters and bounds
    DEFAULT_INITIAL_PARAMS = [0.04, 0.1, 0.2, -0.5, 0.01]
    DEFAULT_PARAM_BOUNDS = ([-np.inf, 0, 0, -1, -np.inf], [np.inf, np.inf, np.inf, 1, np.inf])

    # Parameter names for reference
    PARAM_NAMES = ['a', 'b', 'sigma', 'rho', 'm']
    JW_PARAM_NAMES = ['nu', 'psi', 'p', 'c', 'nu_tilde']

    # Parameter descriptions for documentation
    PARAM_DESCRIPTIONS = {
        'a': 'Base level of total implied variance',
        'b': 'Volatility skewness/smile modulation (controls wing slopes)',
        'sigma': 'Convexity control of the volatility smile (reduces ATM curvature)',
        'rho': 'Skewness/slope of the volatility smile (-1 to 1, rotates smile)',
        'm': 'Horizontal shift of the smile peak',
        'nu': 'ATM variance (level of ATM volatility)',
        'psi': 'ATM volatility skew (affects the gradient of the curve at ATM point)',
        'p': 'Slope of put wing (left side of curve)',
        'c': 'Slope of call wing (right side of curve)',
        'nu_tilde': 'Minimum implied total variance',
    }

    @staticmethod
    def svi(LM: float, a: float, b: float, sigma: float, rho: float, m: float) -> float:
        return a + b * (rho * (LM - m) + np.sqrt((LM - m) ** 2 + sigma ** 2))

    @staticmethod
    def svi_d(LM: float, a: float, b: float, sigma: float, rho: float, m: float) -> float:
        return b * (rho + ((LM - m) / np.sqrt((LM - m) ** 2 + sigma ** 2)))

    @staticmethod
    def svi_dd(LM: float, a: float, b: float, sigma: float, rho: float, m: float) -> float:
        return b * LM ** 2 / ((LM - m) ** 2 + sigma ** 2) ** 1.5

    @staticmethod
    def svi_min_strike(sigma: float, rho: float, m: float) -> float:
        return m - ((sigma * rho) / np.sqrt(1 - rho ** 2))

    @staticmethod
    def raw_to_jw_params(a: float, b: float, sigma: float, rho: float, m: float, t: float) -> Tuple[float, float, float, float, float]:
        nu = (a + b * ((-rho) * m + np.sqrt(m ** 2 + sigma ** 2))) / t
        psi = (1 / np.sqrt(nu * t)) * (b / 2) * (rho - (m / np.sqrt(m ** 2 + sigma ** 2)))
        p = (1 / np.sqrt(nu * t)) * b * (1 - rho)
        c = (1 / np.sqrt(nu * t)) * b * (1 + rho)
        nu_tilde = (1 / t) * (a + b * sigma * np.sqrt(1 - rho ** 2))
        return nu, psi, p, c, nu_tilde

    @staticmethod
    def jw_to_raw_params(nu: float, psi: float, p: float, c: float, nu_tilde: float, t: float) -> Tuple[float, float, float, float, float]:
        w = nu * t
        b = (c + p) / 2
        rho = (c - p) / (c + p)
        beta = rho - ((2 * w * psi) / b)
        alpha = np.sign(beta) * (np.sqrt((1 / (beta ** 2)) - 1))
        m = (((nu ** 2) - (nu_tilde ** 2)) * t) / (
                b * ((-rho) + (np.sign(alpha) * np.sqrt(1 + alpha ** 2)) - (alpha * np.sqrt(1 - rho ** 2))))
        sigma = alpha * m
        a = ((nu_tilde ** 2) * t) - (b * sigma * np.sqrt(1 - rho ** 2))
        return a, b, sigma, rho, m


# Models dictionary for easy access
MODELS = {
    'svi': SVIModel,
}
