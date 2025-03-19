"""PAREpy toolbox: Probabilistic Approach to Reliability Engineering"""
import time
import copy
import os
import itertools
from datetime import datetime
from multiprocessing import Pool

import numpy as np
import pandas as pd

import parepy_toolbox.common_library as parepyco


def sampling_algorithm_structural_analysis_kernel(setup: dict) -> pd.DataFrame:
    """
    This function creates the samples and evaluates the limit state functions in structural reliability problems. Based on the data, it calculates probabilities of failure and reliability indexes.

    Args:
        setup (Dictionary): Setup settings
        'number of samples' (Integer): Number of samples (key in setup dictionary)
        'numerical model' (Dictionary): Numerical model settings (key in setup dictionary)
        'variables settings' (List): Variables settings, listed as dictionaries (key in setup dictionary)
        'number of state limit functions or constraints' (Integer): Number of state limit functions or constraints (key in setup dictionary)
        'none variable' (None, list, float, dictionary, str or any): None variable. User can use this variable in objective function (key in setup dictionary)
        'objective function' (Python function): Objective function. The PAREpy user defined this function (key in setup dictionary)
        'name simulation' (String or None): Output filename (key in setup dictionary)

    Returns:
        results_about_data (DataFrame): Results about reliability analysis
        failure_prob_list (List): Failure probability list
        beta_list (List): Beta list
    """
        

    # General settings
    obj = setup['objective function']
    n_samples = setup['number of samples']
    variables_settings = setup['variables settings']
    for i in variables_settings:
        if 'seed' not in i:
            i['seed'] = None
    n_dimensions = len(variables_settings)
    n_constraints = setup['number of state limit functions or constraints']
    none_variable = setup['none variable']

    # Algorithm settings
    model = setup['numerical model']
    algorithm = model['model sampling']
    if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
        time_analysis = model['time steps']
    else:
        time_analysis = None

    # Creating samples
    dataset_x = parepyco.sampling(n_samples=n_samples, model=model,
                                    variables_setup=variables_settings)

    # Starting variables
    capacity = np.zeros((len(dataset_x), n_constraints))
    demand = np.zeros((len(dataset_x), n_constraints))
    state_limit = np.zeros((len(dataset_x), n_constraints))
    indicator_function = np.zeros((len(dataset_x), n_constraints))

    # Singleprocess Objective Function evaluation
    for id, sample in enumerate(dataset_x):
        capacity_i, demand_i, state_limit_i = obj(list(sample), none_variable)
        capacity[id, :] = capacity_i.copy()
        demand[id, :] = demand_i.copy()
        state_limit[id, :] = state_limit_i.copy()
        indicator_function[id, :] = [1 if value <= 0 else 0 for value in state_limit_i]

    # Storage all results (horizontal stacking)
    results = np.hstack((dataset_x, capacity, demand, state_limit, indicator_function))

    # Transforming time results in dataframe X_i T_i R_i S_i G_i I_i
    if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
        tam = int(len(results) / n_samples)
        line_i = 0
        line_j = tam
        result_all = []
        for i in range(n_samples):
            i_sample_in_temp = results[line_i:line_j, :]
            i_sample_in_temp = i_sample_in_temp.T
            line_i += tam
            line_j += tam
            i_sample_in_temp = i_sample_in_temp.flatten().tolist()
            result_all.append(i_sample_in_temp)
        results_about_data = pd.DataFrame(result_all)
    else:
        results_about_data = pd.DataFrame(results)

    # Rename columns in dataframe
    column_names = []
    for i in range(n_dimensions):
        if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
            for j in range(time_analysis):
                column_names.append(f'X_{i}_t={j}')
        else:
            column_names.append(f'X_{i}')
    if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
        for i in range(time_analysis):
            column_names.append(f'STEP_t_{i}') 
    for i in range(n_constraints):
        if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
            for j in range(time_analysis):
                column_names.append(f'R_{i}_t={j}')
        else:
            column_names.append(f'R_{i}')
    for i in range(n_constraints):
        if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
            for j in range(time_analysis):
                column_names.append(f'S_{i}_t={j}')
        else:
            column_names.append(f'S_{i}')
    for i in range(n_constraints):
        if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
            for j in range(time_analysis):
                column_names.append(f'G_{i}_t={j}')
        else:
            column_names.append(f'G_{i}')
    for i in range(n_constraints):
        if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
            for j in range(time_analysis):
                column_names.append(f'I_{i}_t={j}')
        else:
            column_names.append(f'I_{i}')
    results_about_data.columns = column_names

    # First Barrier Failure (FBF) or non-dependent time reliability analysis
    if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME', 'LHS-TIME', 'LHS_TIME', 'LHS TIME']:
        results_about_data, _ = parepyco.fbf(algorithm, n_constraints, time_analysis, results_about_data)
     
    return results_about_data


