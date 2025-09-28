import numpy as np
from pydantic import BaseModel
from typing import Optional

"""Script containing the geometric information about the airfoils and the optimization parameters"""
class Airfoil(BaseModel):

    tag: str = 'base'
    cst_coefficients: dict
    settings: dict
    # TODO: move this to its own class maybe?
    optimization_parameters: Optional[dict] = None

    @classmethod
    def reflex(cls):

        tag = "reflex"

        cst_coefficients = {
            'upper' : np.array([0.102220,0.15578,0.099851,0.069602,0.4,-0.15,1e-06,0.35]),
            'lower' : np.array([-0.22348,-0.28056,-0.11018,-0.13087,-0.28754,-0.25265,-0.14652,-0.35407]),
        }

        settings = {
            'yte'       : 0.0,
            'type'      : 'round',
        }

        return cls(tag=tag, cst_coefficients=cst_coefficients, settings=settings)