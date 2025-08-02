from pydantic import BaseModel
from typing import Optional

import numpy as np

class OperatingConditions(BaseModel):

    # TODO: expand this to be an array of operating conditions
    mach: Optional[float] = np.nan
    altitude: Optional[float] = np.nan