import numpy as np
from typing import Literal

# TODO: convert this to a class

def std_atm(
    altitude: float,
    units: Literal["m","km","ft"] = "km",
    print_output: bool = False
    ) -> dict:
    """
    Standard Atmosphere Calculator

    Inputs:
        altitude: Altitude in km or in desired units: {m, km, ft}
        units: Unit of input altitude ('m', 'km', 'ft')
        print_output: Boolean flag to print results

    Outputs:
        atm_data: Tuple containing (P_inf, T_inf, rho_inf, mu_inf)
    """
    unit_conversion = {'m': 1/1000, 'ft': 0.0003048, 'km': 1}[units]

    altitude *= unit_conversion

    r_0 = 6.3781e6  # m
    g_0 = 9.806  # m/s^2
    MW_0 = 28.9644  # kg/kmol
    R_unv = 8314  # J/kmol K
    Beta = 1.458e-6  # kg/smK^1/2
    Suth = 110.4  # K

    if altitude <= 86:
        h = (r_0 * altitude * 1000) / (r_0 + altitude * 1000) / 1000

        h_i = np.array([0, 11, 20, 32, 47, 51, 71, 84.857])
        L_h = np.array([-6.5, 0, 1, 2.8, 0, -2.8, -2])
        T_m = np.array([288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65])
        P_i = np.array([101325, 22631.95, 5474.79, 868.01, 110.9, 66.94, 3.956])

        index = np.searchsorted(h_i, h, side='right') - 1

        h_i_use, L_h_use, T_m_use, P_use = h_i[index], L_h[index], T_m[index], P_i[index]

        if L_h_use == 0:
            P_inf = P_use * np.exp((-g_0 * MW_0 * (altitude - h_i_use)) / (R_unv / 1000 * T_m_use))
        else:
            exponent = (g_0 * MW_0) / (R_unv / 1000 * L_h_use)
            base = (T_m_use) / (T_m_use + L_h_use * (altitude - h_i_use))
            P_inf = P_use * (base ** exponent)

        T_inf = T_m_use + L_h_use * (altitude - h_i_use)
        rho_inf = (P_inf * MW_0) / (R_unv * T_inf)
    else:
        h_i_use, L_h_use, T_m_use, P_use = 71, -2, 214.65, 3.956
        exponent = (g_0 * MW_0) / (R_unv / 1000 * L_h_use)
        base = (T_m_use) / (T_m_use + L_h_use * (altitude - h_i_use))
        P_top = P_use * (base ** exponent)
        T_top = T_m_use + L_h_use * (altitude - h_i_use)
        rho_top = (P_top * MW_0) / (R_unv * T_top)

        z = altitude
        z_i = np.array([86, 100, 110, 120, 150])
        L_h = np.array([1.6481, 5, 10, 20])
        T_m = np.array([186.945, 210.65, 260.65, 360.65])
        MW = np.array([28.9644, 28.88, 28.56, 28.08])
        P_i = np.array([0.34313, 0.030075, 0.0073544, 0.0025217])
        b = 3.31e-7  # m^-1

        index = np.searchsorted(z_i, z, side='right') - 1
        z_i_use, L_h_use, T_m_use, MW_use, P_use = z_i[index], L_h[index], T_m[index], MW[index], P_i[index]

        exponent = -( (g_0 / (R_unv / MW_use * L_h_use)) * (1 + b * (T_m_use / L_h_use - z_i_use)))
        third_term = np.exp((g_0 * b) / ((R_unv / MW_use) * L_h_use) * (z - z_i_use))
        T_inf = T_m_use + L_h_use * (z - z_i_use)
        P_inf = P_use * ((T_inf / T_m_use) ** exponent) * third_term

        exponent = -( (g_0 / (R_unv / MW_use * L_h_use)) *
                     ((R_unv / MW_use) * L_h_use / g_0 + 1 + b * (T_m_use / L_h_use - z_i_use)))
        third_term = np.exp((g_0 * b) / ((R_unv / MW_use) * L_h_use) * (z - z_i_use))
        rho_inf = rho_top * ((T_inf / T_m_use) ** exponent) * third_term

    mu_inf = (Beta * T_inf ** 1.5) / (Suth + T_inf)

    if print_output:
        print("Freesream Conditions:")
        print(f'\tPressure:     {P_inf:.6f} Pa')
        print(f'\tTemperature:  {T_inf:.6f} K')
        print(f'\tDensity:      {rho_inf:.6f} kg/m^3')
        print(f'\tViscosity:    {mu_inf:.6f} Ns/m^2')

    return {'Pressure' : P_inf , 'Temperature' : T_inf , 'Density' : rho_inf , 'Viscosity' : mu_inf}


if __name__ == "__main__":
    alt = 10
    units = 'km'
    std_atm(altitude=alt, units=units, print_output=True)