def sampling_algorithm_structural_analysis(setup: dict) -> tuple[pd.DataFrame, list, list]:
    """
    This function creates the samples and evaluates the limit state functions in structural reliability problems.

    Args:
        setup (Dictionary): Setup settings.
        'number of samples' (Integer): Number of samples (key in setup dictionary)
        'numerical model' (Dictionary): Numerical model settings (key in setup dictionary)
        'variables settings' (List): Variables settings (key in setup dictionary)
        'number of state limit functions or constraints' (Integer): Number of state limit functions or constraints  
        'none_variable' (None, list, float, dictionary, str or any): None variable. User can use this variable in objective function (key in setup dictionary)           
        'objective function' (Python function): Objective function. The PAREpy user defined this function (key in setup dictionary)
        'name simulation' (String or None): Output filename (key in setup dictionary)
    
    Returns:    
        results_about_data (DataFrame): Results about reliability analysis
        failure_prob_list (List): Failure probability list
        beta_list (List): Beta list
    """

    try:
        # Setup verification
        if not isinstance(setup, dict):
            raise TypeError('The setup parameter must be a dictionary.')

        # Keys verification
        for key in setup.keys():
            if key not in ['objective function',
                           'number of samples',
                           'numerical model',
                           'variables settings',
                           'number of state limit functions or constraints',
                           'none variable',
                           'type process',
                           'name simulation'
                          ]:
                raise ValueError("""The setup parameter must have the following keys:
                                    - objective function;
                                    - number of samples;
                                    - numerical model;
                                    - variables settings;
                                    - number of state limit functions or constraints;
                                    - none variable;
                                    - type process;
                                    - name simulation"""
                                )

        # Number of samples verification
        if not isinstance(setup['number of samples'], int):
            raise TypeError('The key "number of samples" must be an integer.')

        # Numerical model verification
        if not isinstance(setup['numerical model'], dict):
            raise TypeError('The key "numerical model" must be a dictionary.')

        # Variables settings verification
        if not isinstance(setup['variables settings'], list):
            raise TypeError('The key "variables settings" must be a list.')

        # Number of state limit functions or constraints verification
        if not isinstance(setup['number of state limit functions or constraints'], int):
            raise TypeError('The key "number of state limit functions or constraints" must be an integer.')
        
        # Objective function verification
        if not callable(setup['objective function']):
            raise TypeError('The key "objective function" must be Python function.')        
        
        # Name simulation verification
        if not isinstance(setup['name simulation'], (str, type(None))):
            raise TypeError('The key "name simulation" must be a None or string.')
        parepyco.log_message('Checking inputs completed!')

        # Multiprocessing sampling algorithm
        parepyco.log_message('Started State Limit Function evaluation (g)...')
        total_samples = setup['number of samples']
        algorithm = setup['numerical model']['model sampling']
        div = total_samples // 10
        mod = total_samples % 10
        setups = []
        for i in range(10):
            new_setup = copy.deepcopy(setup)
            if i == 9:
                samples = div + mod
            else:
                samples = div
            new_setup['number of samples'] = samples
            setups.append(new_setup)
        start_time = time.perf_counter()
        with Pool() as pool:
            results = pool.map(sampling_algorithm_structural_analysis_kernel, setups)
        end_time = time.perf_counter()
        results_about_data = pd.concat(results, ignore_index=True)
        final_time = end_time - start_time
        parepyco.log_message(f'Finished State Limit Function evaluation (g) in {final_time:.2e} seconds!')

        # Failure probability and beta index calculation
        parepyco.log_message('Started evaluation beta reliability index and failure probability...')
        start_time = time.perf_counter()
        failure_prob_list, beta_list = parepyco.calc_pf_beta(results_about_data, algorithm.upper(), setup['number of state limit functions or constraints'])
        end_time = time.perf_counter()
        final_time = end_time - start_time
        parepyco.log_message(f'Finished evaluation beta reliability index and failure probability in {final_time:.2e} seconds!')

        # Save results in .txt file
        if setup['name simulation'] is not None:
            name_simulation = setup['name simulation']
            file_name = str(datetime.now().strftime('%Y%m%d-%H%M%S'))
            file_name_txt = f'{name_simulation}_{algorithm.upper()}_{file_name}.txt'
            results_about_data.to_csv(file_name_txt, sep='\t', index=False)
            parepyco.log_message(f'Voilà!!!!....simulation results are saved in {file_name_txt}')
        else:
            parepyco.log_message('Voilà!!!!....simulation results were not saved in a text file!')

        return results_about_data, failure_prob_list, beta_list

    except (Exception, TypeError, ValueError) as e:
        print(f"Error: {e}")
        return None, None, None


