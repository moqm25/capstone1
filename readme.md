# Capstone I | CS492

This repository contains the necessary files and data for our project. Here's a brief overview of the directory structure and the purpose of each file and folder:

## Root Directory

- `.gitignore`: This file is used to exclude certain files from the Git repository.
- `readme.md`: This is the file you're currently reading. It provides an overview of the project directory.
- `upload_to_github.py`: This Python script is used to upload files to the GitHub repository.
- `WRF-Solar-BNL_Install.bash`: This Bash script is used to install the WRF-Solar-BNL software.

## Ground Truth

The `ground_truth` directory contains files related to the ground truth data of our project:

- `ground_truth_data.npy`: This file contains the ground truth data in NumPy format.
- `ground_truth.jpg` and `ground_truth_subplot.jpg`: These are visual representations of the ground truth data.
- `plot_ground_truth.py`: This Python script is used to generate the ground truth plots.
- `sgpradflux10long_area_mean.c2.20090506_1200UTC.nc`: This file contains specific ground truth data.

## WRF-Data-netCDF4

The `WRF-Data-netCDF4` directory contains output files from the Weather Research and Forecasting (WRF) model. Each file represents the model output for a specific time, as indicated by the timestamp in the file name.
