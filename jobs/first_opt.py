from helpers.std_atm import std_atm
from wrapper.xfoil_wrapper import XfoilWrapper
from geometry.geometric_functions import AirfoilFunctions
from geometry.runner_airfoil import RunAirfoil
import numpy as np
from pydantic import BaseModel


class OptimizationParms(BaseModel):
    max_cst_delta: float = 0.05
    max_tc_ratio: float = 0.12

class _Settings(BaseModel):

    run_airfoil: RunAirfoil = RunAirfoil.test_airfoil()
    optimization_parameters: OptimizationParms = OptimizationParms()

class _Outputs(BaseModel):

    results: dict = {}


class OptimizeLD:

    def __init__(self):
        self.settings = _Settings()
        self.outputs = _Outputs()
        return

    def run(self):


