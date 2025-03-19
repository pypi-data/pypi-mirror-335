"""Common library for PAREpy toolbox"""
from typing import Union, Callable
import re
from datetime import datetime

from scipy.integrate import quad
import scipy.stats as stats
import numpy as np
from numpy import sqrt, pi, exp
import pandas as pd

import parepy_toolbox.distributions as parepydi


def sampling(n_samples: int, model: dict, variables_setup: list) -> np.ndarray:
    """
    This algorithm generates a set of random numbers according to a type of distribution.

    Args:
        n_samples (Integer): Number of samples
        model (Dictionary): Model parameters
        variables_setup (List): Random variable parameters (list of dictionaries)
    
    Returns:
        random_sampling (np.array): Random samples
    """

    # Model settings
    model_sampling = model['model sampling'].upper()
    id_type = []
    id_corr = []
    for v in variables_setup:
        if 'parameters' in v and 'corr' in v['parameters']:
            id_type.append('g-corr-g_var')
            id_corr.append(v['parameters']['corr']['var'])
        else:
            id_type.append('g')
    for k in id_corr:
        id_type[k] = 'g-corr-b_var'

    if model_sampling in ['MCS', 'LHS']:
        random_sampling = np.zeros((n_samples, len(variables_setup)))

        for j, variable in enumerate(variables_setup):
            if id_type[j] == 'g-corr-b_var':
                continue
            type_dist = variable['type'].upper()
            seed_dist = variable['seed']
            params = variable['parameters']

            if (type_dist == 'NORMAL' or type_dist == 'GAUSSIAN') and id_type[j] == 'g':
                mean = params['mean']
                sigma = params['sigma']
                parameters = {'mean': mean, 'sigma': sigma}
                random_sampling[:, j] = parepydi.normal_sampling(parameters, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)

            elif (type_dist == 'NORMAL' or type_dist == 'GAUSSIAN') and id_type[j] == 'g-corr-g_var':
                mean = params['mean']
                sigma = params['sigma']
                parameters_g = {'mean': mean, 'sigma': sigma}
                pho = params['corr']['pho']
                m = params['corr']['var']
                parameters_b = variables_setup[m]['parameters']
                random_sampling[:, m], random_sampling[:, j] = parepydi.corr_normal_sampling(parameters_b, parameters_g, pho, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)

            elif type_dist == 'UNIFORM' and id_type[j] == 'g':
                min_val = params['min']
                max_val = params['max']
                parameters = {'min': min_val, 'max': max_val}
                random_sampling[:, j] = parepydi.uniform_sampling(parameters, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)

            elif type_dist == 'GUMBEL MAX' and id_type[j] == 'g':
                mean = params['mean']
                sigma = params['sigma']
                parameters = {'mean': mean, 'sigma': sigma}
                random_sampling[:, j] = parepydi.gumbel_max_sampling(parameters, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)

            elif type_dist == 'GUMBEL MIN' and id_type[j] == 'g':
                mean = params['mean']
                sigma = params['sigma']
                parameters = {'mean': mean, 'sigma': sigma}
                random_sampling[:, j] = parepydi.gumbel_min_sampling(parameters, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)

            elif type_dist == 'LOGNORMAL' and id_type[j] == 'g':
                mean = params['mean']
                sigma = params['sigma']
                parameters = {'mean': mean, 'sigma': sigma}
                random_sampling[:, j] = parepydi.lognormal_sampling(parameters, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)

            elif type_dist == 'TRIANGULAR' and id_type[j] == 'g':
                min_val = params['min']
                max_val = params['max']
                mode = params['mode']
                parameters = {'min': min_val, 'max': max_val, 'mode': mode}
                random_sampling[:, j] = parepydi.triangular_sampling(parameters, method=model_sampling.lower(), n_samples=n_samples, seed=seed_dist)
    elif model_sampling in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
        time_analysis = model['time steps']
        random_sampling = np.empty((0, len(variables_setup)))
        match = re.search(r'\b(MCS|LHS)\b', model_sampling.upper(), re.IGNORECASE)
        model_sampling = match.group(1).upper()

        for _ in range(n_samples):
            temporal_sampling = np.zeros((time_analysis, len(variables_setup)))

            for j, variable in enumerate(variables_setup):
                if id_type[j] == 'g-corr-b_var':
                    continue
                type_dist = variable['type'].upper()
                seed_dist = variable['seed']
                sto = variable['stochastic variable']
                params = variable['parameters']

                if (type_dist == 'NORMAL' or type_dist == 'GAUSSIAN') and id_type[j] == 'g':
                    mean = params['mean']
                    sigma = params['sigma']
                    parameters = {'mean': mean, 'sigma': sigma}
                    if sto is False:
                        temporal_sampling[:, j] = parepydi.normal_sampling(parameters, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                    else:
                        temporal_sampling[:, j] = parepydi.normal_sampling(parameters, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

                elif (type_dist == 'NORMAL' or type_dist == 'GAUSSIAN') and id_type[j] == 'g-corr-g_var':
                    mean = params['mean']
                    sigma = params['sigma']
                    parameters_g = {'mean': mean, 'sigma': sigma}
                    pho = params['corr']['pho']
                    m = params['corr']['var']
                    parameters_b = variables_setup[m]['parameters']
                    if sto is False:
                        temporal_sampling[:, m], temporal_sampling[:, j] = parepydi.corr_normal_sampling(parameters_b, parameters_g, pho, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                        temporal_sampling[1:, m]
                    else:
                        temporal_sampling[:, m], temporal_sampling[:, j] = parepydi.corr_normal_sampling(parameters_b, parameters_g, pho, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

                elif type_dist == 'UNIFORM' and id_type[j] == 'g':
                    min_val = params['min']
                    max_val = params['max']
                    parameters = {'min': min_val, 'max': max_val}
                    if sto is False:
                        temporal_sampling[:, j] = parepydi.uniform_sampling(parameters, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                    else:
                        temporal_sampling[:, j] = parepydi.uniform_sampling(parameters, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

                elif type_dist == 'GUMBEL MAX' and id_type[j] == 'g':
                    mean = params['mean']
                    sigma = params['sigma']
                    parameters = {'mean': mean, 'sigma': sigma}
                    if sto is False:
                        temporal_sampling[:, j] = parepydi.gumbel_max_sampling(parameters, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                    else:
                        temporal_sampling[:, j] = parepydi.gumbel_max_sampling(parameters, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

                elif type_dist == 'GUMBEL MIN' and id_type[j] == 'g':
                    mean = params['mean']
                    sigma = params['sigma']
                    parameters = {'mean': mean, 'sigma': sigma}
                    if sto is False:
                        temporal_sampling[:, j] = parepydi.gumbel_min_sampling(parameters, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                    else:
                        temporal_sampling[:, j] = parepydi.gumbel_min_sampling(parameters, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

                elif type_dist == 'LOGNORMAL' and id_type[j] == 'g':
                    mean = params['mean']
                    sigma = params['sigma']
                    parameters = {'mean': mean, 'sigma': sigma}
                    if sto is False:
                        temporal_sampling[:, j] = parepydi.lognormal_sampling(parameters, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                    else:
                        temporal_sampling[:, j] = parepydi.lognormal_sampling(parameters, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

                elif type_dist == 'TRIANGULAR' and id_type[j] == 'g':
                    min_val = params['min']
                    max_val = params['max']
                    mode = params['mode']
                    parameters = {'min': min_val, 'max': max_val, 'mode': mode}
                    if sto is False:
                        temporal_sampling[:, j] = parepydi.triangular_sampling(parameters, method=model_sampling.lower(), n_samples=1, seed=seed_dist)
                        temporal_sampling[1:, j]
                    else:
                        temporal_sampling[:, j] = parepydi.triangular_sampling(parameters, method=model_sampling.lower(), n_samples=time_analysis, seed=seed_dist)

            random_sampling = np.concatenate((random_sampling, temporal_sampling), axis=0)  

        time_sampling = np.zeros((time_analysis * n_samples, 1))
        cont = 0
        for _ in range(n_samples):
            for m in range(time_analysis):
                time_sampling[cont, 0] = int(m)
                cont += 1
        random_sampling = np.concatenate((random_sampling, time_sampling), axis=1)   

    return random_sampling


def newton_raphson(f: Callable, df: Callable, x0: float, tol: float) -> float:
    """
    This function calculates the root of a function using the Newton-Raphson method.

    Args:
        f (Python function [def]): Function
        df (Python function [def]): Derivative of the function
        x0 (Float): Initial value
        tol (Float): Tolerance
    
    Returns:
        x0 (Float): Root of the function
    """

    if abs(f(x0)) < tol:
        return x0
    else:
        return newton_raphson(f, df, x0 - f(x0)/df(x0), tol)


def pf_equation(beta: float) -> float:
    """
    This function calculates the probability of failure (pf) for a given reliability index (ϐ) using a standard normal cumulative distribution function. The calculation is performed by integrating the probability density function (PDF) of a standard normal distribution.

    Args:
        beta (Float): Reliability index
    
    Returns:
        pf_value (Float): Probability of failure
    """

    def integrand(x):
        return 1/sqrt(2*np.pi) * np.exp(-x**2/2)

    def integral_x(x):
        integral, _ = quad(integrand, 0, x)
        return 1 - (0.5 + integral)

    return integral_x(beta)


def beta_equation(pf: float) -> Union[float, str]:
    """
    This function calculates the reliability index value for a given probability of failure (pf).

    Args:
        pf (Float): Probability of failure

    Returns:
        beta_value (Float or String): Beta value
    """

    if pf > 0.5:
        beta_value = "minus infinity"
    else:
        F = lambda BETA: BETA*(0.00569689925051199*sqrt(2)*exp(-0.497780952459929*BETA**2)/sqrt(pi) + 0.0131774933075162*sqrt(2)*exp(-0.488400032299965*BETA**2)/sqrt(pi) + 0.0204695783506533*sqrt(2)*exp(-0.471893773055302*BETA**2)/sqrt(pi) + 0.0274523479879179*sqrt(2)*exp(-0.448874334002837*BETA**2)/sqrt(pi) + 0.0340191669061785*sqrt(2)*exp(-0.42018898411968*BETA**2)/sqrt(pi) + 0.0400703501675005*sqrt(2)*exp(-0.386874144322843*BETA**2)/sqrt(pi) + 0.045514130991482*sqrt(2)*exp(-0.350103048710684*BETA**2)/sqrt(pi) + 0.0502679745335254*sqrt(2)*exp(-0.311127540182165*BETA**2)/sqrt(pi) + 0.0542598122371319*sqrt(2)*exp(-0.271217130855817*BETA**2)/sqrt(pi) + 0.0574291295728559*sqrt(2)*exp(-0.231598755762806*BETA**2)/sqrt(pi) + 0.0597278817678925*sqrt(2)*exp(-0.19340060305222*BETA**2)/sqrt(pi) + 0.0611212214951551*sqrt(2)*exp(-0.157603139738968*BETA**2)/sqrt(pi) + 0.0615880268633578*sqrt(2)*exp(-0.125*BETA**2)/sqrt(pi) + 0.0611212214951551*sqrt(2)*exp(-0.0961707934336129*BETA**2)/sqrt(pi) + 0.0597278817678925*sqrt(2)*exp(-0.0714671611917261*BETA**2)/sqrt(pi) + 0.0574291295728559*sqrt(2)*exp(-0.0510126028581118*BETA**2)/sqrt(pi) + 0.0542598122371319*sqrt(2)*exp(-0.0347157651329596*BETA**2)/sqrt(pi) + 0.0502679745335254*sqrt(2)*exp(-0.0222960750615538*BETA**2)/sqrt(pi) + 0.045514130991482*sqrt(2)*exp(-0.0133198644739499*BETA**2)/sqrt(pi) + 0.0400703501675005*sqrt(2)*exp(-0.00724451280416452*BETA**2)/sqrt(pi) + 0.0340191669061785*sqrt(2)*exp(-0.00346766973926267*BETA**2)/sqrt(pi) + 0.0274523479879179*sqrt(2)*exp(-0.00137833506369952*BETA**2)/sqrt(pi) + 0.0204695783506533*sqrt(2)*exp(-0.000406487440814915*BETA**2)/sqrt(pi) + 0.0131774933075162*sqrt(2)*exp(-6.80715702059458e-5*BETA**2)/sqrt(pi) + 0.00569689925051199*sqrt(2)*exp(-2.46756468031828e-6*BETA**2)/sqrt(pi))/2 + pf - 0.5
        F_PRIME = lambda BETA: BETA*(-0.00567161586997623*sqrt(2)*BETA*exp(-0.497780952459929*BETA**2)/sqrt(pi) - 0.0128717763140469*sqrt(2)*BETA*exp(-0.488400032299965*BETA**2)/sqrt(pi) - 0.0193189331214818*sqrt(2)*BETA*exp(-0.471893773055302*BETA**2)/sqrt(pi) - 0.0246453088397815*sqrt(2)*BETA*exp(-0.448874334002837*BETA**2)/sqrt(pi) - 0.0285889583658099*sqrt(2)*BETA*exp(-0.42018898411968*BETA**2)/sqrt(pi) - 0.0310043648675369*sqrt(2)*BETA*exp(-0.386874144322843*BETA**2)/sqrt(pi) - 0.0318692720390705*sqrt(2)*BETA*exp(-0.350103048710684*BETA**2)/sqrt(pi) - 0.031279502533111*sqrt(2)*BETA*exp(-0.311127540182165*BETA**2)/sqrt(pi) - 0.0294323811914605*sqrt(2)*BETA*exp(-0.271217130855817*BETA**2)/sqrt(pi) - 0.0266010299072288*sqrt(2)*BETA*exp(-0.231598755762806*BETA**2)/sqrt(pi) - 0.0231028167058843*sqrt(2)*BETA*exp(-0.19340060305222*BETA**2)/sqrt(pi) - 0.0192657928246347*sqrt(2)*BETA*exp(-0.157603139738968*BETA**2)/sqrt(pi) - 0.0153970067158395*sqrt(2)*BETA*exp(-0.125*BETA**2)/sqrt(pi) - 0.0117561527336413*sqrt(2)*BETA*exp(-0.0961707934336129*BETA**2)/sqrt(pi) - 0.00853716430789267*sqrt(2)*BETA*exp(-0.0714671611917261*BETA**2)/sqrt(pi) - 0.00585921875877428*sqrt(2)*BETA*exp(-0.0510126028581118*BETA**2)/sqrt(pi) - 0.00376734179556552*sqrt(2)*BETA*exp(-0.0347157651329596*BETA**2)/sqrt(pi) - 0.00224155706678351*sqrt(2)*BETA*exp(-0.0222960750615538*BETA**2)/sqrt(pi) - 0.00121248411291229*sqrt(2)*BETA*exp(-0.0133198644739499*BETA**2)/sqrt(pi) - 0.000580580329711626*sqrt(2)*BETA*exp(-0.00724451280416452*BETA**2)/sqrt(pi) - 0.000235934471270962*sqrt(2)*BETA*exp(-0.00346766973926267*BETA**2)/sqrt(pi) - 7.56770676252561e-5*sqrt(2)*BETA*exp(-0.00137833506369952*BETA**2)/sqrt(pi) - 1.66412530366349e-5*sqrt(2)*BETA*exp(-0.000406487440814915*BETA**2)/sqrt(pi) - 1.79402532164194e-6*sqrt(2)*BETA*exp(-6.80715702059458e-5*BETA**2)/sqrt(pi) - 2.81149347557902e-8*sqrt(2)*BETA*exp(-2.46756468031828e-6*BETA**2)/sqrt(pi))/2 + 0.002848449625256*sqrt(2)*exp(-0.497780952459929*BETA**2)/sqrt(pi) + 0.00658874665375808*sqrt(2)*exp(-0.488400032299965*BETA**2)/sqrt(pi) + 0.0102347891753266*sqrt(2)*exp(-0.471893773055302*BETA**2)/sqrt(pi) + 0.0137261739939589*sqrt(2)*exp(-0.448874334002837*BETA**2)/sqrt(pi) + 0.0170095834530893*sqrt(2)*exp(-0.42018898411968*BETA**2)/sqrt(pi) + 0.0200351750837502*sqrt(2)*exp(-0.386874144322843*BETA**2)/sqrt(pi) + 0.022757065495741*sqrt(2)*exp(-0.350103048710684*BETA**2)/sqrt(pi) + 0.0251339872667627*sqrt(2)*exp(-0.311127540182165*BETA**2)/sqrt(pi) + 0.027129906118566*sqrt(2)*exp(-0.271217130855817*BETA**2)/sqrt(pi) + 0.028714564786428*sqrt(2)*exp(-0.231598755762806*BETA**2)/sqrt(pi) + 0.0298639408839463*sqrt(2)*exp(-0.19340060305222*BETA**2)/sqrt(pi) + 0.0305606107475775*sqrt(2)*exp(-0.157603139738968*BETA**2)/sqrt(pi) + 0.0307940134316789*sqrt(2)*exp(-0.125*BETA**2)/sqrt(pi) + 0.0305606107475775*sqrt(2)*exp(-0.0961707934336129*BETA**2)/sqrt(pi) + 0.0298639408839463*sqrt(2)*exp(-0.0714671611917261*BETA**2)/sqrt(pi) + 0.028714564786428*sqrt(2)*exp(-0.0510126028581118*BETA**2)/sqrt(pi) + 0.027129906118566*sqrt(2)*exp(-0.0347157651329596*BETA**2)/sqrt(pi) + 0.0251339872667627*sqrt(2)*exp(-0.0222960750615538*BETA**2)/sqrt(pi) + 0.022757065495741*sqrt(2)*exp(-0.0133198644739499*BETA**2)/sqrt(pi) + 0.0200351750837502*sqrt(2)*exp(-0.00724451280416452*BETA**2)/sqrt(pi) + 0.0170095834530893*sqrt(2)*exp(-0.00346766973926267*BETA**2)/sqrt(pi) + 0.0137261739939589*sqrt(2)*exp(-0.00137833506369952*BETA**2)/sqrt(pi) + 0.0102347891753266*sqrt(2)*exp(-0.000406487440814915*BETA**2)/sqrt(pi) + 0.00658874665375808*sqrt(2)*exp(-6.80715702059458e-5*BETA**2)/sqrt(pi) + 0.002848449625256*sqrt(2)*exp(-2.46756468031828e-6*BETA**2)/sqrt(pi)
        beta_value = newton_raphson(F, F_PRIME, 0.0, 1E-15)

        return beta_value


def calc_pf_beta(df_or_path: Union[pd.DataFrame, str], numerical_model: str, n_constraints: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates the values of probability of failure or reliability index from the columns of a DataFrame that start with 'I_' (Indicator function). If a .txt file path is passed, this function evaluates pf and β values too.
    
    Args:
        df_or_path (DataFrame or String): The DataFrame containing the columns with boolean values about indicator function, or a path to a .txt file
        numerical_model (Dictionary): Containing the numerical model
        n_constraints (Integer): Number of state limit functions or constraints 

    Returns:
        df_pf (DataFrame): DataFrame containing the values for probability of failure for each 'G_' column
        df_beta (DataFrame): DataFrame containing the values for beta for each 'G_' column
    """

    # Read dataset
    if isinstance(df_or_path, str) and df_or_path.endswith('.txt'):
        df = pd.read_csv(df_or_path, delimiter='\t')
    else:
        df = df_or_path

    # Calculate pf and beta values
    if numerical_model.upper() in ['MCS', 'LHS']:
        filtered_df = df.filter(like='I_', axis=1)
        pf_results = filtered_df.mean(axis=0)
        df_pf = pd.DataFrame([pf_results.to_list()], columns=pf_results.index)
        beta_results = [beta_equation(pf) for pf in pf_results.to_list()] 
        df_beta = pd.DataFrame([beta_results], columns=pf_results.index)
    elif numerical_model.upper() in ['TIME-MCS', 'TIME-LHS', 'TIME MCS', 'TIME LHS', 'MCS TIME', 'LHS TIME', 'MCS-TIME', 'LHS-TIME']:
        df_pf = pd.DataFrame()
        df_beta = pd.DataFrame()
        for i in range(n_constraints):
            filtered_df = df.filter(like=f'I_{i}', axis=1)
            pf_results = filtered_df.mean(axis=0)
            beta_results = [beta_equation(pf) for pf in pf_results.to_list()]
            df_pf[f'G_{i}'] = pf_results.to_list()
            df_beta[f'G_{i}'] = beta_results

    return df_pf, df_beta


def convergence_probability_failure(df: pd.DataFrame, column: str) -> tuple[list, list, list, list, list]:
    """
    This function calculates the convergence rate of a given column in a data frame. This function is used to check the convergence of the failure probability.

    Args:
        df (DataFrame): DataFrame containing the data with indicator function column
        column (String): Name of the column to be analyzed

    Returns:
        div (List): list containing sample sizes
        m (List): list containing the mean values of the column. pf value rate
        ci_l (List): list containing the lower confidence interval values of the column
        ci_u (List): list containing the upper confidence interval values of the column
        var (List): list containing the variance values of the column
    """
    
    column_values = df[column].to_list()
    step = 1000
    div = [i for i in range(step, len(column_values), step)]
    m = []
    ci_u = []
    ci_l = []
    var = []
    for i in range(0, len(div)+1):
        if i == len(div):
            aux = column_values.copy()
            div.append(len(column_values))
        else:
            aux = column_values[:div[i]]
        mean = np.mean(aux)
        std = np.std(aux, ddof=1)
        n = len(aux)
        confidence_level = 0.95
        t_critic = stats.t.ppf((1 + confidence_level) / 2, df=n-1)
        margin = t_critic * (std / np.sqrt(n))
        confidence_interval = (mean - margin, mean + margin)
        m.append(mean)
        ci_u.append(confidence_interval[1])
        ci_l.append(confidence_interval[0])
        var.append((mean * (1 - mean))/n)

    return div, m, ci_l, ci_u, var


def fbf(algorithm: str, n_constraints: int, time_analysis: int, results_about_data: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """
    This function application first barrier failure algorithm.

    Args:
        algorithm (str): Name of the algorithm
        n_constraints (int): Number of constraints analyzed
        time_analysis (int): Time period for analysis
        results_about_data (pd.DataFrame): DataFrame containing the results to be processed 

    Returns:
        results_about_data: Updated DataFrame after processing
    """

    if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME']:
        i_columns = []
        for i in range(n_constraints):
            aux_column_names = []
            for j in range(time_analysis):
                aux_column_names.append('I_' + str(i) + '_t=' + str(j))
            i_columns.append(aux_column_names)

        for i in i_columns:
            matrixx = results_about_data[i].values
            for id, linha in enumerate(matrixx):
                indice_primeiro_1 = np.argmax(linha == 1)
                if linha[indice_primeiro_1] == 1:
                    matrixx[id, indice_primeiro_1:] = 1
            results_about_data = pd.concat([results_about_data.drop(columns=i),
                                            pd.DataFrame(matrixx, columns=i)], axis=1)
    else:
        i_columns = []
        for i in range(n_constraints):
            i_columns.append(['I_' + str(i)])
    
    return results_about_data, i_columns


def log_message(message: str) -> None:
    """
    Logs a message with the current time.

    Args:
        message (str): The message to log.
    
    Returns:
        None
    """
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f'{current_time} - {message}')


def norm_array(ar: list) -> float:
    """
    Evaluates the norm of the array ar.

    Args:
        ar (float): A list of numerical values (floats) representing the array.

    Returns:
        float: The norm of the array.
    """
    norm_ar = [i ** 2 for i in ar]
    norm_ar = sum(norm_ar) ** 0.5
    return norm_ar


def hasofer_lind_rackwitz_fiessler_algorithm(y_k: np.ndarray, g_y: float, grad_y_k: np.ndarray) -> np.ndarray:
    """
    This function calculates the y new value using the Hasofer-Lind-Rackwitz-Fiessler algorithm.
    
    Args:
        y_k (Float): Current y value
        g_y (Float): Objective function in point y_k
        grad_y_k (Float): Gradient of the objective function in point y_k
        
    Returns:
        y_new (Float): New y value
    """

    num = np.dot(np.transpose(grad_y_k), y_k) - np.array([[g_y]])
    print("num: ", num)
    num = num[0][0]
    den = (np.linalg.norm(grad_y_k)) ** 2
    print("den: ", den)
    aux = num / den
    y_new = aux * grad_y_k

    return y_new


# def goodness_of_fit(data: Union[np.ndarray, list], distributions: Union[str, list] = 'all') -> dict:
#     """
#     Evaluates the fit of distributions to the provided data.

#     This function fits various distributions to the data using the distfit library and returns the top three distributions based on the fit score.

#     Args:
#         data (np.array or list): Data to which distributions will be fitted. It should be a list or array of numeric values.
#         distributions (str or list, optional): Distributions to be tested. If 'all', all available distributions will be tested. Otherwise, it should be a list of strings specifying the names of the distributions to test. The default is 'all'.

#     Returns:
#         dict: A dictionary containing the top three fitted distributions. Each entry is a dictionary with the following keys:
#             - 'rank': Ranking of the top three distributions based on the fit score.
#             - 'type' (str): The name of the fitted distribution.
#             - 'params' (tuple): Parameters of the fitted distribution.
    
#     Raises:
#         ValueError: If the expected 'score' column is not present in the DataFrame returned by `dist.summary()`.
#     """

#     if distributions == 'all':
#         dist = distfit()
#     else:
#         dist = distfit(distr=distributions)
    
#     dist.fit_transform(data)
#     summary_df = dist.summary
#     sorted_models = summary_df.sort_values(by='score').head(3)
    
#     top_3_distributions = {
#         f'rank_{i+1}': {
#             'type': model['name'],
#             'params': model['params']
#         }
#         for i, model in sorted_models.iterrows()
#     }
    
#     return top_3_distributions