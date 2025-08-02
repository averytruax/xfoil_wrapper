import numpy as np
from pydantic import BaseModel

"""Script containing the geometric information about the airfoils and the optimization parameters"""
class RunAirfoil(BaseModel):

    tag: str = 'base'
    cst_coefficients: dict = None
    settings: dict = None
    optimization_parameters: dict = None

    @classmethod
    def reflex(cls):

        airfoil = cls()

        airfoil.tag = "reflex"

        airfoil.cst_coefficients = {
            'upper' : np.array([0.102220,0.15578,0.099851,0.069602,0.4,-0.15,1e-06,0.35]),
            'lower' : np.array([-0.22348,-0.28056,-0.11018,-0.13087,-0.28754,-0.25265,-0.14652,-0.35407]),
        }

        airfoil.settings = {
            'yte'       : 0.0,
            'type'      : 'round',
        }

        return airfoil