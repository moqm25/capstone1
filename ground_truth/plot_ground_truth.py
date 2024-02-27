import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import os

def get_GT():
    GTDIR = '/home/capstonei/CS492_Tasks/ground_truth/'
    os.chdir(GTDIR)
    if 'ground_truth_data.npy' in os.listdir(GTDIR):
        data = np.load('ground_truth_data.npy', allow_pickle=True).item()
        return data['obs_swdtot'], data['obs_swddir'], data['obs_swddif'], data['obs_swddni'], data['obs_time']
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
    return data['obs_swdtot'], data['obs_swddir'], data['obs_swddif'], data['obs_swddni'], data['obs_time']

def show_GT(name, obs_swdtot, obs_swddir, obs_swddif, obs_swddni, obs_time):
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

if __name__ == '__main__':
    obs_swdtot, obs_swddir, obs_swddif, obs_swddni, obs_time = get_GT()
    show_GT('ground_truth', obs_swdtot, obs_swddir, obs_swddif, obs_swddni, obs_time)
