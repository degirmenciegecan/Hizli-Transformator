"""Insulation and dielectric standards calculations (Module 11)"""
from engine.constants import BIL_TABLE

def _r(val, decimals=2):
    if val == "—" or val is None: return "—"
    try: return round(float(val), decimals)
    except: return "—"

def get_bil_data(V):
    """
    Determine highest system voltage Um and retrieve BIL values from IEC 60076-3.
    V: line voltage in V
    """
    if V is None or V == "—":
        return 0, 0, 0, 1
    
    try:
        V_float = float(V)
    except (TypeError, ValueError):
        return 0, 0, 0, 1

    # Um (highest system voltage) in kV
    Um = (V_float * 1.1) / 1000.0 if V_float >= 1000.0 else (V_float * 1.1) / 1000.0
    if Um < 0.6:
        Um = 0.6

    bil_kVp = 0
    ac_test_kV = 0
    test_dur = 1

    # BIL_TABLE is a list of tuples: (max_voltage_kV, bil_kVp, ac_test_kV, test_duration_min)
    matched = False
    for row in BIL_TABLE:
        max_v, bil, ac_test, dur = row
        if Um <= max_v:
            bil_kVp = bil if bil is not None else 0
            ac_test_kV = ac_test if ac_test is not None else 0
            test_dur = dur
            matched = True
            break

    if not matched and BIL_TABLE:
        # If higher than table max, extrapolate
        last_row = BIL_TABLE[-1]
        bil_kVp = last_row[1] or 850
        ac_test_kV = last_row[2] or 360
        test_dur = last_row[3]

    if bil_kVp == 0:
        bil_kVp = max(Um * 5.0, 10.0) if Um > 1.1 else 0
    if ac_test_kV == 0:
        ac_test_kV = bil_kVp / 2.5 if bil_kVp > 0 else 3.0

    return Um, bil_kVp, ac_test_kV, test_dur

def calculate_insulation(V1, V2, phase=3):
    """
    Calculate insulation and dielectric properties for HV and LV sides.
    """
    hv_Um, hv_bil, hv_ac, hv_dur = get_bil_data(V1)
    lv_Um, lv_bil, lv_ac, lv_dur = get_bil_data(V2)

    hv_creepage_mm = (hv_bil / 2.5) if hv_bil > 0 else (hv_ac * 10)
    hv_oil_mm = (hv_bil / 5.0) if hv_bil > 0 else (hv_ac * 5)

    lv_creepage_mm = (lv_bil / 2.5) if lv_bil > 0 else (lv_ac * 10)
    lv_oil_mm = (lv_bil / 5.0) if lv_bil > 0 else (lv_ac * 5)

    return {
        "hv_Um_kV": _r(hv_Um, 2),
        "hv_BIL_kVp": _r(hv_bil, 1) if hv_bil > 0 else "—",
        "hv_AC_test_kV": _r(hv_ac, 1),
        "hv_test_duration_min": hv_dur,
        "hv_creepage_mm": _r(hv_creepage_mm, 1),
        "creepage_distance_mm": _r(hv_creepage_mm, 1),
        "lv_Um_kV": _r(lv_Um, 2),
        "lv_BIL_kVp": _r(lv_bil, 1) if lv_bil > 0 else "—",
        "lv_AC_test_kV": _r(lv_ac, 1),
        "lv_test_duration_min": lv_dur,
        "lv_creepage_mm": _r(lv_creepage_mm, 1),
        "oil_clearance_hv_mm": _r(hv_oil_mm, 1),
        "clearance_oil_mm": _r(hv_oil_mm, 1),
        "oil_clearance_lv_mm": _r(lv_oil_mm, 1)
    }
