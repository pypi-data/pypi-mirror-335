"""
Model fitting and calibration module for the Voly package.

This module handles fitting volatility models to market data and
calculating fitting statistics.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Union, Any
from scipy.optimize import least_squares
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from voly.utils.logger import logger, catch_exception
from voly.formulas import get_domain
from voly.exceptions import VolyError
from voly.models import SVIModel
import warnings

warnings.filterwarnings("ignore")


@catch_exception
def calculate_residuals(params: List[float], t: float, option_chain: pd.DataFrame,
                        model: Any = SVIModel) -> np.ndarray:
    """Calculate residuals between market and model implied volatilities."""
    maturity_data = option_chain[option_chain['t'] == t]
    w = np.array([model.svi(x, *params) for x in maturity_data['log_moneyness']])
    iv_actual = maturity_data['mark_iv'].values
    return iv_actual - np.sqrt(w / t)


@catch_exception
def fit_model(option_chain: pd.DataFrame,
              model_name: str = 'svi',
              initial_params: Optional[List[float]] = None,
              param_bounds: Optional[Tuple] = None) -> pd.DataFrame:
    """
    Fit a volatility model to market data.

    Parameters:
    - option_chain: DataFrame with market data
    - model_name: Type of model to fit (default: 'svi')
    - initial_params: Optional initial parameters for optimization (default: model's defaults)
    - param_bounds: Optional parameter bounds for optimization (default: model's defaults)

    Returns:
    - DataFrame with all fit results and performance metrics as columns, maturity_names as index
    """
    if model_name.lower() != 'svi':
        raise VolyError(f"Model type '{model_name}' is not supported. Currently only 'svi' is available.")

    # Use defaults if not provided
    initial_params = initial_params or SVIModel.DEFAULT_INITIAL_PARAMS
    param_bounds = param_bounds or SVIModel.DEFAULT_PARAM_BOUNDS

    # Define column names and their data types
    column_dtypes = {
        's': float,
        'u': float,
        't': float,
        'r': float,
        'oi': float,
        'volume': float,
        'maturity_date': 'datetime64[ns]',
        'a': float,
        'b': float,
        'sigma': float,
        'rho': float,
        'm': float,
        'nu': float,
        'psi': float,
        'p': float,
        'c': float,
        'nu_tilde': float,
        'fit_success': bool,
        'cost': float,
        'optimality': float,
        'rmse': float,
        'mae': float,
        'r2': float,
        'max_error': float,
        'n_points': int
    }

    # Get unique maturities and sort them
    unique_ts = sorted(option_chain['t'].unique())
    maturity_names = [option_chain[option_chain['t'] == t]['maturity_name'].iloc[0] for t in unique_ts]

    # Store results in a dictionary first
    results_data = {col: [] for col in column_dtypes.keys()}

    # ANSI color codes for terminal output
    GREEN, RED, RESET = '\033[32m', '\033[31m', '\033[0m'

    s = option_chain['index_price'].iloc[-1]

    for t in unique_ts:
        # Get data for this maturity
        maturity_data = option_chain[option_chain['t'] == t]
        maturity_name = maturity_data['maturity_name'].iloc[0]

        logger.info(f"Optimizing for {maturity_name}...")

        # Optimize SVI parameters
        try:
            result = least_squares(
                calculate_residuals,
                initial_params,
                args=(t, option_chain, SVIModel),
                bounds=param_bounds,
                max_nfev=1000
            )
        except Exception as e:
            raise VolyError(f"Optimization failed for {maturity_name}: {str(e)}")

        # Extract raw parameters
        a, b, sigma, rho, m = result.x

        # Calculate model predictions for statistics
        w = np.array([SVIModel.svi(x, *result.x) for x in maturity_data['log_moneyness']])
        iv_model = np.sqrt(w / t)
        iv_market = maturity_data['mark_iv'].values

        # Calculate statistics
        rmse = np.sqrt(mean_squared_error(iv_market, iv_model))
        mae = mean_absolute_error(iv_market, iv_model)
        r2 = r2_score(iv_market, iv_model)
        max_error = np.max(np.abs(iv_market - iv_model))

        # Get or calculate additional required data
        u = maturity_data['underlying_price'].iloc[0]

        # Aggregate open interest and volume
        oi = maturity_data['open_interest'].sum() if 'open_interest' in maturity_data.columns else 0
        volume = maturity_data['volume'].sum() if 'volume' in maturity_data.columns else 0
        r = maturity_data['interest_rate'].iloc[0] if 'interest_rate' in maturity_data.columns else 0

        # Calculate Jump-Wing parameters
        nu, psi, p, c, nu_tilde = SVIModel.raw_to_jw_params(a, b, sigma, rho, m, t)

        # Store values in the results dictionary with proper types
        results_data['s'].append(float(s))
        results_data['u'].append(float(u))
        results_data['t'].append(float(t))
        results_data['r'].append(float(r))
        results_data['oi'].append(float(oi))
        results_data['volume'].append(float(volume))
        results_data['maturity_date'].append(maturity_data['maturity_date'].iloc[0])
        results_data['a'].append(float(a))
        results_data['b'].append(float(b))
        results_data['sigma'].append(float(sigma))
        results_data['m'].append(float(m))
        results_data['rho'].append(float(rho))
        results_data['nu'].append(float(nu))
        results_data['psi'].append(float(psi))
        results_data['p'].append(float(p))
        results_data['c'].append(float(c))
        results_data['nu_tilde'].append(float(nu_tilde))
        results_data['fit_success'].append(bool(result.success))
        results_data['cost'].append(float(result.cost))
        results_data['optimality'].append(float(result.optimality))
        results_data['rmse'].append(float(rmse))
        results_data['mae'].append(float(mae))
        results_data['r2'].append(float(r2))
        results_data['max_error'].append(float(max_error))
        results_data['n_points'].append(int(len(maturity_data)))

        # Log result
        status = f'{GREEN}SUCCESS{RESET}' if result.success else f'{RED}FAILED{RESET}'
        logger.info(f'Optimization for {maturity_name}: {status}')
        logger.info('-------------------------------------')

    # Create DataFrame with proper types
    results_df = pd.DataFrame(results_data, index=maturity_names)

    # Convert columns to appropriate types
    for col, dtype in column_dtypes.items():
        if col in results_df.columns:
            try:
                results_df[col] = results_df[col].astype(dtype)
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not convert column {col} to {dtype}: {e}")

    return results_df


@catch_exception
def get_iv_surface(model_results: pd.DataFrame,
                   domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                   return_domain: str = 'log_moneyness') -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Generate implied volatility surface using optimized SVI parameters.

    Works with both regular fit_results and interpolated_results dataframes.

    Parameters:
    - model_results: DataFrame from fit_model() or interpolate_model(). Maturity names or DTM as Index
    - domain_params: Tuple of (min, max, num_points) for the log-moneyness array
    - return_domain: Domain for x-axis values ('log_moneyness', 'moneyness', 'returns', 'strikes', 'delta')

    Returns:
    - Tuple of (iv_surface, x_surface)
      iv_surface: Dictionary mapping maturity/dtm names to IV arrays
      x_surface: Dictionary mapping maturity/dtm names to requested x domain arrays
    """
    # Check if required columns are present
    required_columns = ['a', 'b', 'sigma', 'rho', 'm', 't']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    # Generate implied volatility surface in log-moneyness domain
    LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])

    iv_surface = {}
    x_surface = {}

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
        w = np.array([SVIModel.svi(x, *params) for x in LM])
        o = np.sqrt(w / t)
        iv_surface[i] = o

        # Calculate x domain for this maturity/dtm
        x = get_domain(domain_params, s, r, o, t, return_domain)
        x_surface[i] = x

    return iv_surface, x_surface
