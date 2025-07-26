# Import Scripts to be used
from std_atm import std_atm
from geometry.geometric_functions import AirfoilFunctions
from wrapper.runner_airfoil import airfoil_desc , optimization_parameters
from xfoil_wrapper import XfoilWrapper
import matplotlib.pyplot as plt
from math import sqrt



# #Name of the file for the final drag polar to be output to
# datafile = 'wrapper_data.txt'

#Options for the wrapper =========================================
M = 0.2   #Mach number for the analysis (Keep below M = 0.7)
altitude = 30000  #Altitude for the analysis (specify units as third argument

#=================================================================

if __name__ == "__main__":

    # Have this file be the one that is run, but have it reference files
    # that are in a job_configuration directory

    # Create the airfoil and export it as a dat file
    upper_coords = gf.cst_xy(airfoil_desc['cst_upper'],
                             airfoil_desc['yte'],
                             airfoil_desc['type'],
                             num_points=50)
    lower_coords = gf.cst_xy(airfoil_desc['cst_lower'],
                             airfoil_desc['yte'],
                             airfoil_desc['type'],
                             num_points=50)

    gf.write_dat_file('wrapper_airfoil.dat',upper_coords,lower_coords)

    atm_data = std_atm(altitude,'ft')
    a = sqrt(1.4 * 287 * atm_data['Temperature'])
    Re = (atm_data['Density'] * M * a) / atm_data['Viscosity'] # 1/m
    print(M*a)
    print(atm_data['Density'])
    print(atm_data['Temperature'])
    print(atm_data['Viscosity'])
    print(Re)

    run = XfoilWrapper()

    # run.test_this_thang(Re,M)

    polar = run.get_airfoil_polar_data(Re,M)

    # fig = plt.figure(figsize=(8,5))
    # ax = plt.axes()
    # ax.set_xlabel('Cd')
    # ax.set_ylabel('Cl')
    # ax.set_xlim((min(polar['cd'][:])-0.1*min(polar['cd'][:]),max(polar['cd'][:])+0.1*max(polar['cd'][:])))
    # ax.set_ylim((min(polar['cl'][:])-0.1*min(polar['cl'][:]),max(polar['cl'][:])+0.1*max(polar['cl'][:])))
    # plt.plot(polar['cd'],polar['cl'])
    # plt.savefig('Drag_Polar.png')

    # fig = plt.figure(figsize=(8,5))
    # ax = plt.axes()
    # ax.set_xlabel('alpha')
    # ax.set_ylabel('Cl')
    # ax.set_ylim((min(polar['cl'][:])-0.1*min(polar['cl'][:]),max(polar['cl'][:])+0.1*max(polar['cl'][:])))
    # ax.set_xlim((min(polar['alpha'][:])-0.1*min(polar['alpha'][:]),max(polar['alpha'][:])+0.1*max(polar['alpha'][:])))
    # plt.plot(polar['alpha'],polar['cl'])
    # plt.savefig('Lift_Curve.png')

    # fig = plt.figure(figsize=(8,5))
    # ax = plt.axes()
    # ax.set_xlabel('alpha')
    # ax.set_ylabel('cd')
    # ax.set_ylim((min(polar['cd'][:])-0.1*min(polar['cd'][:]),max(polar['cd'][:])+0.1*max(polar['cd'][:])))
    # ax.set_xlim((min(polar['alpha'][:])-0.1*min(polar['alpha'][:]),max(polar['alpha'][:])+0.1*max(polar['alpha'][:])))
    # plt.plot(polar['alpha'],polar['cd'])
    # plt.savefig('Drag_Bucket.png')