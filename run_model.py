import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import os
import subprocess

def run_WRF(PATH, num_cores=4):
    print(" - Run Real")
    subprocess.call(f"mpirun -np {num_cores} {PATH}/real.exe".split(), cwd=PATH)
    print(" - Run WRF")
    subprocess.call(f"mpirun -np {num_cores} {PATH}/wrf.exe".split(), cwd=PATH)

def get_data(wrffolder):
    files = [file for file in os.listdir(wrffolder) if file.startswith("wrfout")]
    data = {}
    for outfile in files:
        nc = netCDF4.Dataset(os.path.join(wrffolder, outfile))
        for var in nc.variables:
            # Check if the variable data is numeric
            if np.issubdtype(nc[var].dtype, np.number):
                if var not in data:
                    data[var] = []
                data[var].append(np.mean(nc[var][:]))
            else:
                # If the variable data is not numeric, try to convert it to numeric
                try:
                    numeric_data = nc[var][:].astype(np.float)
                    if var not in data:
                        data[var] = []
                    data[var].append(np.mean(numeric_data))
                except ValueError:
                    # If the conversion fails, skip this variable
                    continue
    for var in data:
        data[var] = np.array(data[var])
    return data

def show_data(name, data, output_dir):
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs[0, 0].plot(data['SWDOWN'], label="SWDOWN")
    axs[0, 0].set_title('SWDOWN')
    axs[0, 1].plot(data['SWDDIR'], label="SWDDIR")
    axs[0, 1].set_title('SWDDIR')
    axs[1, 0].plot(data['SWDDIF'], label="SWDDIF")
    axs[1, 0].set_title('SWDDIF')
    axs[1, 1].plot(data['SWDDNI'], label="SWDDNI")
    axs[1, 1].set_title('SWDDNI')
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, name + '_subplot.jpg'))

    plt.figure(figsize=(10, 6))
    plt.plot(data['SWDOWN'], label="SWDOWN")
    plt.plot(data['SWDDIR'], label="SWDDIR")
    plt.plot(data['SWDDIF'], label="SWDDIF")
    plt.plot(data['SWDDNI'], label="SWDDNI")
    plt.xlabel('Time (hours)')
    plt.ylabel('Solar Irradiance (W/m^2)')
    plt.title('WRF Output')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, name + '.jpg'))

if __name__ == '__main__':
    PATH = "/home/capstonei/CS492_Tasks/WRF-Computer-Steering/Build_WRF/WRF/run" # Path to the run directory where the models are stored
    OUTPUT_DIR = "/home/capstonei/CS492_Tasks/output_plots" # Path to the directory where the plots will be saved
    run_WRF(PATH, 4)
    # TEST_PATH = "WRF-Data-netCDF4"
    data = get_data(PATH)
    # data = get_data(TEST_PATH)
    show_data('WRF_output', data, OUTPUT_DIR)
