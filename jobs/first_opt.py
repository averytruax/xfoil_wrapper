from helpers.std_atm import Atmosphere
from wrapper.xfoil_wrapper import XfoilWrapper
from wrapper.data_classes import OperatingConditions
from geometry.geometric_functions import AirfoilFunctions
from geometry.runner_airfoil import RunAirfoil
import numpy as np
from pydantic import BaseModel


class OptimizationParms(BaseModel):
    max_cst_delta: float = 0.05
    max_tc_ratio: float = 0.12
    alpha: float = 3.5 # degrees

class _Settings(BaseModel):

    # Data Classes
    run_airfoil: RunAirfoil = RunAirfoil.reflex()
    optimization_parameters: OptimizationParms = OptimizationParms()
    operating_conditions: OperatingConditions = OperatingConditions()

class _Outputs(BaseModel):

    results: dict = {}

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

        run = XfoilWrapper(print_comms=True)
        airfoil = settings.run_airfoil

        # Write the airfoil CST to a dat file for XFOIL to read
        af_functions = AirfoilFunctions()
        af_functions.create_and_write_airfoil_file(airfoil)

        settings.operating_conditions.mach = 0.4
        settings.operating_conditions.altitude = 10

        atm: Atmosphere = Atmosphere.evaluate(settings.operating_conditions)

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

        

        run.test_this_thang(atm.reynolds_number, atm.mach)

