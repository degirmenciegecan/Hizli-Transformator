"""Magnetization, no-load current components, and inrush dynamics (Module 12)"""
import math

def _r(val, decimals=2):
    """Safely round values or return '—' for missing/invalid input."""
    if val == "—" or val is None: return "—"
    try: return round(float(val), decimals)
    except: return "—"

def calculate_magnetization(V1, I1, P0, S, phase=3, Bm=None):
    """
    Calculate magnetization properties including no-load current components and inrush peak estimates.
    """
    try:
        V1_val = float(V1) if V1 != "—" and V1 is not None else 0
        I1_val = float(I1) if I1 != "—" and I1 is not None else 0
        P0_val = float(P0) if P0 != "—" and P0 is not None else 0
        S_val = float(S) if S != "—" and S is not None else 0
        phase_val = int(phase) if phase else 3
        Bm_val = float(Bm) if Bm is not None and Bm != "—" else 1.65
    except (TypeError, ValueError):
        return {}

    if V1_val <= 0 or I1_val <= 0:
        return {
            "Ic_A": "—", "Im_A": "—", "I0_A": "—", "I0_pct": "—",
            "cos_phi_0": "—", "inrush_peak_A": "—", "inrush_factor": 10,
            "inrush_time_constant_s": 0.5, "inrush_decay_s": 2.5
        }

    # 1. Loss component (core loss current)
    if phase_val == 3:
        Ic_A = P0_val / (math.sqrt(3.0) * V1_val)
    else:
        Ic_A = P0_val / V1_val

    # 2. Magnetizing current estimation based on standard power transformer statistics
    S_kVA = S_val / 1000.0 if S_val >= 1000.0 else S_val
    if S_kVA < 100:
        I0_pct_est = 1.8
        K_inrush = 8.5
    elif S_kVA <= 630:
        I0_pct_est = 0.65
        K_inrush = 6.2
    elif S_kVA <= 2500:
        I0_pct_est = 0.35
        # Scales smoothly between 4.5 and 5.5 for medium power units (matches factory sheets 4.79 - 5.29)
        K_inrush = 5.0 * (1.0 + (Bm_val - 1.35) * 0.5) if Bm_val else 5.0
    else:
        I0_pct_est = 0.20
        K_inrush = 4.2

    I0_target = I1_val * (I0_pct_est / 100.0)
    if I0_target > Ic_A:
        Im_A = math.sqrt(I0_target ** 2 - Ic_A ** 2)
    else:
        Im_A = I0_target * 0.9

    # 3. Vector sum no-load current
    I0_A = math.sqrt(Ic_A ** 2 + Im_A ** 2)
    I0_pct = (I0_A / I1_val) * 100.0

    # 4. No-load power factor (cos φ0)
    cos_phi_0 = (Ic_A / I0_A) if I0_A > 0 else 0.15

    # 5. Inrush current estimate (first cycle peak)
    inrush_peak_A = K_inrush * math.sqrt(2.0) * I1_val
    tau_inrush = 0.5
    inrush_decay_s = 5.0 * tau_inrush

    return {
        "Ic_A": _r(Ic_A, 3),
        "Im_A": _r(Im_A, 3),
        "I0_A": _r(I0_A, 3),
        "I0_pct": _r(I0_pct, 2),
        "cos_phi_0": _r(cos_phi_0, 4),
        "inrush_peak_A": _r(inrush_peak_A, 1),
        "inrush_peak_hv": _r(inrush_peak_A, 1),
        "inrush_factor": K_inrush,
        "inrush_ratio": K_inrush,
        "inrush_time_constant_s": tau_inrush,
        "inrush_decay_s": inrush_decay_s
    }
