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


class OptimizationResults(BaseModel):
    pass