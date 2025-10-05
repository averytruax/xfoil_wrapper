import numpy as np
from pydantic import BaseModel, model_validator
from typing import Optional, Literal

"""Script containing the geometric information about the airfoils and the optimization parameters"""

# Inherant to an airfoil as described in Kulfan
# These coefficients describe the curvature of the leaading edge
AIRFOIL_TYPE_COEFFICIENTS: tuple[float, float] = {
        'round': (0.5, 1),
        'elliptic': (0.5, 0.5),
        'biconvex': (1, 1),
        'sears_haack': (0.75, 0.75),
        'low_drag': (0.75, 0.25),
        'cone_wedge': (1, 0.001),
        'rectangle_duct': (0.001, 0.001),
    }

class Airfoil(BaseModel, arbitrary_types_allowed=True):
    """ This class defines an airfoil according to the CST method presented in kulfan et al."""

    tag: str = 'base'
    cst_coefficients: dict[Literal['upper','lower'], np.ndarray]

    # round will almost always be used for subsonic / transonic flow
    airfoil_type: Literal['round', 'elliptic', 'biconvex', 'sears_haack',
            'low_drag', 'cone_wedge', 'rectangle_duct']


    # These will be created from the airfoil type
    n1: float
    n2: float

    # Normally 0.0, except for very specific cases
    yte: float = 0.0

    # TODO: move this to its own class maybe?
    optimization_parameters: Optional[dict] = None

    @model_validator(mode='after')
    def check_coefficients(cls, values):
        coeffs = values.cst_coefficients
        len_upper = len(coeffs.get('upper', []))
        len_lower = len(coeffs.get('lower', []))
        if len_upper != len_lower:
            raise ValueError(
                f"Upper and lower CST coefficient lists must be the same length. Got {len_upper} and {len_lower}."
            )
        elif len_upper == len_lower == 0:
            raise ValueError("CST coefficient lists cannot be empty.")
        return values

    # ========================= DEFINE AIRFOILS HERE ===============================

    @classmethod
    def reflex(cls):

        tag = "reflex"

        airfoil_type = 'round'

        n1 = AIRFOIL_TYPE_COEFFICIENTS[airfoil_type][0]
        n2 = AIRFOIL_TYPE_COEFFICIENTS[airfoil_type][1]

        cst_coefficients = {
            'upper' : np.array([0.102220,0.15578,0.099851,0.069602,0.4,-0.15,1e-06,0.35]),
            'lower' : np.array([-0.22348,-0.28056,-0.11018,-0.13087,-0.28754,-0.25265,-0.14652,-0.35407]),
        }

        return cls(
            tag=tag,
            cst_coefficients=cst_coefficients,
            airfoil_type= airfoil_type,
            n1=n1,
            n2=n2,
            )