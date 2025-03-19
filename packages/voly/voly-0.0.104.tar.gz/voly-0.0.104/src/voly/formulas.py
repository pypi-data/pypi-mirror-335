"""
Option pricing formulas and general calculations.
"""

import numpy as np
from scipy.stats import norm
from typing import Tuple, Dict, Union, List, Optional
from voly.utils.logger import catch_exception
from voly.models import SVIModel
from typing import Tuple


@catch_exception
def vectorize_inputs(func):
    """
    Decorator to vectorize Black-Scholes functions to handle both scalar and array inputs.
    """
    def wrapper(s, K, r, o, t, option_type='call'):
        # Check if inputs are scalar
        K_scalar = np.isscalar(K)
        o_scalar = np.isscalar(o)

        # If both inputs are scalar, use the original function directly
        if K_scalar and o_scalar:
            return func(s, K, r, o, t, option_type)

        # Use NumPy's vectorize to handle array inputs
        vectorized_func = np.vectorize(lambda K_val, o_val:
                                       func(s, K_val, r, o_val, t, option_type))

        # Call the vectorized function with the inputs
        return vectorized_func(K, o)

    return wrapper


@catch_exception
@vectorize_inputs
def d1(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    # option_type is ignored in this function but included for compatibility
    if o <= 0 or t <= 0:
        return np.nan
    return (np.log(s / K) + (r + o ** 2 / 2) * t) / (o * np.sqrt(t))

@catch_exception
@vectorize_inputs
def d2(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    # option_type is ignored in this function but included for compatibility
    if o <= 0 or t <= 0:
        return np.nan
    return d1(s, K, r, o, t, option_type) - o * np.sqrt(t)


@catch_exception
@vectorize_inputs
def bs(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        # Intrinsic value at expiry
        if option_type.lower() in ["call", "c"]:
            return max(0, s - K)
        else:
            return max(0, K - s)

    d1_val = d1(s, K, r, o, t)
    d2_val = d2(s, K, r, o, t)

    if option_type.lower() in ["call", "c"]:
        return s * norm.cdf(d1_val) - K * np.exp(-r * t) * norm.cdf(d2_val)
    else:  # put
        return K * np.exp(-r * t) * norm.cdf(-d2_val) - s * norm.cdf(-d1_val)


@catch_exception
@vectorize_inputs
def delta(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        # At expiry, delta is either 0 or 1 for call, 0 or -1 for put
        if option_type.lower() in ["call", "c"]:
            return 1.0 if s > K else 0.0
        else:
            return -1.0 if s < K else 0.0

    d1_val = d1(s, K, r, o, t)

    if option_type.lower() in ["call", "c"]:
        return norm.cdf(d1_val)
    else:  # put
        return norm.cdf(d1_val) - 1.0


@catch_exception
@vectorize_inputs
def gamma(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d1_val = d1(s, K, r, o, t, option_type)
    return norm.pdf(d1_val) / (s * o * np.sqrt(t))


@catch_exception
@vectorize_inputs
def vega(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d1_val = d1(s, K, r, o, t, option_type)
    return s * norm.pdf(d1_val) * np.sqrt(t) / 100  # Divided by 100 for 1% change


@catch_exception
@vectorize_inputs
def theta(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d1_val = d1(s, K, r, o, t, option_type)
    d2_val = d2(s, K, r, o, t, option_type)

    # First part of theta (same for both call and put)
    theta_part1 = -s * norm.pdf(d1_val) * o / (2 * np.sqrt(t))

    # Second part depends on option type
    if option_type.lower() in ["call", "c"]:
        theta_part2 = -r * K * np.exp(-r * t) * norm.cdf(d2_val)
    else:  # put
        theta_part2 = r * K * np.exp(-r * t) * norm.cdf(-d2_val)

    # Return theta per day (t is in years)
    return (theta_part1 + theta_part2) / 365.0


@catch_exception
@vectorize_inputs
def rho(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d2_val = d2(s, K, r, o, t, option_type)

    if option_type.lower() in ["call", "c"]:
        return K * t * np.exp(-r * t) * norm.cdf(d2_val) / 100
    else:  # put
        return -K * t * np.exp(-r * t) * norm.cdf(-d2_val) / 100


@catch_exception
@vectorize_inputs
def vanna(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d1_val = d1(s, K, r, o, t, option_type)
    d2_val = d2(s, K, r, o, t, option_type)

    return -norm.pdf(d1_val) * d2_val / o


@catch_exception
@vectorize_inputs
def volga(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d1_val = d1(s, K, r, o, t, option_type)
    d2_val = d2(s, K, r, o, t, option_type)

    return s * norm.pdf(d1_val) * np.sqrt(t) * d1_val * d2_val / o


@catch_exception
@vectorize_inputs
def charm(s: float, K: float, r: float, o: float, t: float, option_type: str = 'call') -> float:
    if o <= 0 or t <= 0:
        return 0.0

    d1_val = d1(s, K, r, o, t, option_type)
    d2_val = d2(s, K, r, o, t, option_type)

    # First term is the same for calls and puts
    term1 = -norm.pdf(d1_val) * d1_val / (2 * t)

    # Second term depends on option type
    if option_type.lower() in ["call", "c"]:
        term2 = -r * np.exp(-r * t) * norm.cdf(d2_val)
    else:  # put
        term2 = r * np.exp(-r * t) * norm.cdf(-d2_val)

    # Return charm per day (t is in years)
    return (term1 + term2) / 365.25


@catch_exception
@vectorize_inputs
def greeks(s: float, K: float, r: float, o: float, t: float,
           option_type: str = 'call') -> Dict[str, float]:
    return {
        'price': bs(s, K, r, o, t, option_type),
        'delta': delta(s, K, r, o, t, option_type),
        'gamma': gamma(s, K, r, o, t, option_type),
        'vega': vega(s, K, r, o, t, option_type),
        'theta': theta(s, K, r, o, t, option_type),
        'rho': rho(s, K, r, o, t, option_type),
        'vanna': vanna(s, K, r, o, t, option_type),
        'volga': volga(s, K, r, o, t, option_type),
        'charm': charm(s, K, r, o, t, option_type)
    }


@catch_exception
@vectorize_inputs
def iv(option_price: float, s: float, K: float, r: float, t: float,
       option_type: str = 'call', precision: float = 1e-8,
       max_iterations: int = 100) -> float:
    """
    Calculate implied volatility using Newton-Raphson method.

    Parameters:
    - option_price: MarKet price of the option
    - s: Underlying price
    - K: Strike price
    - r: RisK-free rate
    - t: Time to expiry in years
    - option_type: 'call' or 'put'
    - precision: Desired precision
    - max_iterations: Maximum number of iterations

    Returns:
    - Implied volatility
    """
    if t <= 0:
        return np.nan

    # Check if option price is within theoretical bounds
    if option_type.lower() in ["call", "c"]:
        intrinsic = max(0, s - K * np.exp(-r * t))
        if option_price < intrinsic:
            return np.nan  # Price below intrinsic value
        if option_price >= s:
            return np.inf  # Price exceeds underlying
    else:  # put
        intrinsic = max(0, K * np.exp(-r * t) - s)
        if option_price < intrinsic:
            return np.nan  # Price below intrinsic value
        if option_price >= K:
            return np.inf  # Price exceeds strike

    # Initial guess - Manaster and Koehler (1982) method
    o = np.sqrt(2 * np.pi / t) * option_price / s

    # Ensure initial guess is reasonable
    o = max(0.001, min(o, 5.0))

    for _ in range(max_iterations):
        # Calculate option price and vega with current volatility
        price = bs(s, K, r, o, t, option_type)
        v = vega(s, K, r, o, t, option_type)

        # Calculate price difference
        price_diff = price - option_price

        # Check if precision reached
        if abs(price_diff) < precision:
            return o

        # Avoid division by zero
        if abs(v) < 1e-10:
            # Change direction based on whether price is too high or too low
            o = o * 1.5 if price_diff < 0 else o * 0.5
        else:
            # Newton-Raphson update
            o = o - price_diff / (v * 100)  # Vega is for 1% change

        # Ensure volatility stays in reasonable bounds
        o = max(0.001, min(o, 5.0))

    # If we reach here, we didn't converge
    return np.nan


@catch_exception
def get_domain(domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
               s: float = None,
               r: float = None,
               o: np.ndarray = None,
               t: float = None,
               return_domain: str = 'log_moneyness') -> np.ndarray:
    """
    Compute the x-domain for a given return type (log-moneyness, moneyness, returns, strikes, or delta).

    Parameters:
    -----------
    domain_params : Tuple[float, float, int],
        Parameters for log-moneyness domain: (min_log_moneyness, max_log_moneyness, num_points).
        Default is (-1.5, 1.5, 1000).
    s : float, optional
        Spot price of the underlying asset. Required for 'strikes' and 'delta' domains.
    r : float, optional
        Risk-free interest rate. Required for 'delta' domain.
    o : np.ndarray, optional
        Array of implied volatilities. Required for 'delta' domain.
    t : float, optional
        Time to maturity in years. Required for 'delta' domain.
    return_domain : str, optional
        The desired domain to return. Options are 'log_moneyness', 'moneyness', 'returns' 'strikes', or 'delta'.
        Default is 'log_moneyness'.

    Returns:
    --------
    np.ndarray
        The x-domain array corresponding to the specified return_domain.

    Raises:
    -------
    ValueError
        If required parameters are missing for the specified return_domain.
    """

    # Extract log-moneyness parameters and generate array
    LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])

    # Handle different return domains
    if return_domain == 'log_moneyness':
        return LM

    elif return_domain == 'moneyness':
        return np.exp(LM)

    elif return_domain == 'returns':
        return np.exp(LM) - 1

    elif return_domain == 'strikes':
        if s is None:
            raise ValueError("Spot price 's' is required for return_domain='strikes'.")
        return s / np.exp(LM)

    elif return_domain == 'delta':
        # Check for required parameters
        required_params = {'s': s, 'r': r, 'o': o, 't': t}
        missing_params = [param for param, value in required_params.items() if value is None]
        if missing_params:
            raise ValueError(f"The following parameters are required for return_domain='delta': {missing_params}")

        if len(o) != len(LM):
            raise ValueError(
                f"'o' must have the same length as the log-moneyness array ({len(LM)})."
                f"Length 'o'={len(o)}, length 'LM'={len(LM)}")

        # Compute strikes
        K = s / np.exp(LM)

        # Compute deltas
        D = delta(s, K, r, o, t, 'call')
        return D

    else:
        raise ValueError(
            f"Invalid return_domain: {return_domain}. Must be one of ['log_moneyness', 'moneyness', 'returns', 'striKes', 'delta'].")
