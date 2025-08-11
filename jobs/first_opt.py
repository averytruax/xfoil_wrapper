from helpers.std_atm import Atmosphere
from helpers.file_readers import FileReaders
from wrapper.xfoil_wrapper import XfoilOperator
from wrapper.data_classes import OperatingConditions, OptimizationResults
from geometry.geometric_functions import AirfoilFunctions
from geometry.runner_airfoil import RunAirfoil
from wrapper.xfoil_wrapper import StandardOperations
import numpy as np
from scipy.optimize import minimize
from pydantic import BaseModel


class OptimizationParms(BaseModel):
    max_cst_delta: float = 0.05
    max_tc_ratio: float = 0.12

class _Settings(BaseModel):

    # Data Classes
    run_airfoil: RunAirfoil = RunAirfoil.reflex()
    optimization_parameters: OptimizationParms = OptimizationParms()

    # Operating Conditions for the optimization
    mach: float = 0.4
    altitude: float = 10 # altitude in km
    alpha: float = 3.5 # degrees


class _Outputs(BaseModel):

    results: OptimizationResults = OptimizationResults()

class OptimizeLD:

    def __init__(self):
        self.settings = _Settings()
        self.outputs = _Outputs()
        return

    def run_process(self):
        """
        This method is responsible for actually running the optimization and storing the results
        """
        settings = self.settings
        outputs = self.outputs


    def get_LD(self) -> float:

        settings = self.settings

        run = StandardOperations(print_comms=True)
        # TODO: have this be done in one function call and move inside the objective function for the optimization.
        run.operating_conditions.mach = settings.mach
        run.operating_conditions.altitude = settings.altitude
        run.operating_conditions.alpha = settings.alpha
        atm: Atmosphere = Atmosphere.evaluate(run.operating_conditions)
        run.operating_conditions.reynolds_number = atm.reynolds_number

        airfoil = settings.run_airfoil

        # Write the airfoil CST to a dat file for XFOIL to read
        af_functions = AirfoilFunctions()
        af_functions.create_and_write_airfoil_file(airfoil)


        # Set up the constraints for the optimization
        max_delta = settings.optimization_parameters.max_cst_delta
        # NOTE: Assumption is made that all CST coefficients have same sign as their surface (e.g. upper = +ve)
        cst_top_surface_upper_lim = (
            airfoil.cst_coefficients['upper'] + max_delta
        )
        # Limit CST coefficients to have a lower bound of 0.0
        cst_top_surface_lower_lim = (
            np.clip(airfoil.cst_coefficients['upper'] - max_delta, 0.0, None)
        )
        # Limit CST coefficients to have a upper bound of 0.0
        cst_bot_surface_upper_lim = (
            np.clip(airfoil.cst_coefficients['lower'] + max_delta, None, 0.0)
        )
        cst_bot_surface_lower_lim = (
            airfoil.cst_coefficients['lower'] - max_delta
        )

        # Flatten all bounds together for SLSQP
        bounds = list(zip(
            np.concatenate([cst_top_surface_lower_lim, cst_bot_surface_lower_lim]),
            np.concatenate([cst_top_surface_upper_lim, cst_bot_surface_upper_lim])
        ))

        # Initial guess = current airfoil coefficients
        x0 = np.concatenate([
            airfoil.cst_coefficients['upper'],
            airfoil.cst_coefficients['lower']
        ])

        # Number of upper surface coefficients
        n_upper = len(airfoil.cst_coefficients['upper'])

        def objective(params):
            # Unpack
            upper_coeffs = params[:n_upper]
            lower_coeffs = params[n_upper:]

            # Set these back into your airfoil object
            airfoil.cst_coefficients['upper'] = upper_coeffs
            airfoil.cst_coefficients['lower'] = lower_coeffs

            # Run aerodynamic solver
            run.setup_run_state()
            run.get_LD()

            # Read results
            df = FileReaders().read_aero_file()
            CL = df['CL'].iloc[0]
            CD = df['CD'].iloc[0]
            LD = CL / CD

            # We want to maximize LD, so minimize -LD
            return -LD

        # Run optimizer
        res = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            options={'disp': True, 'maxiter': 50}  # adjust maxiter if needed
        )

        print("Optimal coefficients (upper):", res.x[:n_upper])
        print("Optimal coefficients (lower):", res.x[n_upper:])
        print("Max L/D:", -res.fun)





