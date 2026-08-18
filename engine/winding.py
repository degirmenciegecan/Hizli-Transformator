"""Winding design calculations with DC, Eddy, and Stray loss analysis (Module 7)"""
import math
from engine.constants import CONDUCTOR, VECTOR_GROUPS

def _r(val, decimals=2):
    """Safely round values or return '—' for missing/invalid input."""
    if val == "—" or val is None: return "—"
    try: return round(float(val), decimals)
    except: return "—"

def calculate_winding(I1, I2, N1, N2, A1_mm2, A2_mm2, material_hv='Cu', material_lv='Cu',
                      frequency=50.0, core_diameter_mm=None, S_kVA=None, phase=3,
                      vector_group='Dyn11', I1_phase=None, I2_phase=None):
    """
    Calculate winding design parameters, DC copper losses, conductor eddy losses (Kec),
    and stray load losses in compliance with IEC 60076-1.
    """
    try:
        I1 = float(I1) if I1 != "—" and I1 is not None else 0
        I2 = float(I2) if I2 != "—" and I2 is not None else 0
        N1 = float(N1) if N1 != "—" and N1 is not None else 0
        N2 = float(N2) if N2 != "—" and N2 is not None else 0
        A1_mm2 = float(A1_mm2) if A1_mm2 != "—" and A1_mm2 is not None else 0
        A2_mm2 = float(A2_mm2) if A2_mm2 != "—" and A2_mm2 is not None else 0
        phase_count = int(phase) if phase else 3
        freq = float(frequency) if frequency else 50.0
    except (TypeError, ValueError):
        return {}

    s_k = float(S_kVA) if S_kVA is not None and S_kVA != "—" else 50.0

    if core_diameter_mm is None or core_diameter_mm == "—" or core_diameter_mm == 0:
        core_diameter_mm = 50.0 * (s_k ** 0.25)
    else:
        core_diameter_mm = float(core_diameter_mm)

    # 1. Conductor diameter (for round wire equivalent)
    d_conductor_hv_mm = math.sqrt(4.0 * A1_mm2 / math.pi) if A1_mm2 > 0 else 0
    d_conductor_lv_mm = math.sqrt(4.0 * A2_mm2 / math.pi) if A2_mm2 > 0 else 0

    # 2. Parallel conductors (practical flat/foil strip limit ~12-16 mm²)
    n_parallel_hv = max(1, math.ceil(A1_mm2 / 12.0)) if A1_mm2 > 12.0 else 1
    n_parallel_lv = max(1, math.ceil(A2_mm2 / 12.0)) if A2_mm2 > 12.0 else 1

    # 3. Mean Length of Turn (MLT)
    # Accounting for core tube, LV foil/layer radial depth, duct, and HV disc spacing
    MLT_lv_mm = math.pi * (core_diameter_mm + 70.0)
    MLT_hv_mm = math.pi * (core_diameter_mm + 170.0)

    # 4. Conductor length per phase (m)
    L_hv_phase = (N1 * MLT_hv_mm) / 1000.0
    L_lv_phase = (N2 * MLT_lv_mm) / 1000.0
    total_L_hv = L_hv_phase * phase_count
    total_L_lv = L_lv_phase * phase_count

    # 5. Resistivity, Temperature Coefficient and Skin Depth (at 75°C)
    mat_hv = CONDUCTOR.get(material_hv, CONDUCTOR.get('Cu', {}))
    mat_lv = CONDUCTOR.get(material_lv, CONDUCTOR.get('Cu', {}))

    rho_20_hv = mat_hv.get("resistivity_20", 1.724e-8)
    rho_20_lv = mat_lv.get("resistivity_20", 1.724e-8)
    alpha_hv = mat_hv.get("temp_coeff", 0.00393)
    alpha_lv = mat_lv.get("temp_coeff", 0.00393)
    density_hv = mat_hv.get("density", 8900)
    density_lv = mat_lv.get("density", 8900)

    rho_75_hv = rho_20_hv * (1.0 + alpha_hv * 55.0)
    rho_75_lv = rho_20_lv * (1.0 + alpha_lv * 55.0)

    mu_0 = 4.0 * math.pi * 1e-7  # H/m
    skin_depth_hv = math.sqrt(rho_75_hv / (math.pi * freq * mu_0)) if freq > 0 else 0.010
    skin_depth_lv = math.sqrt(rho_75_lv / (math.pi * freq * mu_0)) if freq > 0 else 0.010

    # 6. Resistance per phase at 20°C & 75°C
    R_20_hv = (rho_20_hv * L_hv_phase) / (A1_mm2 * 1e-6) if A1_mm2 > 0 else 0
    R_20_lv = (rho_20_lv * L_lv_phase) / (A2_mm2 * 1e-6) if A2_mm2 > 0 else 0

    R_75_hv = R_20_hv * (1.0 + alpha_hv * 55.0)
    R_75_lv = R_20_lv * (1.0 + alpha_lv * 55.0)

    # 7. Phase currents according to Vector Group
    vg_info = VECTOR_GROUPS.get(str(vector_group).strip(), VECTOR_GROUPS.get('Dyn11', {}))
    if I1_phase is not None and I1_phase != "—":
        i1_ph = float(I1_phase)
    else:
        if phase_count == 3:
            i1_ph = I1 / math.sqrt(3.0) if vg_info.get('primary_conn') == 'D' else I1
        else:
            i1_ph = I1

    if I2_phase is not None and I2_phase != "—":
        i2_ph = float(I2_phase)
    else:
        if phase_count == 3:
            i2_ph = I2 / math.sqrt(3.0) if vg_info.get('secondary_conn') == 'd' else I2
        else:
            i2_ph = I2

    # 8. DC I²R Copper Losses at 75°C
    P_dc_hv_W = phase_count * (i1_ph ** 2) * R_75_hv
    P_dc_lv_W = phase_count * (i2_ph ** 2) * R_75_lv
    P_dc_total_W = P_dc_hv_W + P_dc_lv_W

    # 9. Eddy Current Loss Factor (Kec) & Winding Eddy Losses
    # Formulated from transformer leakage field analysis (IEC 60076 / J&P Transformer Book)
    # Kec = (π² / 6) × (n_eff × d_radial / δ)²
    d_hv_radial_mm = min(3.5, max(1.0, math.sqrt(4.0 * (A1_mm2 / n_parallel_hv) / math.pi))) if A1_mm2 > 0 else 1.5
    d_lv_radial_mm = min(2.5, max(0.6, 0.8 + 0.4 * math.log10(max(1.0, s_k / 50.0)))) if A2_mm2 > 0 else 1.2

    d_hv_m = d_hv_radial_mm * 1e-3
    d_lv_m = d_lv_radial_mm * 1e-3

    n_eff_hv = min(2.0, max(1.0, 1.0 + 0.1 * math.log10(max(1.0, N1 / 100.0))))
    n_eff_lv = min(1.8, max(1.0, 1.0 + 0.15 * math.log10(max(1.0, N2 / 10.0))))

    Kec_hv = (math.pi**2 / 6.0) * ((n_eff_hv * d_hv_m / skin_depth_hv) ** 2) if skin_depth_hv > 0 else 0
    Kec_lv = (math.pi**2 / 6.0) * ((n_eff_lv * d_lv_m / skin_depth_lv) ** 2) if skin_depth_lv > 0 else 0

    # Safeguard bounds for standard winding constructions [0.5% - 25%]
    Kec_hv = min(0.25, max(0.005, Kec_hv))
    Kec_lv = min(0.25, max(0.005, Kec_lv))

    P_eddy_hv_W = P_dc_hv_W * Kec_hv
    P_eddy_lv_W = P_dc_lv_W * Kec_lv
    P_eddy_total_W = P_eddy_hv_W + P_eddy_lv_W
    Kec_total = (P_eddy_total_W / P_dc_total_W) if P_dc_total_W > 0 else 0

    # 10. Stray Losses (Structural steel, tank wall, clamps)
    # Scaled progressively with power rating from 3% to 8% of DC losses
    K_stray = min(0.08, max(0.03, 0.03 + 0.015 * math.log10(max(1.0, s_k / 25.0))))
    P_stray_W = P_dc_total_W * K_stray

    # 11. Total Calculated Load Loss (Pk_calculated_total)
    Pk_calculated_total_W = P_dc_total_W + P_eddy_total_W + P_stray_W

    # 12. Physical conductor weights
    weight_hv_kg = total_L_hv * (A1_mm2 * 1e-6) * density_hv
    weight_lv_kg = total_L_lv * (A2_mm2 * 1e-6) * density_lv

    return {
        "d_conductor_hv_mm": _r(d_conductor_hv_mm),
        "d_conductor_lv_mm": _r(d_conductor_lv_mm),
        "hv_conductor_dia_mm": _r(d_conductor_hv_mm),
        "lv_conductor_dia_mm": _r(d_conductor_lv_mm),
        "n_parallel_hv": n_parallel_hv,
        "n_parallel_lv": n_parallel_lv,
        "MLT_hv_mm": _r(MLT_hv_mm),
        "MLT_lv_mm": _r(MLT_lv_mm),
        "R_hv_75": _r(R_75_hv, 4),
        "R_lv_75": _r(R_75_lv, 4),
        "R_75C_hv_ohm": _r(R_75_hv, 4),
        "R_75C_lv_ohm": _r(R_75_lv, 4),
        "P_cu_hv_W": _r(P_dc_hv_W),
        "P_cu_lv_W": _r(P_dc_lv_W),
        "P_cu_total_W": _r(P_dc_total_W),
        
        # New loss components (Directive 1)
        "pk_dc_only": _r(P_dc_total_W),
        "pk_dc_hv_W": _r(P_dc_hv_W),
        "pk_dc_lv_W": _r(P_dc_lv_W),
        "pk_eddy": _r(P_eddy_total_W),
        "pk_eddy_hv_W": _r(P_eddy_hv_W),
        "pk_eddy_lv_W": _r(P_eddy_lv_W),
        "pk_eddy_pct": _r(Kec_total * 100.0, 2),
        "Kec_hv_pct": _r(Kec_hv * 100.0, 2),
        "Kec_lv_pct": _r(Kec_lv * 100.0, 2),
        "pk_stray": _r(P_stray_W),
        "pk_stray_pct": _r(K_stray * 100.0, 2),
        "pk_calculated_total": _r(Pk_calculated_total_W),
        "skin_depth_hv_mm": _r(skin_depth_hv * 1000.0, 2),
        "skin_depth_lv_mm": _r(skin_depth_lv * 1000.0, 2),

        "weight_hv_kg": _r(weight_hv_kg),
        "weight_lv_kg": _r(weight_lv_kg),
        "total_conductor_length_hv_m": _r(total_L_hv),
        "total_conductor_length_lv_m": _r(total_L_lv)
    }
