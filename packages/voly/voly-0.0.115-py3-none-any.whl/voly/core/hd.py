"""
This module handles calculating historical densities from
time series of prices and converting them to implied volatility smiles.
"""

import ccxt
import pandas as pd
import datetime as dt
from scipy import stats
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError
from voly.core.rnd import get_all_moments
from voly.formulas import iv
from voly.models import SVIModel
from voly.core.fit import fit_model


@catch_exception
def get_historical_data(currency, lookback_days, granularity, exchange_name):
    """
    Fetch historical OHLCV data for a cryptocurrency.

    Parameters:
    ----------
    currency : str
        The cryptocurrency to fetch data for (e.g., 'BTC', 'ETH').
    lookback_days : str
        The lookback period in days, formatted as '90d', '30d', etc.
    granularity : str
        The time interval for data points (e.g., '15m', '1h', '1d').
    exchange_name : str
        The exchange to fetch data from (default: 'binance').

    Returns:
    -------
    df_hist : pandas.DataFrame containing the historical price data with OHLCV columns.
    """

    try:
        # Get the exchange class from ccxt
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class({'enableRateLimit': True})
    except (AttributeError, TypeError):
        raise VolyError(f"Exchange '{exchange_name}' not found in ccxt. Please check the exchange name.")

    # Form the trading pair symbol
    symbol = currency + '/USDT'

    # Convert lookback_days to timestamp
    if lookback_days.endswith('d'):
        days_ago = int(lookback_days[:-1])
        date_start = (dt.datetime.now() - dt.timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        raise VolyError("lookback_days should be in format '90d', '30d', etc.")

    from_ts = exchange.parse8601(date_start)
    ohlcv_list = []
    ohlcv = exchange.fetch_ohlcv(symbol, granularity, since=from_ts, limit=1000)
    ohlcv_list.append(ohlcv)
    while True:
        from_ts = ohlcv[-1][0]
        new_ohlcv = exchange.fetch_ohlcv(symbol, granularity, since=from_ts, limit=1000)
        ohlcv.extend(new_ohlcv)
        if len(new_ohlcv) != 1000:
            break

    # Convert to DataFrame
    df_hist = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df_hist['date'] = pd.to_datetime(df_hist['date'], unit='ms')
    df_hist.set_index('date', inplace=True)
    df_hist = df_hist.sort_index(ascending=True)

    print(f"Data fetched successfully: {len(df_hist)} rows from {df_hist.index[0]} to {df_hist.index[-1]}")

    return df_hist


def generate_lm_points(min_lm, max_lm):
    if min_lm >= max_lm:
        raise ValueError("min_lm must be less than max_lm")

    max_transformed = np.sqrt(max_lm) if max_lm > 0 else 0
    min_transformed = -np.sqrt(-min_lm) if min_lm < 0 else 0

    transformed_points = np.arange(min_transformed, max_transformed + 0.05, 0.05)
    lm_points = np.sign(transformed_points) * transformed_points ** 2

    lm_points = np.unique(np.round(lm_points, decimals=2))
    lm_points = sorted(lm_points)

    return lm_points


@catch_exception
def get_hd_surface(model_results: pd.DataFrame,
                   df_hist: pd.DataFrame,
                   domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                   return_domain: str = 'log_moneyness') -> Tuple[
    Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray], pd.DataFrame]:

    # Check if required columns are present
    required_columns = ['s', 't', 'r']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    # Determine granularity from df_hist
    if len(df_hist) > 1:
        # Calculate minutes between consecutive timestamps
        minutes_diff = (df_hist.index[1] - df_hist.index[0]).total_seconds() / 60
        minutes_per_period = int(minutes_diff)
    else:
        VolyError("Cannot determine granularity from df_hist.")
        return

    pdf_surface = {}
    cdf_surface = {}
    x_surface = {}
    all_moments = {}

    # Process each maturity
    for i in model_results.index:
        # Get parameters for this maturity
        s = model_results.loc[i, 's']
        r = model_results.loc[i, 'r']
        t = model_results.loc[i, 't']

        LM = get_domain(domain_params, s, r, None, t, 'log_moneyness')
        M = get_domain(domain_params, s, r, None, t, 'moneyness')
        R = get_domain(domain_params, s, r, None, t, 'returns')
        K = get_domain(domain_params, s, r, None, t, 'log_moneyness')

        # Filter historical data for this maturity's lookback period
        start_date = dt.datetime.now() - dt.timedelta(days=int(t * 365.25))
        maturity_hist = df_hist[df_hist.index >= start_date].copy()

        if len(maturity_hist) < 10:
            logger.warning(f"Not enough historical data for maturity {i}, skipping.")
            continue

        # Calculate the number of periods that match the time to expiry
        n_periods = int(t * 365.25 * 24 * 60 / minutes_per_period)

        # Compute returns and weights
        maturity_hist['returns'] = np.log(maturity_hist['close'] / maturity_hist['close'].shift(1)) * np.sqrt(n_periods)
        maturity_hist = maturity_hist.dropna()

        returns = maturity_hist['returns'].values

        if len(returns) < 10:
            logger.warning(f"Not enough valid returns for maturity {i}, skipping.")
            continue

        mu_scaled = returns.mean()
        sigma_scaled = returns.std()

        # Correct Girsanov adjustment to match the risk-neutral mean
        expected_risk_neutral_mean = (r - 0.5 * sigma_scaled ** 2) * np.sqrt(t)
        adjustment = mu_scaled - expected_risk_neutral_mean
        adj_returns = returns - adjustment  # Shift the mean to risk-neutral

        # Create HD and Normalize
        f = stats.gaussian_kde(adj_returns, bw_method='silverman', weights=weights)
        hd_lm = f(LM)
        hd_lm = np.maximum(hd_lm, 0)
        total_area = np.trapz(hd_lm, LM)
        if total_area > 0:
            pdf_lm = hd_lm / total_area
        else:
            logger.warning(f"Total area is zero for maturity {i}, skipping.")
            continue

        pdf_k = pdf_lm / K
        pdf_m = pdf_k * s
        pdf_r = pdf_lm / (1 + R)

        cdf = np.concatenate(([0], np.cumsum(pdf_lm[:-1] * np.diff(LM))))

        if return_domain == 'log_moneyness':
            x = LM
            pdf = pdf_lm
            moments = get_all_moments(x, pdf)
        elif return_domain == 'moneyness':
            x = M
            pdf = pdf_m
            moments = get_all_moments(x, pdf)
        elif return_domain == 'returns':
            x = R
            pdf = pdf_r
            moments = get_all_moments(x, pdf)
        elif return_domain == 'strikes':
            x = K
            pdf = pdf_k
            moments = get_all_moments(x, pdf)

        # Store results
        pdf_surface[i] = pdf
        cdf_surface[i] = cdf
        x_surface[i] = x
        all_moments[i] = moments

    # Create a DataFrame with moments using the same index as model_results
    moments = pd.DataFrame(all_moments).T

    return hd_surface, cdf_surface, x_surface, moments


