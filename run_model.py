# import matplotlib.pyplot as plt
# import netCDF4
# import numpy as np
# import os
# import subprocess

# def run_WRF(PATH, num_cores=4, max_tries=10):
#     print(" - Run Real")
#     subprocess.call(f"mpiexec -np {num_cores} {PATH}/real.exe".split(), cwd=PATH)
#     print(" - Run WRF")
#     for _ in range(max_tries):
#         process = subprocess.call(f"mpiexec -np {num_cores} {PATH}/wrf.exe".split(), cwd=PATH)
#         if process == 0:
#             return 1
#     print(f"FAILED TO RUN IN {max_tries} ATTEMPTS")
#     return 0

# def get_data(wrffolder):
#     files = [file for file in os.listdir(wrffolder) if file.startswith("wrfout")]
#     print(files)
#     data = {}
#     for outfile in files:
#         nc = netCDF4.Dataset(os.path.join(wrffolder, outfile))
#         for var in nc.variables:
#             # Check if the variable data is numeric
#             if np.issubdtype(nc[var].dtype, np.number):
#                 if var not in data:
#                     data[var] = []
#                 data[var].append(np.mean(nc[var][:]))
#             else:
#                 # If the variable data is not numeric, try to convert it to numeric
#                 try:
#                     numeric_data = nc[var][:].astype(np.float64)  # Use np.float64 instead of np.float
#                     if var not in data:
#                         data[var] = []
#                     data[var].append(np.mean(numeric_data))
#                 except ValueError:
#                     # If the conversion fails, skip this variable
#                     continue
#     for var in data:
#         data[var] = np.array(data[var])
#     return data


# def show_data(name, data, output_dir):
#     fig, axs = plt.subplots(2, 2, figsize=(15, 10))
#     axs[0, 0].plot(data['SWDOWN'], label="SWDOWN")
#     axs[0, 0].set_title('SWDOWN')
#     axs[0, 1].plot(data['SWDDIR'], label="SWDDIR")
#     axs[0, 1].set_title('SWDDIR')
#     axs[1, 0].plot(data['SWDDIF'], label="SWDDIF")
#     axs[1, 0].set_title('SWDDIF')
#     axs[1, 1].plot(data['SWDDNI'], label="SWDDNI")
#     axs[1, 1].set_title('SWDDNI')
#     fig.tight_layout()
#     plt.savefig(os.path.join(output_dir, name + '_subplot.jpg'))

#     plt.figure(figsize=(10, 6))
#     plt.plot(data['SWDOWN'], label="SWDOWN")
#     plt.plot(data['SWDDIR'], label="SWDDIR")
#     plt.plot(data['SWDDIF'], label="SWDDIF")
#     plt.plot(data['SWDDNI'], label="SWDDNI")
#     plt.xlabel('Time (hours)')
#     plt.ylabel('Solar Irradiance (W/m^2)')
#     plt.title('WRF Output')
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(os.path.join(output_dir, name + '.jpg'))

# if __name__ == '__main__':
#     # PATH = "/home/capstonei/CS492_Tasks/WRF-Computer-Steering/Build_WRF/WRF/run" # Path to the run directory where the models are stored
#     OUTPUT_DIR = "/home/capstonei/CS492_Tasks/output_plots" # Path to the directory where the plots will be saved
#     # if not run_WRF(PATH, 4):
#     #     exit()
#     TEST_PATH = "/home/capstonei/CS492_Tasks/WRF-Data-netCDF4"
#     # data = get_data(PATH)
#     data = get_data(TEST_PATH)
#     show_data('WRF_output', data, OUTPUT_DIR)
import os
import re
import numpy as np
import netCDF4
import matplotlib.pyplot as plt
import shutil

def copy_files(src_folder, dest_folder):
    files = [file for file in os.listdir(src_folder) if file.startswith("wrfout") ]
    for file in files:
        shutil.copy(os.path.join(src_folder, file), dest_folder)

def get_time_from_filename(filename):
    m = re.match(r"wrfout_d01_2009-05-(\d\d)_(\d\d):(\d\d):(\d\d)", filename)
    return (int(m[1]) - 6) * 24 + int(m[2]) + int(m[3]) / 60 + int(m[4]) / 3600

def process(wrffolder, epoch_name):
    files = [file for file in os.listdir(wrffolder) if file.startswith("wrfout")]
    data = []
    for outfile in files:
        nc = netCDF4.Dataset(os.path.join(wrffolder, outfile))
        data.append([get_time_from_filename(outfile), np.mean(nc["SWDOWN"][0, :]), np.mean(nc["SWDDIR"][0, :]), np.mean(nc["SWDDIF"][0,:]), np.mean(nc["SWDDIR"][0, :]) + np.mean(nc["SWDDIF"][0,:])])
    data = np.array(sorted(data, key=lambda x: x[0]))
    data = data[(data[:, 0] >= 12) & (data[:, 0] <= 27)]
    np.save(epoch_name + '.npy', data)
    return data

def show_run(run, name, output_dir):
    plt.clf()
    plt.scatter(run[:,0], run[:,1], label = "SWDOWN")
    plt.scatter(run[:,0], run[:,4], label = "DIR + DIF")
    plt.xlabel('Time (hours)')  # x-axis label
    plt.ylabel('Solar Irradiance (W/m^2)')  # y-axis label
    plt.title('WRF Output')  # title
    plt.legend()
    plt.savefig(os.path.join(output_dir, name + '.jpg'))

if __name__ == '__main__':
    SRC_PATH = "/home/capstonei/CS492_Tasks/WRF-Computer-Steering/Build_WRF/WRF/run" # Path to the run directory where the models are stored and WRF outs are
    DEST_PATH = "/home/capstonei/CS492_Tasks/WRF-Data-netCDF4" # Path to the directory where the .nc files will be copied to
    OUTPUT_DIR = "/home/capstonei/CS492_Tasks/output_plots" # Path to the directory where the plots will be saved
    copy_files(SRC_PATH, DEST_PATH)
    run = process(DEST_PATH, 'epoch_name')
    show_run(run, 'model_predictions', OUTPUT_DIR)
