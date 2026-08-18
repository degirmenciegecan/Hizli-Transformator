import math

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

def calculate_voltage_regulation(V2, ur_pct, ux_pct, uk):
    """
    Calculates voltage regulation.
    V2: secondary voltage
    ur_pct: resistive short-circuit voltage %
    ux_pct: reactive short-circuit voltage %
    uk: impedance voltage %
    """
    try:
        V2 = float(V2)
        ur = float(ur_pct)
        ux = float(ux_pct)
        uk = float(uk)
    except (TypeError, ValueError):
        return {}

    regulation_table = []
    for cos_phi in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]:
        sin_phi = math.sqrt(max(0, 1 - cos_phi**2))
        epsilon = ur * cos_phi + ux * sin_phi + ((ux * cos_phi - ur * sin_phi) ** 2) / 200.0
        v2_loaded = V2 * (1 - epsilon / 100.0)
        regulation_table.append({
            "cos_phi": cos_phi,
            "regulation_pct": _r(epsilon, 3),
            "V2_loaded": _r(v2_loaded, 2)
        })

    if uk > 0:
        max_reg_cos_phi = ur / uk
        sin_phi_max = ux / uk
        max_reg_pct = ur * max_reg_cos_phi + ux * sin_phi_max + ((ux * max_reg_cos_phi - ur * sin_phi_max) ** 2) / 200.0
        zero_reg_cos_phi = ux / uk
    else:
        max_reg_cos_phi = 1.0
        max_reg_pct = 0.0
        zero_reg_cos_phi = 0.0

    return {
        "regulation_table": regulation_table,
        "max_reg_cos_phi": _r(max_reg_cos_phi, 4),
        "max_reg_pct": _r(max_reg_pct, 3),
        "zero_reg_cos_phi": _r(zero_reg_cos_phi, 4)
    }