def concatenates_txt_files_sampling_algorithm_structural_analysis(setup: dict) -> tuple[pd.DataFrame, list, list]:
    """
    Concatenates .txt files generated by the sampling_algorithm_structural_analysis algorithm, and calculates probabilities of failure and reliability indexes based on the data.

    Args:
        setup (Dictionary): Setup settings.
        'folder_path' (String): Path to the folder containing the .txt files (key in setup dictionary)
        'number of state limit functions or constraints' (Integer): Number of state limit functions or constraints  
        'simulation name' (String or None): Name of the simulation (key in setup dictionary)
    
    Returns:    
        results_about_data (DataFrame): A DataFrame containing the concatenated results from the .txt files.
        failure_prob_list (List): A list containing the calculated failure probabilities for each indicator function.
        beta_list (List): A list containing the calculated reliability indices (beta) for each indicator function.
    """

    try:
        # General settings
        if not isinstance(setup, dict):
            raise TypeError('The setup parameter must be a dictionary.')

        folder_path = setup['folder_path']
        algorithm = setup['numerical model']['model sampling']
        n_constraints = setup['number of state limit functions or constraints']

        # Check folder path
        if not os.path.isdir(folder_path):
            raise FileNotFoundError(f'The folder path {folder_path} does not exist.')

        # Concatenate files
        start_time = time.perf_counter()
        parepyco.log_message('Uploading files!')
        results_about_data = pd.DataFrame()
        for file_name in os.listdir(folder_path):
            # Check if the file has a .txt extension
            if file_name.endswith('.txt'):
                file_path = os.path.join(folder_path, file_name)
                temp_df = pd.read_csv(file_path, delimiter='\t')
                results_about_data = pd.concat([results_about_data, temp_df], ignore_index=True)
        end_time = time.perf_counter()
        final_time = end_time - start_time
        parepyco.log_message(f'Finished Upload in {final_time:.2e} seconds!')

        # Failure probability and beta index calculation
        parepyco.log_message('Started evaluation beta reliability index and failure probability...')
        start_time = time.perf_counter()
        failure_prob_list, beta_list = parepyco.calc_pf_beta(results_about_data, algorithm.upper(), n_constraints)
        end_time = time.perf_counter()
        final_time = end_time - start_time
        parepyco.log_message(f'Finished evaluation beta reliability index and failure probability in {end_time - start_time:.2e} seconds!')

        # Save results in .txt file
        if setup['name simulation'] is not None:
            name_simulation = setup['name simulation']
            file_name = str(datetime.now().strftime('%Y%m%d-%H%M%S'))
            file_name_txt = f'{name_simulation}_{algorithm.upper()}_{file_name}.txt'
            results_about_data.to_csv(file_name_txt, sep='\t', index=False)
            parepyco.log_message(f'Voilà!!!!....simulation results are saved in {file_name_txt}')
        else:
            parepyco.log_message('Voilà!!!!....simulation results were not saved in a text file!')

        return results_about_data, failure_prob_list, beta_list

    except (Exception, TypeError, ValueError) as e:
        print(f"Error: {e}")
        return None, None, None


