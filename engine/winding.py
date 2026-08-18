"""Winding design calculations (Module 7)"""
import math
from engine.constants import CONDUCTOR

def _r(val, decimals=2):
    """Safely round values or return '—' for missing/invalid input."""
    if val == "—" or val is None: return "—"
    try: return round(float(val), decimals)
    except: return "—"

def calculate_winding(I1, I2, N1, N2, A1_mm2, A2_mm2, material_hv='Cu', material_lv='Cu', frequency=50.0, core_diameter_mm=None, S_kVA=None):
    """
    Calculate winding design parameters.
    """
    try:
        I1 = float(I1) if I1 != "—" and I1 is not None else 0
        I2 = float(I2) if I2 != "—" and I2 is not None else 0
        N1 = float(N1) if N1 != "—" and N1 is not None else 0
        N2 = float(N2) if N2 != "—" and N2 is not None else 0
        A1_mm2 = float(A1_mm2) if A1_mm2 != "—" and A1_mm2 is not None else 0
        A2_mm2 = float(A2_mm2) if A2_mm2 != "—" and A2_mm2 is not None else 0
    except (TypeError, ValueError):
        return {}

    if S_kVA is not None and (core_diameter_mm is None or core_diameter_mm == "—" or core_diameter_mm == 0):
        try:
            s_val = float(S_kVA)
            s_k = s_val / 1000.0 if s_val >= 1000.0 else s_val
            core_diameter_mm = 50.0 * (s_k ** 0.25)
        except:
            core_diameter_mm = 120.0
    elif core_diameter_mm is None or core_diameter_mm == "—":
        core_diameter_mm = 120.0
    else:
        core_diameter_mm = float(core_diameter_mm)

    # 1. Conductor diameter (for round wire equivalent)
    d_conductor_hv_mm = math.sqrt(4.0 * A1_mm2 / math.pi) if A1_mm2 > 0 else 0
    d_conductor_lv_mm = math.sqrt(4.0 * A2_mm2 / math.pi) if A2_mm2 > 0 else 0

    # 2. Parallel conductors (practical flat/foil strip limit ~12-16 mm²)
    n_parallel_hv = max(1, math.ceil(A1_mm2 / 12.0)) if A1_mm2 > 12.0 else 1
    n_parallel_lv = max(1, math.ceil(A2_mm2 / 12.0)) if A2_mm2 > 12.0 else 1

    # 3. Mean Length of Turn (MLT)
    MLT_hv_mm = math.pi * (core_diameter_mm + 60.0)
    MLT_lv_mm = math.pi * (core_diameter_mm + 25.0)

    # 4. Total conductor length (m)
    L_hv = (N1 * MLT_hv_mm) / 1000.0
    L_lv = (N2 * MLT_lv_mm) / 1000.0

    # 5. Resistivity and Temperature Coefficient
    mat_hv = CONDUCTOR.get(material_hv, CONDUCTOR.get('Cu', {}))
    mat_lv = CONDUCTOR.get(material_lv, CONDUCTOR.get('Cu', {}))

    rho_20_hv = mat_hv.get("resistivity_20", 1.724e-8)
    rho_20_lv = mat_lv.get("resistivity_20", 1.724e-8)
    alpha_hv = mat_hv.get("temp_coeff", 0.00393)
    alpha_lv = mat_lv.get("temp_coeff", 0.00393)
    density_hv = mat_hv.get("density", 8900)
    density_lv = mat_lv.get("density", 8900)

    # Resistance at 20°C
    R_20_hv = (rho_20_hv * L_hv) / (A1_mm2 * 1e-6) if A1_mm2 > 0 else 0
    R_20_lv = (rho_20_lv * L_lv) / (A2_mm2 * 1e-6) if A2_mm2 > 0 else 0

    # Resistance at 75°C (IEC 60076 standard reference temperature)
    R_75_hv = R_20_hv * (1.0 + alpha_hv * 55.0)
    R_75_lv = R_20_lv * (1.0 + alpha_lv * 55.0)

    # 7. Copper / Conductor losses at 75°C
    P_cu_hv_W = (I1 ** 2) * R_75_hv
    P_cu_lv_W = (I2 ** 2) * R_75_lv
    P_cu_total_W = P_cu_hv_W + P_cu_lv_W

    # 8. Physical conductor weight (kg)
    weight_hv_kg = L_hv * (A1_mm2 * 1e-6) * density_hv
    weight_lv_kg = L_lv * (A2_mm2 * 1e-6) * density_lv

    return {
        "d_conductor_hv_mm": _r(d_conductor_hv_mm),
        "d_conductor_lv_mm": _r(d_conductor_lv_mm),
        "n_parallel_hv": n_parallel_hv,
        "n_parallel_lv": n_parallel_lv,
        "MLT_hv_mm": _r(MLT_hv_mm),
        "MLT_lv_mm": _r(MLT_lv_mm),
        "R_hv_75": _r(R_75_hv, 4),
        "R_lv_75": _r(R_75_lv, 4),
        "P_cu_hv_W": _r(P_cu_hv_W),
        "P_cu_lv_W": _r(P_cu_lv_W),
        "P_cu_total_W": _r(P_cu_total_W),
        "weight_hv_kg": _r(weight_hv_kg),
        "weight_lv_kg": _r(weight_lv_kg),
        "total_conductor_length_hv_m": _r(L_hv),
        "total_conductor_length_lv_m": _r(L_lv)
    }
