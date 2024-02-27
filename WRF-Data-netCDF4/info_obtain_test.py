import netCDF4

def display_variables(nc_file):
    nc = netCDF4.Dataset(nc_file)
    print("Variables in the .nc file:")
    for var in nc.variables:
        print(var)

# Example usage:
display_variables("/home/capstonei/CS492_Tasks/WRF-Data-netCDF4/wrfout_d01_2009-05-06_00:00:00")
