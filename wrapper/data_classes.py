from pydantic import BaseModel
from typing import Optional
import numpy as np

class OperatingConditions(BaseModel):

    # TODO: expand this to be an array of operating conditions
    mach: Optional[float] = np.nan
    altitude: Optional[float] = np.nan
    alpha: Optional[float] = np.nan  # Angle of attack in degrees
    reynolds_number: Optional[float] = np.nan  # Reynolds number
    viscosity: Optional[float] = np.nan  # Viscosity of the fluid
    density: Optional[float] = np.nan  # Density of the fluid


class OptimizationResults(BaseModel, arbitrary_types_allowed=True):
    """
    Class to hold the results of any optimization process
    Fields may vary depending on what is being optimized
    """

    parameters: dict = {} # Dictionary to hold the parameters used in the optimization
    residuals_list: list = [] # List of residuals from the optimization
    airfoils_list: list = [] # List of airfoil shapes at each iteration
