from typing import Literal
import numpy as np
from scipy.special import factorial
import os

def cst_xy(
        cst: list, 
        yte: float, 
        airfoil_type: Literal['round', 'elliptic', 'biconvex', 'sears_haack', 'low_drag',
                 'cone_wedge', 'rectangle_duct'] = 'round', 
        num_points: int = 200) -> np.array:
    """
    Converts CST coefficients to XY coordinates for an airfoil.
    
    Parameters:
        cst (array-like): CST coefficients for the airfoil surface (upper or lower)
        yte (float): Trailing edge offset in the z/c direction
        airfoil_type (str): Airfoil shape type, must be one of:
            'round', 'elliptic', 'biconvex', 'sears_haack', 'low_drag',
            'cone_wedge', 'rectangle_duct'
    
    Returns:
        xy_array (numpy.ndarray): Array containing x and y coordinates for the airfoil surface
    """
    cst = np.asarray(cst).flatten()
    
    n_dict: dict = {
        'round': (0.5, 1),
        'elliptic': (0.5, 0.5),
        'biconvex': (1, 1),
        'sears_haack': (0.75, 0.75),
        'low_drag': (0.75, 0.25),
        'cone_wedge': (1, 0.001),
        'rectangle_duct': (0.001, 0.001),
    }[airfoil_type]

    n1, n2 = n_dict


    
    # Define the order of polynomial based on number of CST coefficients
    n = len(cst)
    r = np.arange(1, n + 1)

    # Generate x values evenly spaced between 0 and 2*pi
    psi = np.linspace(-np.pi , 0 , num_points)
    psi = (np.cos(psi)+1)/2    
    
    # Define the binomial coefficient
    K = factorial(n - 1) / (factorial(r - 1) * factorial(n - r))
    
    # Define the Shape function
    S = np.sum(cst * K * np.power(psi[:, None], r - 1) * np.power(1 - psi[:, None], n - r), axis=1)
    
    # Define Expression for shape of the airfoil
    y = psi**n1 * (1 - psi)**n2 * S + (psi * yte)
    x = psi
    
    return np.column_stack((x, y))

def write_dat_file(filename, xy_upper , xy_lower):
    '''
    Inputs: 
        filename    : The name of the .dat file to be output
        xy_upper    : The (x,y) numpy array for the upper surface
        xy_lower    : The (x,y) numpy array for the lower surface

    Outputs:
        None
    '''

    if os.path.exists(filename):
        os.remove(filename)
    upper_surface = xy_upper[::-1][0:-1]
    lower_surface = xy_lower[:]
    all_coords = np.concatenate((upper_surface, lower_surface))
    with open(filename , 'w') as file:
        file.write(f'{filename}\n')
        for i in range(len(all_coords)):
            file.write(f'\t{all_coords[i][0]:.5f} \t{all_coords[i][1]:.5f}\n')


