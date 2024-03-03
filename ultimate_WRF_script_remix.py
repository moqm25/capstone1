# Additions by Sohaib - if it works, this will be merged into the og ultimate_WRF_script.py
import os
import re
import numpy as np
import netCDF4
import matplotlib.pyplot as plt
import shutil
import subprocess
import xarray as xr
from skopt.utils import use_named_args
from skopt.space import Real
from skopt import gp_minimize as BO
from sklearn.metrics import mean_squared_error
import pandas as pd
# Importing necessary modules
print("Importing necessary modules...")

# Compiling a regular expression to match the time format in the filename
time_regex = re.compile(r"wrfout_d01_2009-05-(\d\d)_(\d\d):(\d\d):(\d\d)")
print("Compiled time regex...")

# Function to extract time from the filename
def get_time_from_filename(filename):
    print(f"Getting time from filename: {filename}")
    match = time_regex.match(filename)
    return (int(match[1]) - 6) * 24 + int(match[2]) + int(match[3]) / 60 + int(match[4]) / 3600

# Function to get ground truth data
def get_GT(GTDIR):
    print(f"Changing directory to: {GTDIR}")
    os.chdir(GTDIR)
    if 'ground_truth_data.npy' not in os.listdir(GTDIR):
        print("Ground truth data not found, generating...")
        pathToGT = os.path.join(GTDIR, 'sgpradflux10long_area_mean.c2.20090506_1200UTC.nc')
        GT = netCDF4.Dataset(pathToGT)
        data = {
            'obs_swdtot': np.array(GT['obs_swdtot']),
            'obs_swddir': np.array(GT['obs_swddir']),
            'obs_swddif': np.array(GT['obs_swddif']),
            'obs_swddni': np.array(GT['obs_swddni']),
            'obs_time': np.array(GT['obs_time'])
        }
        np.save('ground_truth_data.npy', data, allow_pickle=True, fix_imports=True)
        print("Ground truth data saved.")
    else:
        print("Ground truth data found.")

# Function to plot ground truth data
def show_GT(name, GTDIR):
    print(f"Loading ground truth data from: {GTDIR}ground_truth_data.npy")
    data = np.load(GTDIR + 'ground_truth_data.npy', allow_pickle=True).item()
    obs_swdtot = data['obs_swdtot']
    obs_swddir = data['obs_swddir']
    obs_swddif = data['obs_swddif']
    obs_swddni = data['obs_swddni']
    obs_time = data['obs_time']

    print("Plotting ground truth data...")
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs[0, 0].plot(obs_time, obs_swdtot, label="obs_swdtot")
    axs[0, 0].set_title('obs_swdtot')
    axs[0, 1].plot(obs_time, obs_swddir, label="obs_swddir")
    axs[0, 1].set_title('obs_swddir')
    axs[1, 0].plot(obs_time, obs_swddif, label="obs_swddif")
    axs[1, 0].set_title('obs_swddif')
    axs[1, 1].plot(obs_time, obs_swddni, label="obs_swddni")
    axs[1, 1].set_title('obs_swddni')
    fig.tight_layout()
    plt.savefig(name + '_subplot.jpg')
    print(f"Subplot saved as: {name}_subplot.jpg")

    plt.figure(figsize=(10, 6))
    plt.plot(obs_time, obs_swdtot, label="obs_swdtot")
    plt.plot(obs_time, obs_swddir, label="obs_swddir")
    plt.plot(obs_time, obs_swddif, label="obs_swddif")
    plt.plot(obs_time, obs_swddni, label="obs_swddni")
    plt.xlabel('Time (hours)')
    plt.ylabel('Solar Irradiance (W/m^2)')
    plt.title('Ground Truth')
    plt.legend()
    plt.tight_layout()
    plt.savefig(name + '.jpg')
    print(f"Plot saved as: {name}.jpg")

# Function to run the WRF model
def run_WRF(PATH, max_tries, num_cores = 4):
    print(f"Changing directory to: {PATH}")
    os.chdir(PATH)
    print("Running Real...")
    subprocess.call(f"mpirun -np {num_cores} {PATH}/real.exe".split(), cwd=PATH)
    print("Running WRF...")
    for _ in range(max_tries):
        process = subprocess.call(f"mpirun -np {num_cores} {PATH}/wrf.exe".split(), cwd=PATH)
        if process == 0:
            print("WRF run successful.")
            return 1
    print(f"FAILED TO RUN IN {max_tries} ATTEMPTS")
    return 0


# Function to copy files from source to destination
def copy_files(src_folder, dest_folder):
    print(f"Copying files from {src_folder} to {dest_folder}...")
    for entry in os.scandir(src_folder):
        if entry.is_file() and entry.name.startswith("wrfout"):
            shutil.copy(entry.path, dest_folder)
    print("Files copied.")

