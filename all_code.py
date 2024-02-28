import netCDF4
import os
import subprocess
import shutil
import matplotlib.pyplot as plt
import numpy as np
import re
from skopt import gp_minimize as BO
from skopt.utils import use_named_args
from skopt.space import Real, Integer, Categorical
from typing import Callable

def get_GT():
    GTDIR = 'Ground_Truth'
    if 'ground_truth.npy' in os.listdir(GTDIR):
        return np.load('Ground_Truth/ground_truth.npy')
    pathToGT = os.path.join(GTDIR, 'sgpradflux10long_area_mean.c2.20090506_1200UTC.nc')
    GT = netCDF4.Dataset(pathToGT)
    npGT = np.array(GT['obs_swdtot'])
    np.save('Ground_Truth/ground_truth.npy', npGT, allow_pickle=True, fix_imports=True)
    return npGT

Xs = list(range(50))

def get_true_data() -> np.ndarray:
    return np.array([(x * 2) + 3 for x in Xs])

def run_model(params) -> np.ndarray:
    return np.array([(x * params['m']) + params['b'] for x in Xs])

dim_vdis     = Real(low=.01, high=1.40, name='vdis')
dim_beta_con = Real(low=1e+20, high=1e+24, name='beta_con', prior='log-uniform')
dimensions  = [dim_vdis, dim_beta_con]

def save_strat(res, folder):
    if folder not in os.listdir():
        os.mkdir(folder)
    np.save(os.path.join(folder, "func_vals.npy"), res['func_vals'])
    plt.plot(res['func_vals'])
    print(res['x'], res['fun'])
    #plt.title("found {:.5f} at {:.3f}".format(res['fun'], res['x']))
    plt.xlabel('epoch')
    plt.ylabel('MSE')
    plt.savefig(os.path.join(folder,'optimization_path.png'))
    return 1

@use_named_args(dimensions=dimensions)
def evaluate(**params):
    pred = run_model(params)[:,-1]
    gt   = get_GT()
    print("\n--- EVALUATING CURRENT RESULTS ---")  
    MSE = np.mean((gt - pred)**2)
    print(params)
    print(f"--- MSE: {MSE} ---\n")
    return MSE

def Bayesian_Opt(iterations=10, seed=123):
    result = BO(func=evaluate, dimensions=dimensions, n_calls=np.int32(iterations), noise=0.1, random_state=np.int32(seed))
    print("BEST PARAMS:", result['x'])
    print("EVAL:", result['fun'])
    if "Bayesian_Opt" not in os.listdir():
        os.mkdir("Bayesian_Opt")
    return result


def kiefer_wolfowitz1d(iterations = 10, seed = 123):
    vdis = .3
    beta_con = 1.0e24
    func_vals = []
    initial_result = evaluate([vdis, beta_con])
    func_vals.append(initial_result)
    best_fun = initial_result
    best_x = [vdis, beta_con]
    
    for n in range(1,iterations+1):
        cn = n**(-1/3)*.3/2
        N1 = evaluate([np.clip(vdis + cn, 0.01, 1.4) ,beta_con])
        N2 = evaluate([np.clip(vdis - cn, 0.01, 1.4) ,beta_con])
        func_vals.append((N1 + N2) / 2)
        if best_fun > func_vals[-1]:
            func_vals.append(best_fun)
            best_x = [vdis, beta_con]
        vdis = np.clip(vdis + 1/n * (N1 - N2) / (2*cn), .01, 1.4)

    if "Kiefer_Wolfowitz1D" not in os.listdir():
        os.mkdir("Kiefer_Wolfowitz1D")
    return {'func_vals': np.array(func_vals), 'fun': best_fun, 'x': best_x}

def rmsprop(evaluate: Callable, num_iterations=1000, lr=0.01, beta=0.9, epsilon=1e-8):
    global dimensions
    def clip_params(params, dims):
        # Clip parameters to stay within the bounds defined by dimensions
        for i, dim in enumerate(dims):
            params[i] = np.clip(params[i], dim.low, dim.high)
        return params
    # Initialize parameters within the bounds
    params = np.array([dim.rvs for dim in dimensions])
    moving_avg_sq_grad = np.zeros(len(dimensions))
    loss = []
    for iteration in range(num_iterations):
        MSE = evaluate(params)
        loss.append(MSE)
        gradients = np.gradient(MSE)
        moving_avg_sq_grad = beta * moving_avg_sq_grad + (1 - beta) * (gradients ** 2)
        params -= (lr / (np.sqrt(moving_avg_sq_grad) + epsilon)) * gradients
        params = clip_params(params, dimensions)
        return {'func_vals': np.array(loss), 'fun': loss[-1], 'x': params}

