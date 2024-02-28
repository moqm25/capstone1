import os
import re
import numpy as np
import netCDF4
import matplotlib.pyplot as plt
import shutil
import subprocess

# Script was used in: /home/capstonei/CS492_Tasks


time_regex = re.compile(r"wrfout_d01_2009-05-(\d\d)_(\d\d):(\d\d):(\d\d)")  

PATH="/home/capstonei/CS492_Tasks"
os.chdir(PATH)

# write documentation
def run_WRF(PATH, max_tries, num_cores = 4):
    os.chdir(PATH)
    print(" - Run Real")
    subprocess.call(f"mpirun -np {num_cores} {PATH}/real.exe".split(), cwd=PATH)
    print(" - Run WRF")
    for _ in range(max_tries):
        process = subprocess.call(f"mpirun -np {num_cores} {PATH}/wrf.exe".split(), cwd=PATH)
        if process == 0:
            return 1
    print(f"FAILED TO RUN IN {max_tries} ATTEMPTS")
    return 0

def copy_files(src_folder, dest_folder):
    for entry in os.scandir(src_folder):
        if entry.is_file() and entry.name.startswith("wrfout"):
            shutil.copy(entry.path, dest_folder)

def get_time_from_filename(filename):
    match = time_regex.match(filename)
    return (int(match[1]) - 6) * 24 + int(match[2]) + int(match[3]) / 60 + int(match[4]) / 3600

def process(wrffolder, output_dir, epoch_name):
    data = []
    for entry in os.scandir(wrffolder):
        if entry.is_file() and entry.name.startswith("wrfout"):
            with netCDF4.Dataset(entry.path) as nc:
                swddir_mean = np.mean(nc["SWDDIR"][0, :])
                data.append([get_time_from_filename(entry.name), np.mean(nc["SWDOWN"][0, :]), swddir_mean, np.mean(nc["SWDDIF"][0,:]), swddir_mean + np.mean(nc["SWDDIF"][0,:])])
    data = np.array(sorted(data, key=lambda x: x[0]))
    data = data[(data[:, 0] >= 12) & (data[:, 0] <= 27)]
    np.save(f"{output_dir}/{epoch_name}.npy", data)
    return data

def show_run(run, name, output_dir):
    plt.clf()
    plt.plot(run[:,0], run[:,1], label = "SWDOWN")
    plt.plot(run[:,0], run[:,4], label = "DIR + DIF")
    plt.xlabel('Time (hours)')  # x-axis label
    plt.ylabel('Solar Irradiance (W/m^2)')  # y-axis label
    plt.title('WRF Output')  # title
    plt.legend()
    plt.savefig(os.path.join(output_dir, name + '.jpg'))

if __name__ == '__main__':
    SRC_PATH = "/home/capstonei/CS492_Tasks/WRF-Computer-Steering/Build_WRF/WRF/run" # Path to the run directory where the models are stored and WRF outs are
    DEST_PATH = "/home/capstonei/CS492_Tasks/WRF-Data-netCDF4" # Path to the directory where the .nc files will be copied to
    OUTPUT_DIR = "/home/capstonei/CS492_Tasks/output_plots" # Path to the directory where the plots will be saved
    # if not run_WRF(SRC_PATH, 10):
    #     exit()
    copy_files(SRC_PATH, DEST_PATH)
    run = process(DEST_PATH, OUTPUT_DIR, 'model_pred')
    show_run(run, 'model_predictions', OUTPUT_DIR)