# Function to process the WRF data
def process(wrffolder, output_dir, epoch_name):
    print(f"Processing data in {wrffolder}...")
    data = []
    for entry in os.scandir(wrffolder):
        if entry.is_file() and entry.name.startswith("wrfout"):
            with netCDF4.Dataset(entry.path) as nc:
                swddir_mean = np.mean(nc["SWDDIR"][0, :])
                data.append([get_time_from_filename(entry.name), np.mean(nc["SWDOWN"][0, :]), swddir_mean, np.mean(nc["SWDDIF"][0,:]), swddir_mean + np.mean(nc["SWDDIF"][0,:])])
    data = np.array(sorted(data, key=lambda x: x[0]))
    data = data[(data[:, 0] >= 12) & (data[:, 0] <= 27)]
    np.save(output_dir + epoch_name + '.npy', data)
    print(f"Data saved as: {output_dir}{epoch_name}.npy")
    return data

# Function to show the run data
def show_run(name, output_dir):
    print(f"Loading run data from: {output_dir}{name}.npy")
    run = np.load(output_dir + name + '.npy')
    plt.clf()
    plt.plot(run[:,0], run[:,1], label = "SWDOWN")
    # plt.plot(run[:,0], run[:,4], label = "DIR + DIF")
    plt.xlabel('Time (hours)')  # x-axis label
    plt.ylabel('Solar Irradiance (W/m^2)')  # y-axis label
    plt.title('WRF Output')  # title
    plt.legend()
    plt.savefig(os.path.join(output_dir, name + '.jpg'))
    print(f"Run plot saved as: {os.path.join(output_dir, name)}.jpg")

# Function to plot ground truth and model predictions
def plot_GT_and_model(GTDIR, output_dir, model_pred_name):
    print(f"Loading ground truth data from: {GTDIR}ground_truth_data.npy")
    obs_data = np.load(GTDIR + 'ground_truth_data.npy', allow_pickle=True).item()
    obs_swdtot = obs_data['obs_swdtot']
    obs_time = obs_data['obs_time']
    print(f"Loading model prediction data from: {output_dir}{model_pred_name}.npy")
    model_pred = np.load(output_dir + model_pred_name + '.npy')
    plt.figure(figsize=(10, 6))
    plt.plot(obs_time, obs_swdtot, label="Ground Truth obs_swdtot")
    plt.plot(model_pred[:,0], model_pred[:,1], label="Model Prediction SWDOWN")
    # plt.plot(model_pred[:,0], model_pred[:,4], label="Model Prediction DIR + DIF")
    plt.xlabel('Time (hours)')
    plt.ylabel('Solar Irradiance (W/m^2)')
    plt.title('Ground Truth and Model Predictions')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir + 'GT_and_model.jpg')
    print(f"Ground truth and model predictions plot saved as: {output_dir}GT_and_model.jpg")


def get_swtot(GTDIR):
    gt_data = xr.open_dataset(GTDIR)
    solar_irradiance_data = gt_data['obs_swdtot']
    gt_swdtot = solar_irradiance_data.values
    return gt_swdtot

space  = [Real(1.02e20, 1.67e24, name='beta_con'),
          Real(0.01, 1.4, name='vdis')]

@use_named_args(space)
def objective(**params):
    vdis = params['vdis']
    beta_con = params['beta_con']
    gt = get_swtot(GTDIR)
    run_WRF(SRC_PATH, 10)
    data = process(DEST_PATH, OUTPUT_DIR, 'base_model_pred')
    df = pd.DataFrame(data)
    mse_result = mean_squared_error(gt,df.iloc[:, 1])
    print(vdis,beta_con)
    print(mse_result)
    return  mse_result

def Bayesian_Opt(iterations=10, seed=123):
    result = BO(func=objective, dimensions=space, n_calls=np.int32(iterations), noise=0.1, random_state=np.int32(seed),acq_func="EI")
    print("BEST PARAMS:", result['x'])
    print("EVAL:", result['fun'])
    if "Bayesian_Opt" not in os.listdir():
        os.mkdir("Bayesian_Opt")
    return result

# Main function
if __name__ == '__main__':
    # Define the paths
    GTDIR = '/home/capstonei/CS492_Tasks/ground_truth/'
    SRC_PATH = "/home/capstonei/CS492_Tasks/WRF-Computer-Steering/Build_WRF/WRF/run"
    DEST_PATH = "/home/capstonei/CS492_Tasks/WRF-Data-netCDF4/"
    OUTPUT_DIR = "/home/capstonei/CS492_Tasks/output_plots/"

    # Obtain Ground Truth Plots
    # get_GT(GTDIR)
    # show_GT('ground_truth', GTDIR)

    # Run the WRF Model
    # run_WRF(SRC_PATH, 10)
    #     exit()

    # Process the WRF Data
    # copy_files(SRC_PATH, DEST_PATH)
    # process(DEST_PATH, OUTPUT_DIR, 'base_model_pred')
    #show_run('base_model_pred', OUTPUT_DIR)

    # Plot Ground Truth and Model Predictions
    # plot_GT_and_model(GTDIR, OUTPUT_DIR, 'base_model_pred')
    result = Bayesian_Opt(10,123)
    print(result)