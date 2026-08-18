"""Core electrical parameter calculations for power transformers."""
import math
from engine.constants import CONDUCTOR

def _r(val, decimals=2):
    """Safe rounding helper."""
    if val == '—' or val is None:
        return '—'
    try:
        return round(float(val), decimals)
    except:
        return '—'

def calculate_electrical(S, V1, V2, uk, P0, Pk, phase=3, frequency=50.0, 
                          k_constant=0.45, material_hv='Cu', material_lv='Cu'):
    """
    Calculate all basic electrical parameters.
    
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
    Et = k_constant * math.sqrt(S_kVA)
    
    # Turns
    N1 = V1 / Et if Et != 0 else 0
    N2 = V2 / Et if Et != 0 else 0
    
    # Currents
    if phase == 3:
        I1 = S / (math.sqrt(3) * V1) if V1 != 0 else 0
        I2 = S / (math.sqrt(3) * V2) if V2 != 0 else 0
    else:
        I1 = S / V1 if V1 != 0 else 0
        I2 = S / V2 if V2 != 0 else 0
        
    # Transformation ratio
    a = V1 / V2 if V2 != 0 else 0
    
    # Short circuit voltage
    Vk = (uk / 100.0) * V1
    
    # Impedances
    if phase == 3:
        Zk = Vk / (math.sqrt(3) * I1) if I1 != 0 else 0
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
    
    # Conductor densities and areas
    J_hv = CONDUCTOR.get(material_hv, {}).get('J_default', 3.0)
    J_lv = CONDUCTOR.get(material_lv, {}).get('J_default', 3.0)
    
    A1 = I1 / J_hv if J_hv != 0 else 0
    A2 = I2 / J_lv if J_lv != 0 else 0
    
    return {
        'S_kVA': _r(S_kVA),
        'Et': _r(Et),
        'N1': _r(N1),
        'N2': _r(N2),
        'I1': _r(I1),
        'I2': _r(I2),
        'a': _r(a, 4),
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
