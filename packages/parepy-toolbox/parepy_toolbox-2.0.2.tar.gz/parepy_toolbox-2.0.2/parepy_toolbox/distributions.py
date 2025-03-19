"""Function of probability distributions"""
import numpy as np
from scipy.stats import norm


def crude_sampling_zero_one(n_samples: int, seed: int=None) -> list:
    """
    This function generates a uniform sampling between 0 and 1.

    Args:
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation

    Returns:
        u (List): Random samples
    """
    rng = np.random.default_rng(seed=seed)

    return rng.random(n_samples).tolist()


def lhs_sampling_zero_one(n_samples: int, dimension: int, seed: int=None) -> np.ndarray:
    """
    This function generates a uniform sampling between 0 and 1 using the Latin Hypercube Sampling Algorithm.

    Args:
        n_samples (Integer): Number of samples
        dimension (Integer): Number of dimensions
        seed (Integer): Seed for random number generation

    Returns:
        u (np.array): Random samples
    """
    r = np.zeros((n_samples, dimension))
    p = np.zeros((n_samples, dimension))
    original_ids = [i for i in range(1, n_samples+1)]
    if seed is not None:
        x = crude_sampling_zero_one(n_samples * dimension, seed)
    else:
        x = crude_sampling_zero_one(n_samples * dimension)
    for i in range(dimension):
        perms = original_ids.copy()
        r[:, i] = x[:n_samples]
        del x[:n_samples]
        rng = np.random.default_rng(seed=seed)
        rng.shuffle(perms)
        p[:, i] = perms.copy()
    u = (p - r) * (1 / n_samples)

    return u