def sobol_algorithm(setup):
    """
    This function calculates the Sobol indices in structural reliability problems.

    Args:
        setup (Dictionary): Setup settings.
        'number of samples' (Integer): Number of samples (key in setup dictionary)
        'variables settings' (List): Variables settings, listed as dictionaries (key in setup dictionary)
        'number of state limit functions or constraints' (Integer): Number of state limit functions or constraints (key in setup dictionary)
        'none variable' (None, list, float, dictionary, str or any): None variable. User can use this variable in objective function (key in setup dictionary)
        'objective function' (Python function): Objective function defined by the user (key in setup dictionary)

    Returns:
        dict_sobol (DataFrame): A dictionary containing the first-order and total-order Sobol sensitivity indixes for each input variable.
    """
    n_samples = setup['number of samples']
    obj = setup['objective function']
    none_variable = setup['none variable']

    dist_a = sampling_algorithm_structural_analysis_kernel(setup)
    dist_b = sampling_algorithm_structural_analysis_kernel(setup)
    y_a = dist_a['G_0'].to_list()
    y_b = dist_b['G_0'].to_list()
    f_0_2 = (sum(y_a) / n_samples) ** 2

    A = dist_a.drop(['R_0', 'S_0', 'G_0', 'I_0'], axis=1).to_numpy()
    B = dist_b.drop(['R_0', 'S_0', 'G_0', 'I_0'], axis=1).to_numpy()
    K = A.shape[1]

    s_i = []
    s_t = []
    p_e = []
    for i in range(K):
        C = np.copy(B) 
        C[:, i] = A[:, i]
        y_c_i = []
        for j in range(n_samples):
            _, _, g = obj(list(C[j, :]), none_variable)
            y_c_i.append(g[0])  
        
        y_a_dot_y_c_i = [y_a[m] * y_c_i[m] for m in range(n_samples)]
        y_b_dot_y_c_i = [y_b[m] * y_c_i[m] for m in range(n_samples)]
        y_a_dot_y_a = [y_a[m] * y_a[m] for m in range(n_samples)]
        s_i.append((1/n_samples * sum(y_a_dot_y_c_i) - f_0_2) / (1/n_samples * sum(y_a_dot_y_a) - f_0_2))
        s_t.append(1 - (1/n_samples * sum(y_b_dot_y_c_i) - f_0_2) / (1/n_samples * sum(y_a_dot_y_a) - f_0_2))

    s_i = [float(i) for i in s_i]
    s_t = [float(i) for i in s_t]
    dict_sobol = pd.DataFrame(
        {'s_i': s_i,
         's_t': s_t}
    )

    return dict_sobol


def generate_factorial_design(level_dict):
    """
    Generates a full factorial design based on the input dictionary of variable levels. The function computes all possible combinations of the provided levels for each variable and returns them in a structured DataFrame.

    Args:
        level_dict (Dictionary): A dictionary where keys represent variable names, and values are lists, arrays, or sequences representing the levels of each variable.

    Returns:
        DataFrame: A dictionary containing all possible combinations of the levels provided in the input dictionary. Each column corresponds to a variable defined in level_dict. And each row represents one combination of the factorial design.
    """
    combinations = list(itertools.product(*level_dict.values()))
    df = pd.DataFrame(combinations, columns=level_dict.keys())

    return df


