from helpers.std_atm import Atmosphere
from helpers.file_readers import FileReaders
from wrapper.xfoil_wrapper import XfoilOperator
from wrapper.data_classes import OperatingConditions, OptimizationResults
from geometry.geometric_functions import AirfoilFunctions
from geometry.airfoil import Airfoil
from copy import deepcopy
from wrapper.xfoil_wrapper import StandardOperations
from wrapper.plotter import OptimizationResultsPlotter
import numpy as np
from scipy.optimize import minimize
from pydantic import BaseModel


class OptimizationParms(BaseModel):
    max_cst_delta: float = 0.05
    max_tc_ratio: float = 0.12

class _Settings(BaseModel):

    # Data Classes
    run_airfoil: Airfoil = Airfoil.reflex()
    optimization_parameters: OptimizationParms = OptimizationParms()

    # Operating Conditions for the optimization
    mach: float = 0.3
    altitude: float = 10 # altitude in km
    alpha: float = 1.5 # degrees


class _Outputs(OptimizationResults):
    pass

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

        self.get_LD()
        self.plot_results()


    def get_LD(self) -> float:

        settings = self.settings
        outputs = self.outputs

        # Initialize the run process and its dependencies
        run = StandardOperations(print_comms=True, display_graphics=True)
        run.start_xfoil()
        # TODO: have this be done in one function call and move inside the objective function for the optimization.
        run.operating_conditions.mach = settings.mach
        run.operating_conditions.altitude = settings.altitude
        run.operating_conditions.alpha = settings.alpha
        atm: Atmosphere = Atmosphere.evaluate(run.operating_conditions)
        run.operating_conditions.reynolds_number = atm.reynolds_number

        airfoil = settings.run_airfoil
        initial_airfoil = deepcopy(airfoil)

        # Write the airfoil CST to a dat file for XFOIL to read
        af_functions = AirfoilFunctions()

        # Set up the constraints for the optimization
        max_delta = settings.optimization_parameters.max_cst_delta
        # NOTE: Assumption is made that all CST coefficients have same sign as their surface (e.g. upper = +ve)
        cst_top_surface_upper_lim = (
            airfoil.cst_coefficients['upper'] + max_delta
        )
        # Limit CST coefficients to have a lower bound of 0.0
        cst_top_surface_lower_lim = (
            airfoil.cst_coefficients['upper'] - max_delta
        )
        cst_bot_surface_upper_lim = (
            airfoil.cst_coefficients['lower'] + max_delta
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

        # Store the parameters used for this optimization
        outputs.parameters = {
            'airfoil': initial_airfoil,


        }

        def objective(params):
            # Unpack
            upper_coeffs = params[:n_upper]
            lower_coeffs = params[n_upper:]

            # Keep track of the coefficients
            outputs.residuals_list.append(tuple(upper_coeffs) + tuple(lower_coeffs))

            # Set these back into your airfoil object
            airfoil.cst_coefficients['upper'] = upper_coeffs
            airfoil.cst_coefficients['lower'] = lower_coeffs

            # Write the new airfoil file
            af_functions.create_and_write_airfoil_file(airfoil)

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
            options={
                'disp': True,
                'iprint': 2,
                'maxiter': 50,
                'eps': settings.optimization_parameters.max_cst_delta * 0.75
            }  # adjust maxiter if needed
        )

        # Unpack
        upper_coeffs = res.x[:n_upper]
        lower_coeffs = res.x[n_upper:]

        # Keep track of the coefficients
        outputs.residuals_list.append(tuple(upper_coeffs) + tuple(lower_coeffs))

        # Set these back into your airfoil object
        airfoil.cst_coefficients['upper'] = upper_coeffs
        airfoil.cst_coefficients['lower'] = lower_coeffs

        print("Optimal coefficients (upper):", res.x[:n_upper])
        print("Optimal coefficients (lower):", res.x[n_upper:])
        print("Max L/D:", -res.fun)


    def plot_results(self):

        plotter = OptimizationResultsPlotter(results=self.outputs)

        fig = plotter.plot_results()

        fig.show()