def uniform_sampling(parameters: dict, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a Uniform sampling between a (minimum) and b (maximum).

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys:  'min' (Minimum value of the uniform distribution [float]), 'max' (Maximum value of the uniform distribution [float])
        method (String): Sampling method. Supports the following values: 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation. Use None for a random seed
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux = crude_sampling_zero_one(n_samples, seed)
        elif seed is None:
            u_aux = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux = lhs_sampling_zero_one(n_samples, 1, seed).flatten()
        elif seed is None:
            u_aux = lhs_sampling_zero_one(n_samples, 1).flatten()

    # PDF parameters and generation of samples    
    a = parameters['min']
    b = parameters['max']
    u = [float(a + (b - a) * i) for i in u_aux]

    return u


def normal_sampling(parameters: dict, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a Normal or Gaussian sampling with mean (mu) and standard deviation (sigma).

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys 'mu' (Mean [float]), 'sigma' (Standard deviation [float])
        method (String): Sampling method. Supports the following values: 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation. Use None for a random seed
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux1 = crude_sampling_zero_one(n_samples, seed)
            u_aux2 = crude_sampling_zero_one(n_samples, seed+1)
        elif seed is None:
            u_aux1 = crude_sampling_zero_one(n_samples)
            u_aux2 = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux1 = lhs_sampling_zero_one(n_samples, 2, seed)
        elif seed is None:
            u_aux1 = lhs_sampling_zero_one(n_samples, 2)

    # PDF parameters and generation of samples  
    mean = parameters['mean']
    std = parameters['sigma']
    u = []
    for i in range(n_samples):
        if method.lower() == 'lhs':
            z = float(np.sqrt(-2 * np.log(u_aux1[i, 0])) * np.cos(2 * np.pi * u_aux1[i, 1]))
        elif method.lower() == 'mcs':
            z = float(np.sqrt(-2 * np.log(u_aux1[i])) * np.cos(2 * np.pi * u_aux2[i]))
        u.append(mean + std * z)

    return u


def corr_normal_sampling(parameters_b: dict, parameters_g: dict, pho_gb: float, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a Normal or Gaussian sampling with mean (mu) and standard deviation (sigma). Variable g have a correlation rho_gb with b.

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys 'mu' (Mean [float]), 'sigma' (Standard deviation [float])
        method (String): Sampling method. Supports the following values: 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation. Use None for a random seed
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux1 = crude_sampling_zero_one(n_samples, seed)
            u_aux2 = crude_sampling_zero_one(n_samples, seed+1)
        elif seed is None:
            u_aux1 = crude_sampling_zero_one(n_samples)
            u_aux2 = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux1 = lhs_sampling_zero_one(n_samples, 2, seed)
        elif seed is None:
            u_aux1 = lhs_sampling_zero_one(n_samples, 2)

    # PDF parameters and generation of samples  
    mean_b = parameters_b['mean']
    std_b = parameters_b['sigma']
    mean_g = parameters_g['mean']
    std_g = parameters_g['sigma']
    b = []
    g = []
    for i in range(n_samples):
        if method.lower() == 'lhs':
            z_1 = float(np.sqrt(-2 * np.log(u_aux1[i, 0])) * np.cos(2 * np.pi * u_aux1[i, 1]))
            z_2 = float(np.sqrt(-2 * np.log(u_aux1[i, 0])) * np.sin(2 * np.pi * u_aux1[i, 1]))
        elif method.lower() == 'mcs':
            z_1 = float(np.sqrt(-2 * np.log(u_aux1[i])) * np.cos(2 * np.pi * u_aux2[i]))
            z_2 = float(np.sqrt(-2 * np.log(u_aux1[i])) * np.sin(2 * np.pi * u_aux2[i]))
        b.append(mean_b + std_b * z_1)
        g.append(mean_g + std_g * (pho_gb * z_1 + z_2 * np.sqrt(1 - pho_gb ** 2)))

    return b, g


def lognormal_sampling(parameters: dict, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a log-normal sampling with mean and standard deviation.

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys 'mu' (mean [float]), 'sigma' (standard deviation [float])
        method (String): Sampling method. Can use 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux1 = crude_sampling_zero_one(n_samples, seed)
            u_aux2 = crude_sampling_zero_one(n_samples, seed+1)
        elif seed is None:
            u_aux1 = crude_sampling_zero_one(n_samples)
            u_aux2 = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux1 = lhs_sampling_zero_one(n_samples, 2, seed)
        elif seed is None:
            u_aux1 = lhs_sampling_zero_one(n_samples, 2)

    # PDF parameters and generation of samples  
    mean = parameters['mean']
    std = parameters['sigma']
    epsilon = np.sqrt(np.log(1 + (std/mean)**2))
    lambdaa = np.log(mean) - 0.5 * epsilon**2
    u = []
    for i in range(n_samples):
        if method.lower() == 'lhs':
            z = float(np.sqrt(-2 * np.log(u_aux1[i, 0])) * np.cos(2 * np.pi * u_aux1[i, 1]))
        elif method.lower() == 'mcs':
            z = float(np.sqrt(-2 * np.log(u_aux1[i])) * np.cos(2 * np.pi * u_aux2[i]))
        u.append(np.exp(lambdaa + epsilon * z))

    return u


def gumbel_max_sampling(parameters: dict, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a Gumbel maximum distribution with a specified mean and standard deviation.

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys 'mu' (mean [float]), 'sigma' (standard deviation [float])
        method (String): Sampling method. Can use 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux = crude_sampling_zero_one(n_samples, seed)
        elif seed is None:
            u_aux = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux = lhs_sampling_zero_one(n_samples, 1, seed).flatten()
        elif seed is None:
            u_aux = lhs_sampling_zero_one(n_samples, 1).flatten()

    # PDF parameters and generation of samples  
    mean = parameters['mean']
    std = parameters['sigma']
    gamma = 0.577215665
    beta = np.pi / (np.sqrt(6) * std)
    alpha = mean - gamma / beta
    u = []
    for i in range(n_samples):
        u.append(alpha - (1 / beta) * np.log(-np.log(u_aux[i])))

    return u


def gumbel_min_sampling(parameters: dict, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a Gumbel Minimum sampling with mean and standard deviation.

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys 'mu' (mean [float]), 'sigma' (standard deviation [float])
        method (String): Sampling method. Can use 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux = crude_sampling_zero_one(n_samples, seed)
        elif seed is None:
            u_aux = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux = lhs_sampling_zero_one(n_samples, 1, seed).flatten()
        elif seed is None:
            u_aux = lhs_sampling_zero_one(n_samples, 1).flatten()

    # PDF parameters and generation of samples  
    mean = parameters['mean']
    std = parameters['sigma']
    gamma = 0.577215665
    beta = np.pi / (np.sqrt(6) * std) 
    alpha = mean + gamma / beta
    u = []
    for i in range(n_samples):
        u.append(alpha + (1 / beta) * np.log(-np.log(1 - u_aux[i])))

    return u


def triangular_sampling(parameters: dict, method: str, n_samples: int, seed: int=None) -> list:
    """
    This function generates a triangular sampling with minimun a, mode c, and maximum b.

    Args:
        parameters (Dictionary): Dictionary of parameters. Keys 'a' (minimum [float]), 'c' (mode [float]), and 'b' (maximum [float])
        method (String): Sampling method. Can use 'lhs' (Latin Hypercube Sampling) or 'mcs' (Crude Monte Carlo Sampling)
        n_samples (Integer): Number of samples
        seed (Integer): Seed for random number generation
    
    Returns:
        u (List): Random samples
    """

    # Random uniform sampling between 0 and 1
    if method.lower() == 'mcs':
        if seed is not None:
            u_aux = crude_sampling_zero_one(n_samples, seed)
        elif seed is None:
            u_aux = crude_sampling_zero_one(n_samples)
    elif method.lower() == 'lhs':
        if seed is not None:
            u_aux = lhs_sampling_zero_one(n_samples, 1, seed).flatten()
        elif seed is None:
            u_aux = lhs_sampling_zero_one(n_samples, 1).flatten()

    # PDF parameters and generation of samples  
    a = parameters['min']
    c = parameters['mode']
    b = parameters['max']
    u = []
    for i in range(n_samples):
        criteria = (c - a) / (b - a)
        if u_aux[i] < criteria:
            u.append(a + np.sqrt(u_aux[i] * (b - a) * (c - a)))
        else:
            u.append(b - np.sqrt((1 - u_aux[i]) * (b - a) * (b - c)))

    return u


def cdf_gumbel_max(x: float, u: float, beta: float) -> float:
    """
    Calculates the cumulative distribution function (CDF) of the Maximum Gumbel distribution.

    Parameters:
        x (Float): Input value for which the CDF will be calculated.
        u (Float): Location parameter (mode) of the Maximum Gumbel distribution.
        beta (Float): Scale parameter of the Maximum Gumbel distribution.

    Returns:
        fx (Float): Value of the CDF at point x.
    """
    fx = np.exp(-np.exp((- beta * (x - u))))
    return fx


def pdf_gumbel_max(x: float, u: float, beta: float) -> float:
    """
    Calculates the probability density function (PDF) of the Maximum Gumbel distribution.

    Parameters:
        x (Float): Input value for which the PDF will be calculated.
        u (Float): Location parameter (mode) of the Maximum Gumbel distribution.
        beta (Float): Scale parameter of the Maximum Gumbel distribution.

    Returns:
        fx (Float): Value of the PDF at point x.
    """
    fx = beta * np.exp((- beta * (x - u))) - np.exp((- beta * (x - u)))
    return fx


def cdf_gumbel_min(x: float, u: float, beta: float) -> float:
    """
    Calculates the cumulative distribution function (CDF) of the Minimum Gumbel distribution.

    Parameters:
        x (Float): Input value for which the CDF will be calculated.
        u (Float): Location parameter (mode) of the Minimum Gumbel distribution.
        beta (Float): Scale parameter of the Minimum Gumbel distribution.

    Returns:
        fx (Float): Value of the CDF at point x.
    """
    fx = 1 - np.exp(- np.exp((beta * (x - u))))
    return fx


def pdf_gumbel_min(x: float, u: float, beta: float) -> float:
    """
    Calculates the probability density function (PDF) of the Minimum Gumbel distribution.

    Parameters:
        x (float): Input value for which the PDF will be calculated.
        u (float): Location parameter (mode) of the Minimum Gumbel distribution.
        beta (float): Scale parameter of the Minimum Gumbel distribution.

    Returns:
        fx (float): Value of the PDF at point x.
    """
    fx = beta * np.exp((beta * (x - u))) - np.exp(beta * (x - u))
    return fx


def cdf_normal(x: float, u: float, sigma: float) -> float:
    """
    Calculates the cumulative distribution function (CDF) of the Normal distribution.

    Parameters:
        x (float): Input value for which the CDF will be calculated.
        u (float): Mean (location) of the Normal distribution.
        sigma (float): Standard deviation (scale) of the Normal distribution.

    Returns:
        fx (float): Value of the CDF at point x.
    """
    fx = norm.cdf(x, loc=u, scale=sigma)
    return fx


def pdf_normal(x: float, u: float, sigma: float) -> float:
    """
    Calculates the probability density function (PDF) of the Normal distribution.

    Parameters:
        x (Float): Input value for which the PDF will be calculated.
        u (Float): Mean (location) of the Normal distribution.
        sigma (Float): Standard deviation (scale) of the Normal distribution.

    Returns:
        fx (Float): Value of the PDF at point x.
    """
    fx = norm.pdf(x, loc=u, scale=sigma)
    return fx


def log_normal(x: float, lambdaa: float, epsilon: float) -> tuple[float, float]:
    """
    Calculates the location (u) and scale (sigma) parameters for a Log-Normal distribution.

    Parameters:
        x (Float): Input value.
        lambdaa (Float): Shape parameter of the Log-Normal distribution.
        epsilon (Float): Scale parameter of the Log-Normal distribution.

    Returns:
        u (Float): Location parameter.
        sigma (Float): Scale parameter.
    """
    loc = x * (1 - np.log(x) + lambdaa)
    sigma = x * epsilon
    return loc, sigma


def non_normal_approach_normal(x, dist, params):
    """
    This function convert non normal distribution to normal distribution.

    Parameters:
        x (Float): Random variable
        dist (String): Type of distribution: 'gumbel max', 'gumbel min', 'lognormal')
        params (Dictionary): Parameters of distribution

    Returns:
        mu_t (Float): mean normal model
        sigma_t (Float): standard deviation normal model
    """

    if dist == 'gumbel max':
        u = params.get('u')
        beta = params.get('beta')
        cdf_x = cdf_gumbel_max(x, u, beta)
        pdf_temp = pdf_gumbel_max(x, u, beta)
    elif dist == 'gumbel min':
        u = params.get('u')
        beta = params.get('beta')
        cdf_x = cdf_gumbel_min(x, u, beta)
        pdf_temp = pdf_gumbel_min(x, u, beta)
    
    if dist == 'lognormal':
        epsilon = params.get('epsilon')
        lambdaa = params.get('lambda')
        loc_eq, sigma_eq = log_normal(x, lambdaa, epsilon)
    else:
        icdf = norm.ppf(cdf_x, loc=0, scale=1)
        sigma_eq = norm.pdf(icdf, loc=0, scale=1) / pdf_temp
        loc_eq = x - sigma_eq * icdf

    return float(loc_eq), float(sigma_eq)