def deterministic_algorithm_structural_analysis(setup: dict) -> tuple[pd.DataFrame, float, int]:
    """
    This function performs a deterministic structural reliability analysis using an iterative algorithm.
    It calculates the reliability index (`beta`), the probability of failure (`pf`), and returns a DataFrame
    containing the results of each iteration.

    Args:
        setup (Dictionary): setup settings.
        'tolerance' (float): The convergence tolerance for the algorithm (key in setup dictionary).
        'max iterations' (int): The maximum number of iterations allowed (key in setup dictionary).
        'numerical model' (Any): The numerical model used for the analysis (user-defined) (key in setup dictionary).
        'variables settings' (List[dict]): Variables settings, listed as dictionaries (key in setup dictionary).
        'number of state limit functions or constraints' (int): Number of state limit functions or constraints (key in setup dictionary).
        'none variable' (None, list, float, dictionary, str or any): None variable. User can use this variable in objective function (key in setup dictionary).
        'objective function' (Python function): Objective function defined by the user (key in setup dictionary).
        'gradient objective function' (Callable): The gradient of the objective function (key in setup dictionary). 
        'name simulation' (str): A name or identifier for the simulation (key in setup dictionary).

    Returns:
        results_df (pd.DataFrame): A DataFrame with the results of each iteration.
        pf (float): The probability of failure calculated using the final reliability index.
        beta (int): The final reliability index.
    """
    try:
        if not isinstance(setup, dict):
            raise TypeError('The setup parameter must be a dictionary.')
        
        required_keys = [
            'tolerance', 'max iterations', 'numerical model', 'variables settings',
            'number of state limit functions or constraints', 'none variable',
            'objective function', 'gradient objective function', 'name simulation'
        ]
        
        for key in required_keys:
            if key not in setup:
                raise ValueError(f'The setup parameter must have the key: {key}.')
        
        variables = setup['variables settings']
        if not isinstance(variables, list):
            raise TypeError('The "variables settings" must be a list.')
        
        for i, var in enumerate(variables):
            if not isinstance(var, dict):
                raise TypeError('Each variable in "variables settings" must be a dictionary.')
            
            if 'parameters' not in var or not isinstance(var['parameters'], dict):
                raise ValueError('Each variable must have a "parameters" key with a dictionary value.')
            
            if 'mean' not in var['parameters'] or 'sigma' not in var['parameters']:
                raise ValueError('Each variable must have "mean" and "sigma" in its parameters.')
            
            if 'type' not in var:
                raise ValueError('Each variable must have a "type" key.')
            
            if var['type'] not in ['normal', 'lognormal', 'gumbel max', 'gumbel min']:
                raise ValueError('The variable type must be one of: "normal", "lognormal", "gumbel max", "gumbel min".')
        

        mu = []
        sigma = []
        tol = setup['tolerance']
        max_iter = setup['max iterations']
        none_variable = setup['none variable']
        obj = setup['objective function']
        grad_obj = setup['gradient objective function']
        params_adapt = {}
        
        for i, var in enumerate(variables):
            mean = var['parameters']['mean']
            std = var['parameters']['sigma']
            mu.append(mean)
            sigma.append(std)
            
            if var['type'] == 'normal':
                params_adapt[f'var{i}'] = {
                    'type': 'normal',
                    'params': {
                        'mu': mean,
                        'sigma': std
                    }
                }
            elif var['type'] == 'lognormal':
                epsilon = np.sqrt(np.log(1 + (std / mean) ** 2))
                lambdaa = np.log(mean) - 0.5 * epsilon ** 2
                params_adapt[f'var{i}'] = {
                    'type': 'lognormal',
                    'params': {
                        'lambda': float(lambdaa),
                        'epsilon': float(epsilon)
                    }
                }
            elif var['type'] == 'gumbel max':
                gamma = 0.577215665  
                beta = np.pi / (np.sqrt(6) * std)
                alpha = mean - gamma / beta
                params_adapt[f'var{i}'] = {
                    'type': 'gumbel max',
                    'params': {
                        'alpha': float(alpha),
                        'beta': float(beta)
                    }
                }
            elif var['type'] == 'gumbel min':
                gamma = 0.577215665 
                beta = np.pi / (np.sqrt(6) * std)
                alpha = mean + gamma / beta
                params_adapt[f'var{i}'] = {
                    'type': 'gumbel min',
                    'params': {
                        'alpha': float(alpha),
                        'beta': float(beta)
                    }
                }
                 

        # for index, value in params_adapt.items():
        #     print(f"index: {index}, \nvalue: {value}")

        # print(f"mu: {mean}, \nsigma: {std}, \ntol: {tol}, \nmax_iter: {max_iter}, \nnone_variable: {none_variable}")
        
        # Fixed in this algorithm
        beta_list = [10000]
        error = 1000
        iter = 0
        step = 1

        x = np.transpose(np.array([mu.copy()]))
        mu = x.copy()
        jacobian_xy = np.diag(sigma)
        jacobian_xy_trans = np.transpose(jacobian_xy)
        jacobian_yx = np.linalg.inv(jacobian_xy)
        y = jacobian_yx @ (x - mu)
        x = jacobian_xy @ y + mu

        while (error > tol and iter < max_iter):
            beta = np.linalg.norm(y)
            beta_list.append(beta)
            g_y = obj(x.flatten().tolist())
            grad_g_x = grad_obj(x.flatten().tolist())
            grad_g_y = np.dot(jacobian_xy_trans, np.transpose(np.array([grad_g_x])))
            num = (np.transpose(grad_g_y) @ y - g_y)
            norm = np.linalg.norm(grad_g_y)
            norm2 = norm ** 2
            #alpha = grad_g_y / norm
            #aux = g_y / norm
            #y = -alpha * (beta + aux)
            d = grad_g_y @ (num / norm2) - y
            #step = minimize_scalar(f_alpha, bounds=(.001, 1), args=([y, d]), method='bounded')
            #print(step.x)
            #y += step.x * d
            y += step * d
            error = np.abs(beta_list[iter + 1] - beta_list[iter])
            x = jacobian_xy @ y + mu

            aux = {
                'iteration': iter,
                **{f'x_{i}': float(x_value.item()) for i, x_value in enumerate(x)},
                'error': error,
                'beta': beta
            }
            if iter == 0:
                results_df = pd.DataFrame([aux])
            else:
                results_df = pd.concat([results_df, pd.DataFrame([aux])], ignore_index=True)

            iter += 1
        pf = parepyco.pf_equation(beta)
        
        return results_df, float(pf), float(beta)
            
    except (Exception, TypeError, ValueError) as e:
        print(f"Error: {e}")
        return None, None, None