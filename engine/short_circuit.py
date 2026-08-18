"""Short-circuit dynamics and withstand calculations (Module 6)"""
import math
from engine.constants import ASYMMETRY_FACTORS

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

def calculate_short_circuit(I1, I2, uk, Rk, Xk, Zk=None, V1=None, V2=None, phase=3, N1=None, N2=None, core_diameter_mm=None):
    """
    Calculates short-circuit current, peak forces, and thermal withstand.
    """
    try:
        I1 = float(I1) if I1 != "—" and I1 is not None else 0
        I2 = float(I2) if I2 != "—" and I2 is not None else 0
        uk = float(uk) if uk != "—" and uk is not None else 0
        Rk = float(Rk) if Rk != "—" and Rk is not None else 0
        Xk = float(Xk) if Xk != "—" and Xk is not None else 0
    except (TypeError, ValueError):
        return {}

    if uk <= 0 or I1 <= 0:
        return {
            "Isc_A": "—", "Isc2_A": "—", "Ipeak_A": "—", "Ipeak2_A": "—",
            "xr_ratio": "—", "K_asymmetry": "—", "F_axial_N": "—",
            "F_radial_N": "—", "Ith_A": "—", "withstand_seconds": 2
        }

    # Symmetrical short circuit current (A)
    Isc = (I1 * 100.0) / uk
    Isc2 = (I2 * 100.0) / uk if I2 > 0 else (Isc * float(V1 or 1) / float(V2 or 1))

    # X/R ratio
    if Rk > 0:
        xr_ratio = Xk / Rk
    else:
        xr_ratio = 15.0

    # Asymmetry factor K interpolation from IEC 60076-5
    K = 1.0 + math.exp(-math.pi / xr_ratio) if xr_ratio > 0 else 1.0
    for xr_val, k_val in ASYMMETRY_FACTORS:
        if xr_ratio <= xr_val:
            K = k_val
            break

    # Asymmetrical peak short circuit current (A)
    Ipeak = Isc * math.sqrt(2.0) * K
    Ipeak2 = Isc2 * math.sqrt(2.0) * K

    # Thermal equivalent short circuit current (2 seconds)
    Ith = Isc * math.sqrt(1.0 + 0.1 * (xr_ratio ** 2)) if xr_ratio < 10 else Isc * 1.5

    # 1. Mechanical forces (IEC 60076-5)
    cd_m = (float(core_diameter_mm) / 1000.0) if core_diameter_mm and core_diameter_mm != "—" else 0.20
    D_mean = cd_m * 1.5
    h_winding = max(0.1, cd_m * 2.7)
    mu0 = 4.0 * math.pi * 1e-7

    F_axial = (mu0 * (Ipeak ** 2) * math.pi * D_mean) / (2.0 * h_winding) if h_winding > 0 else 0
    F_radial = (mu0 * (Ipeak ** 2) * h_winding) / (2.0 * math.pi * D_mean) if D_mean > 0 else 0

    # 2. Conductor Tensile Stress (N/mm²)
    # Typical dynamic hoop stress on outer winding
    sigma_radial = (F_radial / (2.0 * math.pi * 100.0)) if F_radial > 0 else 18.5

    # 3. 3-Second Thermal Withstand Temperature (°C)
    # theta_end = 75 + (J_sc / 106)^2 * 3 for Copper (IEC 60076-5 limit < 250°C)
    J_sc = (Isc / 1.5) if Isc > 0 else 50.0 # short-circuit current density
    theta_3s = min(240.0, 75.0 + ((J_sc / 106.0) ** 2) * 3.0)

    return {
        "Isc_A": _r(Isc, 1),
        "Isc2_A": _r(Isc2, 1),
        "Isc_lv_A": _r(Isc2, 1),
        "Ipeak_A": _r(Ipeak, 1),
        "Ipeak2_A": _r(Ipeak2, 1),
        "Ipeak_lv_A": _r(Ipeak2, 1),
        "xr_ratio": _r(xr_ratio, 2),
        "K_asymmetry": _r(K, 3),
        "asymmetry_factor_k": _r(K, 3),
        "F_axial_N": _r(F_axial, 1),
        "F_radial_N": _r(F_radial, 1),
        "sigma_radial_N_mm2": _r(sigma_radial, 1),
        "theta_3s_C": _r(theta_3s, 1),
        "Ith_A": _r(Ith, 1),
        "withstand_seconds": 2
    }
