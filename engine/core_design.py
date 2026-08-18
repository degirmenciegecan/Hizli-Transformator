"""Core design calculations with dynamic power-dependent geometry (Module 2)"""
import math
from engine.constants import CORE_MATERIAL, CORE_STEPPING, get_core_geometry_ratios

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

def calculate_core_design(S, V1, V2, frequency, phase, core_material='M4', N1=None,
                          k_constant=0.45, Et=None, insulation_clearance_mm=None):
    """
    Calculates core design parameters based on Faraday EMF law and power-dependent
    dynamic 3-limb geometry (Directive 4).
    """
    try:
        S_val = float(S)
        S_kVA = S_val / 1000.0
        V1 = float(V1)
        V2 = float(V2)
        frequency = float(frequency) if frequency else 50.0
        phase = int(phase) if phase else 3
    except (TypeError, ValueError):
        return {}

    mat_props = CORE_MATERIAL.get(core_material, CORE_MATERIAL.get('M4', {}))
    Bm = mat_props.get("Bm_typical", 1.65)
    specific_loss = mat_props.get("specific_loss_1_7T", 1.0)
    density = mat_props.get("density", 7650)
    stacking_factor = mat_props.get("stacking_factor", 0.96)
    build_factor = mat_props.get("build_factor", 1.20)
    core_label = mat_props.get("name", str(core_material))

    K_step = CORE_STEPPING.get(7, 0.75)

    if Et is None or Et == '—' or float(Et or 0) <= 0:
        Et = k_constant * math.sqrt(S_kVA) if S_kVA > 0 else 1.0
    else:
        Et = float(Et)

    # 1. Faraday EMF Net Core Area (m^2)
    # E_t = 4.44 * f * Bm * Ai
    if frequency > 0 and Bm > 0:
        Ai_m2 = Et / (4.44 * frequency * Bm)
    else:
        Ai_m2 = 0

    Ai_cm2 = Ai_m2 * 10000.0
    Ag_cm2 = Ai_cm2 / stacking_factor if stacking_factor > 0 else 0
    Ag_m2 = Ag_cm2 / 10000.0

    # 2. Stepped Core Diameter (mm)
    if K_step > 0 and Ag_m2 > 0:
        core_diameter_m = math.sqrt((4.0 * Ag_m2) / (math.pi * K_step))
    else:
        core_diameter_m = 0
    core_diameter_mm = core_diameter_m * 1000.0

    # 3. Dynamic 3-Limb Core Geometry based on Rating (Directive 4)
    ratio_hw_d, ratio_a_d = get_core_geometry_ratios(S_kVA)
    
    limb_center_dist_mm = core_diameter_mm * ratio_a_d
    window_height_nominal_mm = core_diameter_mm * ratio_hw_d

    # Insulation & Dielectric clearance constraints (Minimum window height)
    min_window_height_mm = window_height_nominal_mm
    if insulation_clearance_mm is not None and insulation_clearance_mm != "—":
        try:
            ins_clr = float(insulation_clearance_mm)
            # Window must accommodate winding + top & bottom dielectric clearances (2x) + mechanical clamping
            min_window_height_mm = max(min_window_height_mm, (core_diameter_mm * 1.5) + (2.0 * ins_clr) + 40.0)
        except:
            pass

    window_height_mm = max(window_height_nominal_mm, min_window_height_mm)

    # 4. Core Weight (kg) based on physical 3-limb volume
    if phase == 3 and Ai_m2 > 0:
        # Total iron volume = 3 limbs + 4 yoke sections
        total_iron_length_m = (3.0 * (window_height_mm / 1000.0)) + (4.0 * (limb_center_dist_mm / 1000.0)) + (2.0 * core_diameter_m)
        Gc = total_iron_length_m * Ai_m2 * density * 1.05
    else:
        # Single phase 2-limb core
        total_iron_length_m = (2.0 * (window_height_mm / 1000.0)) + (2.0 * (limb_center_dist_mm / 1000.0))
        Gc = total_iron_length_m * Ai_m2 * density

    # 5. Specific loss (W/kg) scaling at actual Bm
    p_s = specific_loss * ((Bm / 1.7) ** 2)
    P0_calc = p_s * Gc * build_factor

    # 6. Steinmetz loss separation
    k_h = (specific_loss * 0.75) / (50.0 * (1.7 ** 1.8))
    P_hysteresis = k_h * frequency * (Bm ** 1.8) * Gc
    P_eddy = max(0, P0_calc - P_hysteresis)

    return {
        "Bm": _r(Bm),
        "Ai_cm2": _r(Ai_cm2),
        "Ag_cm2": _r(Ag_cm2),
        "core_diameter_mm": _r(core_diameter_mm),
        "limb_center_dist_mm": _r(limb_center_dist_mm),
        "window_height_mm": _r(window_height_mm),
        "ratio_hw_d": _r(ratio_hw_d, 2),
        "ratio_a_d": _r(ratio_a_d, 2),
        "core_weight_kg": _r(Gc, 1),
        "specific_loss_w_kg": _r(p_s, 3),
        "P0_estimated_W": _r(P0_calc),
        "core_label": core_label,
        "P_hysteresis_W": _r(P_hysteresis),
        "P_eddy_W": _r(P_eddy),
        "stacking_factor": _r(stacking_factor),
        "stepping_factor": _r(K_step)
    }