@catch_exception
def get_rv_surface(model_results: pd.DataFrame,
                   pdf_surface: Dict[str, np.ndarray],
                   x_surface: Dict[str, np.ndarray],
                   domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                   return_domain: str = 'log_moneyness') -> Tuple[
    Dict[str, np.ndarray], Dict[str, np.ndarray], pd.DataFrame]:

    # Check if required columns are present
    required_columns = ['s', 't', 'r']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    iv_surface = {}
    new_x_surface = {}
    all_params = {}

    # Check if hd_surface is empty
    if not hd_surface:
        logger.warning("Historical density surface is empty.")
        return {}, {}, pd.DataFrame()

    # Process each maturity
    for i in model_results.index:
        if i not in hd_surface:
            logger.warning(f"No historical density available for maturity {i}, skipping.")
            continue

        # Get parameters for this maturity
        s = model_results.loc[i, 's']
        r = model_results.loc[i, 'r']
        t = model_results.loc[i, 't']

        # Get historical density for this maturity
        pdf = pdf_surface[i]
        x = x_surface[i]

        # Calculate x_domain grids
        LM = get_domain(domain_params, s, r, None, t, 'log_moneyness')
        M = get_domain(domain_params, s, r, None, t, 'moneyness')
        R = get_domain(domain_params, s, r, None, t, 'returns')
        K = get_domain(domain_params, s, r, None, t, 'log_moneyness')

        # Recover call prices from the PDF
        c_recovered = np.zeros_like(LM)
        for j, lm_k in enumerate(LM):
            mask = LM >= lm_k
            if np.any(mask):
                integrand = s * (np.exp(LM[mask]) - np.exp(lm_k)) * hd[mask]
                c_recovered[j] = np.exp(-r * t) * np.trapz(integrand, LM[mask])

        # Ensure call prices are at least the intrinsic value
        intrinsic_values = np.maximum(s - K, 0)
        c_recovered = np.maximum(c_recovered, intrinsic_values)

        # Determine min_lm and max_lm based on days to expiry (DTE)
        dte = t * 365.25
        if dte <= 30:
            min_lm, max_lm = -0.3, 0.3
        elif dte <= 90:
            min_lm, max_lm = -0.6, 0.6
        else:
            min_lm, max_lm = -0.9, 0.9

        # Generate key log-moneyness points
        key_lm_points = generate_lm_points(min_lm, max_lm)

        # Find the indices of the key log-moneyness points
        key_indices = [np.argmin(np.abs(LM - lm)) for lm in key_lm_points]
        key_lm_actual = LM[key_indices]  # Actual log moneyness values
        key_strikes = K[key_indices]  # Corresponding strikes

        # Extract call prices at key log-moneyness points
        key_call_prices = c_recovered[key_indices]

        # Compute IV at key log-moneyness points using our own iv function
        key_ivs = []
        for j, idx in enumerate(key_indices):
            call_price = key_call_prices[j]
            strike = key_strikes[j]
            if call_price <= 0:
                iv_value = 0.01  # Minimum IV of 1%
            else:
                try:
                    iv_value = iv(option_price=call_price, s=s, K=strike, r=r, t=t, option_type='call')
                    iv_value = max(0.01, min(iv_value, 3.0))  # Clamp between 1% and 300%
                except Exception as e:
                    logger.warning(f"IV calculation failed for strike {strike}: {str(e)}")
                    iv_value = 0.01  # Fallback to 1%
            key_ivs.append(iv_value)
        key_ivs = np.array(key_ivs)

        # Create a synthetic option chain for SVI fitting
        # Convert to DataFrame columns that fit_model expects
        synthetic_chain = pd.DataFrame({
            'maturity_name': [i] * len(key_strikes),
            'maturity_date': pd.Timestamp.now() + pd.Timedelta(days=int(t * 365.25)),
            'index_price': s,
            'underlying_price': s,
            'strike': key_strikes,
            'log_moneyness': key_lm_actual,
            'mark_iv': key_ivs,
            't': t,
            'r': r,
            'option_type': 'call'
        })

        # Fit the SVI model to the recovered IVs
        fit_results_rv = fit_model(option_chain=synthetic_chain, model_name='svi')

        # Get the parameters for this maturity
        a = fit_results_rv.loc[i, 'a']
        b = fit_results_rv.loc[i, 'b']
        sigma = fit_results_rv.loc[i, 'sigma']
        rho = fit_results_rv.loc[i, 'rho']
        m = fit_results_rv.loc[i, 'm']

        # Store the parameters
        params = {
            's': s,
            'r': r,
            't': t,
            'a': a,
            'b': b,
            'sigma': sigma,
            'rho': rho,
            'm': m
        }

        nu, psi, p, c, nu_tilde = SVIModel.raw_to_jw_params(params['a'], params['b'], params['sigma'], params['rho'], params['m'], params['t'])
        params.update({
            'nu': nu,
            'psi': psi,
            'p': p,
            'c': c,
            'nu_tilde': nu_tilde,
        })
        all_params[i] = params

        # Calculate implied volatility using SVI model
        w = np.array([SVIModel.svi(lm, a, b, sigma, rho, m) for lm in LM])
        o_recovered = np.sqrt(w / t)

        # Store results
        iv_surface[i] = o_recovered

        if return_domain == 'log_moneyness':
            x = LM
        elif return_domain == 'moneyness':
            x = M
        elif return_domain == 'returns':
            x = R
        elif return_domain == 'strikes':
            x = K
        elif return_domain == 'delta':
            x = get_domain(domain_params, s, r, o_recovered, t, 'delta')

        new_x_surface[i] = x

    # Create a DataFrame with parameters
    fit_results = pd.DataFrame(all_params).T
    x_surface = new_x_surface
    return iv_surface, x_surface, fit_results