def optimize(strategy, iterations = 10, seed=5):
    strategies = ['BO', 'KW', 'KW1D']
    if strategy == 'BO':
        return Bayesian_Opt(iterations, seed)
    #if strategy == 'KW':
        #return kiefer_wolfowitz(iterations, seed)
    if strategy == 'KW1D':
        return kiefer_wolfowitz1d(iterations, seed)
    print(f"Currently supported strategies are:\n{', '.join(strategies)}")
    


def process(wrffolder,epoch_name):
    def get_time_from_filename(filename):
        m = re.match(r"wrfout_d01_2009-05-(\d\d)_(\d\d):(\d\d):(\d\d)", filename)
        return (int(m[1]) - 6) * 24 + int(m[2]) + int(m[3]) / 60 + int(m[4]) / 3600

    files = [file for file in os.listdir(wrffolder) if file.startswith("wrfout")]
    data = []
    for outfile in files:
        nc = netCDF4.Dataset(os.path.join(wrffolder, outfile))
        data.append([get_time_from_filename(outfile), np.mean(nc["SWDOWN"][0, :]), np.mean(nc["SWDDIR"][0, :]), np.mean(nc["SWDDIF"][0,:]), np.mean(nc["SWDDIR"][0, :]) + np.mean(nc["SWDDIF"][0,:])])
    data = np.array(sorted(data, key=lambda x: x[0]))
    data = data[(data[:, 0] >= 12) & (data[:, 0] <= 27)]
    np.save(epoch_name + '.npy', data)
    return data

def show_run(run, name, GT = False, scatter = False):
    plt.clf()
    if GT:
        gt = get_GT()
        plt.plot(run[:,0], gt, label = "GT")
        plt.title("DOWN MSE: {:.2} TOT MSE: {:.2}".format(np.mean((gt - run[:,1])**2), np.mean((gt - run[:,4])**2)))
    if scatter:
        plt.scatter(run[:,0], run[:,1], label = "SWDOWN")
        plt.scatter(run[:,0], run[:,4], label = "DIR + DIF")
    else:
        plt.scatter(run[:,0], run[:,1], label = "SWDOWN")
        plt.scatter(run[:,0], run[:,4], label = "DIR + DIF")
    plt.legend()
    plt.savefig(name + '.jpg')

def update_params(params, PATH):    
    if 'beta_con' in params:
        params['beta_con'] = "{:.5E}".format(params['beta_con']).replace("E+", "E")
    with open('template.input', 'r') as reader:
        with open(f'{PATH}/namelist.input', 'w') as writer:
            writer.write(reader.read().format(**params))    

def run_WRF(PATH, max_tries, num_cores = 4):
    print(" - Run Real")
    subprocess.call(f"mpiexec -np {num_cores} {PATH}/real.exe".split(), cwd=PATH)
    print(" - Run WRF")
    for _ in range(max_tries):
        process = subprocess.call(f"mpiexec -np {num_cores} {PATH}/wrf.exe".split(), cwd=PATH)
        if process == 0:
            return 1
    print(f"FAILED TO RUN IN {max_tries} ATTEMPTS")
    return 0

def run_model(params: dict) -> np.array:
    epoch_name = "WRF" + "-".join([str(x) for x in params.values()])
    
    if epoch_name + '.npy' in os.listdir('cached_runs'):
        return np.load(os.path.join('cached_runs', epoch_name+'.npy'))
    PATH = "/home/capstoneii/Build_WRF/WRF/run"
    update_params(params, PATH)
    print(f"{params}")
    
    if not run_WRF(PATH, 10):
        exit()
    
    # Retrive Output Data and return
    data = process(PATH, epoch_name)
    cache_data(epoch_name + '.npy')
    return data

def cache_data(name):
    shutil.copy(name, 'cached_runs')

if __name__ == "__main__":
    #save_strat(optimize('KW1D', 8), "Kiefer_Wolfowitz1D")
    #save_strat(optimize('KW', 10), "Kiefer_Wolfowitz")
    save_strat(optimize('BO', 30), "Bayesian_Opt")