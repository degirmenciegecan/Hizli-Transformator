"""Core electrical parameter calculations for power transformers."""
import math
from engine.constants import CONDUCTOR, VECTOR_GROUPS

def _r(val, decimals=2):
    """Safe rounding helper."""
    if val == '—' or val is None:
        return '—'
    try:
        return round(float(val), decimals)
    except:
        return '—'

def calculate_electrical(S, V1, V2, uk, P0, Pk, phase=3, frequency=50.0, 
                          k_constant=0.45, material_hv='Cu', material_lv='Cu',
                          vector_group='Dyn11'):
    """
    Calculate all basic electrical parameters with dynamic vector group support.
    
    Args:
        S: Apparent power (VA)
        V1: Primary voltage (V)
        V2: Secondary voltage (V)
        uk: Short circuit impedance (%)
        P0: No-load loss (W)
        Pk: Load loss (W)
        phase: Number of phases (1 or 3)
        frequency: Operating frequency (Hz)
        k_constant: Volts-per-turn constant
        material_hv: Primary winding material ('Cu' or 'Al')
        material_lv: Secondary winding material ('Cu' or 'Al')
        vector_group: Three-phase vector group (Dyn11, Dyn1, Yyn0, YNyn0, Yd11, Yd1, Dd0)
    
    Returns:
        dict with all electrical parameters
    """
    try:
        S = float(S)
        V1 = float(V1)
        V2 = float(V2)
        uk = float(uk)
        P0 = float(P0)
        Pk = float(Pk)
        phase = int(phase)
        frequency = float(frequency)
    except (ValueError, TypeError):
        return {}

    S_kVA = S / 1000.0
    
    # Volts per turn
    Et = k_constant * math.sqrt(S_kVA) if S_kVA > 0 else 0
    
    # Vector group resolution
    vg_key = str(vector_group).strip() if vector_group else 'Dyn11'
    vg_info = VECTOR_GROUPS.get(vg_key, VECTOR_GROUPS.get('Dyn11', {}))
    
    primary_conn = vg_info.get('primary_conn', 'D')
    secondary_conn = vg_info.get('secondary_conn', 'yn')
    phase_shift_deg = vg_info.get('phase_displacement_deg', 330)
    clock_notation = vg_info.get('clock', 11)
    vg_name = vg_info.get('name', f"{vg_key}")

    # Phase voltages and currents based on vector group
    if phase == 3:
        I1 = S / (math.sqrt(3.0) * V1) if V1 != 0 else 0
        I2 = S / (math.sqrt(3.0) * V2) if V2 != 0 else 0

        # Primary connection (D: Delta, Y/YN: Star)
        if primary_conn == 'D':
            V1_phase = V1
            I1_phase = I1 / math.sqrt(3.0)
        else:
            V1_phase = V1 / math.sqrt(3.0)
            I1_phase = I1

        # Secondary connection (d: Delta, y/yn: Star)
        if secondary_conn == 'd':
            V2_phase = V2
            I2_phase = I2 / math.sqrt(3.0)
        else:
            V2_phase = V2 / math.sqrt(3.0)
            I2_phase = I2
    else:
        primary_conn = '1-Faz'
        secondary_conn = '1-Faz'
        phase_shift_deg = 0
        clock_notation = 0
        vg_name = '1-Faz (Monofaze)'
        V1_phase = V1
        V2_phase = V2
        I1 = S / V1 if V1 != 0 else 0
        I2 = S / V2 if V2 != 0 else 0
        I1_phase = I1
        I2_phase = I2

    # Turns
    N1 = V1_phase / Et if Et != 0 else 0
    N2 = V2_phase / Et if Et != 0 else 0
    
    # Transformation ratio (Turns ratio N1/N2 = V1_phase / V2_phase)
    a = N1 / N2 if N2 != 0 else (V1_phase / V2_phase if V2_phase != 0 else 0)
    a_line = V1 / V2 if V2 != 0 else 0
    
    # Short circuit voltage
    Vk = (uk / 100.0) * V1
    
    # Per-phase wye-equivalent impedances referred to primary
    if phase == 3:
        Zk = Vk / (math.sqrt(3.0) * I1) if I1 != 0 else 0
        Rk = Pk / (3.0 * (I1 ** 2)) if I1 != 0 else 0
    else:
        Zk = Vk / I1 if I1 != 0 else 0
        Rk = Pk / (I1 ** 2) if I1 != 0 else 0
        
    Xk = math.sqrt(Zk**2 - Rk**2) if Zk >= Rk else 0
    
    Lk = Xk / (2.0 * math.pi * frequency) if frequency != 0 else 0
    Lk_mH = Lk * 1000.0
    
    ur_pct = (Pk / S) * 100.0 if S != 0 else 0
    ux_pct = math.sqrt(uk**2 - ur_pct**2) if uk >= ur_pct else 0
    
    # Efficiency & Regulation
    efficiency = S / (S + P0 + Pk) * 100.0 if (S + P0 + Pk) != 0 else 0
    max_efficiency_load = math.sqrt(P0 / Pk) if Pk > 0 else 0
    
    # Voltage regulation at cosφ=0.8
    cos_phi = 0.8
    sin_phi = 0.6
    voltage_regulation = (ur_pct * cos_phi + ux_pct * sin_phi) + ((ux_pct * cos_phi - ur_pct * sin_phi)**2) / 200.0
    
    # Conductor densities and areas (based on winding phase current)
    J_hv = CONDUCTOR.get(material_hv, {}).get('J_default_hv', CONDUCTOR.get(material_hv, {}).get('J_default', 2.0))
    J_lv = CONDUCTOR.get(material_lv, {}).get('J_default_lv', CONDUCTOR.get(material_lv, {}).get('J_default', 2.3))
    
    A1 = I1_phase / J_hv if J_hv != 0 else 0
    A2 = I2_phase / J_lv if J_lv != 0 else 0
    ampere_turns = I1_phase * N1 if N1 > 0 else 0
    
    return {
        'S_kVA': _r(S_kVA),
        'vector_group': vg_key,
        'vector_group_name': vg_name,
        'primary_connection': primary_conn,
        'secondary_connection': secondary_conn,
        'phase_displacement_deg': phase_shift_deg,
        'clock_notation': clock_notation,
        'Et': _r(Et),
        'N1': _r(N1),
        'N2': _r(N2),
        'I1': _r(I1),
        'I2': _r(I2),
        'I1_phase': _r(I1_phase),
        'I2_phase': _r(I2_phase),
        'V1_phase': _r(V1_phase),
        'V2_phase': _r(V2_phase),
        'ampere_turns': _r(ampere_turns, 1),
        'a': _r(a, 4),
        'a_line': _r(a_line, 4),
        'Vk': _r(Vk),
        'Zk': _r(Zk, 4),
        'Rk': _r(Rk, 4),
        'Xk': _r(Xk, 4),
        'Lk': _r(Lk, 6),
        'Lk_mH': _r(Lk_mH, 4),
        'ur_pct': _r(ur_pct),
        'ux_pct': _r(ux_pct),
        'efficiency': _r(efficiency, 3),
        'max_efficiency_load': _r(max_efficiency_load, 3),
        'voltage_regulation': _r(voltage_regulation),
        'J_hv': _r(J_hv),
        'J_lv': _r(J_lv),
        'A1': _r(A1),
        'A2': _r(A2)
    }
