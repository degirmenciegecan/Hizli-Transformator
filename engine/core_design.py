"""Core design calculations (Module 2)"""
import math
from engine.constants import CORE_MATERIAL, CORE_STEPPING

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

def calculate_core_design(S, V1, V2, frequency, phase, core_material='M4', N1=None, k_constant=0.45):
    """
    Calculates core design parameters.
    S: apparent power in VA (or kVA if < 1000)
    V1: primary voltage in V
    V2: secondary voltage in V
    frequency: frequency in Hz
    phase: number of phases (1 or 3)
    core_material: string key for CORE_MATERIAL ('M3', 'M4', 'M5', 'Amorf')
    N1: primary turns (optional)
    k_constant: volts per turn constant (default 0.45)
    """
    try:
        S_val = float(S)
        S_kVA = S_val / 1000.0 if S_val >= 1000.0 else S_val
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

    if N1 is None or N1 == '—':
        Et = k_constant * math.sqrt(S_kVA) if S_kVA > 0 else 1.0
        N1 = max(1, round(V1 / Et))
    else:
        N1 = max(1, round(float(N1)))
        Et = V1 / N1

    # EMF equation: E = 4.44 * f * N1 * Bm * Ai
    # Net core area (m^2)
    if frequency > 0 and Bm > 0 and N1 > 0:
        Ai_m2 = V1 / (4.44 * frequency * N1 * Bm)
    else:
        Ai_m2 = 0

    Ai_cm2 = Ai_m2 * 10000.0
    Ag_cm2 = Ai_cm2 / stacking_factor if stacking_factor > 0 else 0
    Ag_m2 = Ag_cm2 / 10000.0

    if K_step > 0 and Ag_m2 > 0:
        core_diameter_m = math.sqrt((4.0 * Ag_m2) / (math.pi * K_step))
    else:
        core_diameter_m = 0
    core_diameter_mm = core_diameter_m * 1000.0

    # Core weight (kg)
    material_weight_factor = 1.05 if core_material == 'M5' else (0.95 if core_material == 'Amorf' else 1.0)
    Gc = (S_kVA ** 0.75) * 8.5 * material_weight_factor

    # Specific loss scaling at actual Bm
    p_s = specific_loss * ((Bm / 1.7) ** 2)
    P0_calc = p_s * Gc * build_factor

    # Steinmetz separation
    k_h = (specific_loss * 0.75) / (50.0 * (1.7 ** 1.8))
    P_hysteresis = k_h * frequency * (Bm ** 1.8) * Gc
    P_eddy = max(0, P0_calc - P_hysteresis)

    return {
        "Bm": _r(Bm),
        "Ai_cm2": _r(Ai_cm2),
        "Ag_cm2": _r(Ag_cm2),
        "core_diameter_mm": _r(core_diameter_mm),
        "core_weight_kg": _r(Gc, 1),
        "P0_estimated_W": _r(P0_calc),
        "core_label": core_label,
        "P_hysteresis_W": _r(P_hysteresis),
        "P_eddy_W": _r(P_eddy),
        "stacking_factor": _r(stacking_factor),
        "stepping_factor": _r(K_step)
    }
