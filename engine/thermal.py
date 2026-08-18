"""Thermal and cooling analysis (Module 8)"""
import math
from engine.constants import OIL_PROPERTIES, COOLING_METHODS, THERMAL_LIMITS

def _r(val, decimals=2):
    """Safely round values or return '—' for missing/invalid input."""
    if val == "—" or val is None: return "—"
    try: return round(float(val), decimals)
    except: return "—"

def calculate_thermal(S, P0, Pk, oil_type='mineral', delta_T=60.0, cooling_method='ONAN', ambient_temp=30.0, S_kVA=None, material_hv='Cu', material_lv='Cu', core_material='M4'):
    """
    Calculate thermal properties, oil volume/weight, cooling area, and hot-spot temperature.
    """
    try:
        S_val = float(S) if S != "—" and S is not None else 0
        P0_val = float(P0) if P0 != "—" and P0 is not None else 0
        Pk_val = float(Pk) if Pk != "—" and Pk is not None else 0
        delta_T = float(delta_T) if delta_T else 60.0
        ambient_temp = float(ambient_temp) if ambient_temp else 30.0
    except (TypeError, ValueError):
        return {}

    if S_kVA is None or S_kVA == "—":
        S_kVA = S_val / 1000.0 if S_val >= 1000.0 else S_val
    else:
        S_kVA = float(S_kVA)

    al_factor = 1.15 if (material_hv == 'Al' or material_lv == 'Al') else 1.0

    # 1. Oil volume (Litres) and Weight (kg)
    oil_volume_L = (S_kVA ** 0.8) * 4.5 * al_factor if S_kVA > 0 else 0
    oil_info = OIL_PROPERTIES.get(oil_type, OIL_PROPERTIES.get('mineral', {}))
    density = oil_info.get("density", 0.88)
    beta = oil_info.get("beta", 0.00075)

    oil_weight_kg = oil_volume_L * density
    expansion_volume_L = oil_volume_L * beta * delta_T

    # Core and tank approximate weights for structural physics
    mat_weight_factor = 1.05 if core_material == 'M5' else (0.95 if core_material == 'Amorf' else 1.0)
    core_w = (S_kVA ** 0.75) * 8.5 * mat_weight_factor * (1.15 if al_factor > 1.0 else 1.0)
    tank_w = (S_kVA ** 0.7) * 6.5 * (1.10 if al_factor > 1.0 else 1.0)
    conductor_w = (S_kVA * 1.2) if material_hv == 'Cu' else (S_kVA * 0.8)
    dry_weight_kg = conductor_w + core_w + tank_w
    wet_weight_kg = dry_weight_kg + oil_weight_kg

    # 2. Total heat dissipation (W)
    total_heat_loss_W = P0_val + Pk_val

    # 3. Cooling surface area (m²)
    cooling_info = COOLING_METHODS.get(cooling_method, COOLING_METHODS.get('ONAN', {}))
    q_specific = cooling_info.get("q_specific", 400)
    cooling_area_m2 = total_heat_loss_W / q_specific if q_specific > 0 else 0

    # 4. Top oil temperature rise (IEC 60076-2)
    n = cooling_info.get("oil_exponent", 0.8)
    top_oil_rise_C = delta_T

    # 5. Hot spot temperature (°C)
    H = 1.1 # hot-spot factor
    g_r = 23.0 # average winding to oil gradient
    hot_spot_temp_C = ambient_temp + top_oil_rise_C + (H * g_r)

    # 6. Thermal time constant (hours)
    C_thermal = (oil_weight_kg * 1.88 + core_w * 0.48 + conductor_w * 0.39) * 1000.0 # Ws/K
    thermal_time_constant_h = (C_thermal * top_oil_rise_C) / (total_heat_loss_W * 3600.0) if total_heat_loss_W > 0 else 2.5

    # 7. Conservator volume (Litres)
    conservator_volume_L = oil_volume_L * beta * 80.0 * 1.3

    # 8. Recommended cooling method
    if S_kVA <= 3150:
        recommended_cooling = 'ONAN'
    elif S_kVA <= 10000:
        recommended_cooling = 'ONAF'
    elif S_kVA <= 40000:
        recommended_cooling = 'OFAF'
    else:
        recommended_cooling = 'ODAF'

    limit_hs = THERMAL_LIMITS.get("hot_spot_absolute_max", 98)
    hot_spot_warning = hot_spot_temp_C > limit_hs

    return {
        "oil_volume_L": _r(oil_volume_L),
        "oil_weight_kg": _r(oil_weight_kg),
        "expansion_volume_L": _r(expansion_volume_L),
        "dry_weight_kg": _r(dry_weight_kg),
        "wet_weight_kg": _r(wet_weight_kg),
        "core_weight_kg": _r(core_w),
        "tank_weight_kg": _r(tank_w),
        "total_heat_loss_W": _r(total_heat_loss_W),
        "cooling_area_m2": _r(cooling_area_m2),
        "top_oil_rise_C": _r(top_oil_rise_C),
        "hot_spot_temp_C": _r(hot_spot_temp_C),
        "thermal_time_constant_h": _r(thermal_time_constant_h),
        "conservator_volume_L": _r(conservator_volume_L),
        "recommended_cooling": recommended_cooling,
        "cooling_method_used": cooling_method,
        "hot_spot_warning": hot_spot_warning,
        "oil_density": density,
        "expansion_coeff": beta
    }
