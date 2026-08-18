"""
Parametric 2D transformer core, winding, and tank geometry calculations for CAD rendering.
"""

def calculate_cad_geometry(res):
    """
    Computes exact physical mm coordinates and bounding dimensions for:
    1. 3-Limb Magnetic Core (Limbs, Yokes, Windows)
    2. LV Windings on all 3 limbs
    3. HV Windings on all 3 limbs
    4. Oil Cooling Ducts & Insulation Barriers
    5. Transformer Tank Envelope & Oil Level
    """
    el = res.get('electrical', {})
    cd = res.get('core_design', {})
    wd = res.get('winding', {})
    th = res.get('thermal', {})

    # Core Dimensions (mm)
    D = float(cd.get('core_diameter_mm', 150))
    if D <= 0: D = 150.0

    ratio_hw, ratio_a = cd.get('ratio_hw_d', 2.7), cd.get('ratio_a_d', 2.08)
    A = float(cd.get('limb_center_dist_mm', D * ratio_a))
    Hw = float(cd.get('window_height_mm', D * ratio_hw))

    core_w = (2.0 * A) + D
    core_h = Hw + (2.0 * D)
    yoke_h = D * 0.95

    # Winding Dimensions (mm)
    lv_radial = max(15.0, D * 0.14)
    lv_h = max(50.0, Hw * 0.86)
    lv_inner_r = (D / 2.0) + 12.0
    lv_outer_r = lv_inner_r + lv_radial

    duct_radial = 15.0
    
    hv_radial = max(20.0, D * 0.18)
    hv_h = max(45.0, Hw * 0.82)
    hv_inner_r = lv_outer_r + duct_radial
    hv_outer_r = hv_inner_r + hv_radial

    # Compact, well-proportioned tank envelope (mm)
    tank_l = core_w + 140.0
    tank_w = (2.0 * hv_outer_r) + 120.0
    tank_h = core_h + 160.0
    oil_level_h = tank_h - 70.0

    # Center coordinates of 3 limbs
    limb_cx = [ -A, 0.0, A ]

    return {
        "core": {
            "D_mm": round(D, 1),
            "A_mm": round(A, 1),
            "Hw_mm": round(Hw, 1),
            "total_width_mm": round(core_w, 1),
            "total_height_mm": round(core_h, 1),
            "yoke_height_mm": round(yoke_h, 1),
            "limb_centers": [round(cx, 1) for cx in limb_cx]
        },
        "windings": {
            "lv": {
                "radial_mm": round(lv_radial, 1),
                "height_mm": round(lv_h, 1),
                "inner_r_mm": round(lv_inner_r, 1),
                "outer_r_mm": round(lv_outer_r, 1),
                "turns": el.get("N2", "—"),
                "area_mm2": el.get("A2", "—")
            },
            "hv": {
                "radial_mm": round(hv_radial, 1),
                "height_mm": round(hv_h, 1),
                "inner_r_mm": round(hv_inner_r, 1),
                "outer_r_mm": round(hv_outer_r, 1),
                "turns": el.get("N1", "—"),
                "area_mm2": el.get("A1", "—")
            },
            "duct_gap_mm": round(duct_radial, 1)
        },
        "tank": {
            "length_mm": round(tank_l, 1),
            "width_mm": round(tank_w, 1),
            "height_mm": round(tank_h, 1),
            "oil_level_mm": round(oil_level_h, 1),
            "oil_volume_L": th.get("oil_volume_L", "—")
        }
    }
