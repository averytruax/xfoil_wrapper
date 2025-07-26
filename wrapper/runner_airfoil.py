import numpy as np
from pydantic import BaseModel

"""Script containing the geometric information about the airfoils and the optimization parameters"""
class RunnerAirfoil(BaseModel):
    def __init__(self):

        self.tag: str
        self.airfoil_cst_coefficients: dict = None
        self.settings: dict = None
        self.optimization_parameters: dict = None

        return


    @classmethod
    def test_airfoil(cls):

        airfoil = cls()

        airfoil.settings = "test_airfoil"

        airfoil.airfoil_cst_coefficients = {
            'cst_upper' : np.array([0.102220,0.15578,0.099851,0.069602,0.4,-0.15,1e-06,0.35]),
            'cst_lower' : np.array([-0.22348,-0.28056,-0.11018,-0.13087,-0.28754,-0.25265,-0.14652,-0.35407]),
        }

        airfoil.airfoil_settings = {
            'yte'       : 0.0,
            'type'      : 'round',
        }

        # TODO: move these somewhere else in the repo
        optimization_parameters = {
            'thickness_chord_lim' : 0.12,
            'geometric_iteration_lim' : 15.0,
            'target_cl_max' : 1.2,
            'target_cd0_' : 0.02,
            'target_cm0' : 0.01,
        }

        return airfoil