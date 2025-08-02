# Import Scripts to be used
from helpers.std_atm import std_atm
from wrapper.xfoil_wrapper import XfoilWrapper
from geometry.geometric_functions import AirfoilFunctions
from geometry.runner_airfoil import RunAirfoil
from math import sqrt


"""

TODO:
-Need to figure out how to make a pyproject.toml file to treat the directories as packages
-Need to figure out how final files will be structured


"""



# #Name of the file for the final drag polar to be output to
# datafile = 'wrapper_data.txt'

#Options for the wrapper =========================================
M = 0.2   #Mach number for the analysis (Keep below M = 0.7)
altitude = 30000  #Altitude for the analysis (specify units as third argument

#=================================================================

if __name__ == "__main__":

    # TODO: Have this file be the one that is run, but have it reference files
    # that are in a job_configuration directory

    from geometry.geometric_functions import AirfoilFunctions

    obj = AirfoilFunctions()

    airfoil = RunAirfoil.test_airfoil()


    obj.create_and_write_airfoil_file(airfoil)



    atm_data = std_atm(altitude,'ft')
    a = sqrt(1.4 * 287 * atm_data['Temperature'])
    Re = (atm_data['Density'] * M * a) / atm_data['Viscosity'] # 1/m

    run = XfoilWrapper(print_comms=True)

    run.test_this_thang(Re,M)

    # polar = run.get_airfoil_polar_data(Re,M)

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