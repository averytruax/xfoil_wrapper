#Script containing the geometric information about the airfoils and the optimization parameters

airfoil_desc = {
    'cst_upper' : [0.102220,0.15578,0.099851,0.069602,0.4,-0.15,1e-06,0.35],
    'cst_lower' : [-0.22348,-0.28056,-0.11018,-0.13087,-0.28754,-0.25265,-0.14652,-0.35407],
    'yte'       : 0,
    'type'      : 'round'
}

optimization_parameters = {
    'thickness_chord_lim' : 0.12,
    'geometric_iteration_lim' : 15,
    'target_cl_max' : 1.2,
    'target_cd0_' : 0.02,
    'target_cm0' : 0.01 
}