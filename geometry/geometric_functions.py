import numpy as np
from typing import Literal, Optional
from scipy.special import factorial
from pydantic import BaseModel
import os
from geometry.runner_airfoil import RunAirfoil
from helpers.paths import PATHS


class AirfoilFunctions(BaseModel):
    """
    Class containing the basic geometric functions used to construct the CST
    airfoils and interact with XFOIL

    Equations from:
    https://arc.aiaa.org/doi/10.2514/6.2007-62
    """

    # Define Attributes of the class -----------------------------------------------

    # round will almost always be used for subsonic / transonic flow
    airfoil_type: Literal['round', 'elliptic', 'biconvex', 'sears_haack',
            'low_drag', 'cone_wedge', 'rectangle_duct'] = 'round'

    # Inherant to an airfoil as described in Kulfan
    airfoil_type_coefficients: tuple[float, float] = {
        'round': (0.5, 1),
        'elliptic': (0.5, 0.5),
        'biconvex': (1, 1),
        'sears_haack': (0.75, 0.75),
        'low_drag': (0.75, 0.25),
        'cone_wedge': (1, 0.001),
        'rectangle_duct': (0.001, 0.001),
    }[airfoil_type]

    n1: float = airfoil_type_coefficients[0]
    n2: float = airfoil_type_coefficients[1]

    # Normally 0.0, except for very specific cases
    yte: float = 0.0

    # ------------------------------------------------------------------------------

    def create_and_write_airfoil_file(
        self,
        airfoil: RunAirfoil,
        file_name: Optional[str] = 'wrapper_airfoil.dat',
        ) -> None:


        # unpack
        upper_cst = airfoil.cst_coefficients["upper"]
        lower_cst = airfoil.cst_coefficients["lower"]
        yte = airfoil.settings['yte']
        af_type = airfoil.settings['type']

        # Create upper coords
        upper_coords = self.cst_xy(upper_cst,yte,af_type)
        lower_coords = self.cst_xy(lower_cst,yte,af_type)

        self.write_dat_file(upper_coords,lower_coords,file_name)

        return

    def cst_xy(
        self,
        cst: list,
        yte: float,
        airfoil_type: Literal['round', 'elliptic', 'biconvex', 'sears_haack',
            'low_drag', 'cone_wedge', 'rectangle_duct'] = 'round',
        num_points: int = 160
        ) -> np.array:
        """
        Converts CST coefficients to XY coordinates for an airfoil.

        Parameters:
            cst (np.array): CST coefficients for the upper or lower airfoil surface
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

    def write_dat_file(
        self,
        xy_upper: np.ndarray,
        xy_lower: np.ndarray,
        file_name: Optional[str] = 'wrapper_airfoil.dat',
        ) -> None:
        '''
        Inputs:
            filename    : The name of the .dat file to be output
            xy_upper    : The (x,y) numpy array for the upper surface
            xy_lower    : The (x,y) numpy array for the lower surface

        Outputs:
            None
        '''

        outputs_dir = PATHS.outputs()
        full_path = outputs_dir / file_name

        if os.path.exists(full_path):
            os.remove(full_path)
        upper_surface = xy_upper[::-1][0:-1]
        lower_surface = xy_lower[:]
        all_coords = np.concatenate((upper_surface, lower_surface))
        with open(full_path , 'w') as file:
            file.write(f'{full_path}\n')
            for i in range(len(all_coords)):
                file.write(f'\t{all_coords[i][0]:.5f} \t{all_coords[i][1]:.5f}\n')

    def dat_file_to_cst(
        self,
        dat_file: str,
        degree: int, # degree = number of coeffs
        ) -> np.ndarray:

        coords = np.loadtxt(dat_file,skiprows=[0])

        x , y = coords[:, 0] , coords[: , 1]

        n1 , n2 = self.n1, self.n2

        r = np.arange(degree)

        #Kulfan Equation 9
        K = factorial(degree-1)/(factorial(r) * factorial(degree-1-r))

        #Kulfan Equation 1 and 8 (phi matrix for Rsquared fit)
        phi = x*n1*(1-x)*n2*K*np.pow(x,r)*np.pow(1-x,degree-1-r)

        #CST Coefficients - Obtained from the QR factorization of phi.
        Q, R = np.linalg.qr(phi)

        rhs = y - x @ self.yte

        A = np.linalg.solve(R, Q.T @ rhs)

        return A


# Test functions

if __name__ == "__main__":

    dat_file = "../wrapper/wrapper_airfoil.dat"

    obj = AirfoilFunctions()

    obj.dat_file_to_cst(dat_file,6)