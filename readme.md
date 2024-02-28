# Capstone I | CS492

This repository contains the necessary files and data for our project. Here's a brief overview of the directory structure and the purpose of each file and folder:

## Root Directory

- `.gitignore`: This file is used to exclude certain files from the Git repository.
- `readme.md`: This is the file you're currently reading. It provides an overview of the project directory.
- `ultimate_WRF_script.py`: This Python script is used to run the Weather Research and Forecasting (WRF) model.
- `upload_to_github.py`: This Python script is used to upload files to the GitHub repository.

## Experimental Scripts

The `experimental_scripts` directory contains various Python scripts used for testing and development. These scripts were for experimentational purposes and are no longer updated:

- `info_obtain_test.py`: This script was used for testing data extraction.
- `plot_ground_truth.py`: This script was used to generate plots of the ground truth data.
- `plot_WRF_output.py`: This script was used to generate plots of the WRF model output.

## Ground Truth

The `ground_truth` directory contains files related to the ground truth data of our project:

- `ground_truth_data.npy`: This file contains the ground truth data in NumPy format.
- `ground_truth.jpg` and `ground_truth_subplot.jpg`: These are visual representations of the ground truth data.
- `sgpradflux10long_area_mean.c2.20090506_1200UTC.nc`: This file contains specific ground truth data.

## Output Plots

The `output_plots` directory contains various plots generated from the model output:

- `base_model_pred.jpg`: This image shows the base model predictions.
- `base_model_pred.npy`: This file contains the base model predictions in NumPy format.
- `GT_and_model.jpg`: This image shows a comparison between the ground truth and the model predictions.

## WRF-Data-netCDF4

The `WRF-Data-netCDF4` directory contains output files from the Weather Research and Forecasting (WRF) model. Each file represents the model output for a specific time, as indicated by the timestamp in the file name.
