"""
⚡ Hızlı Transformatör - Core Multi-Module Engineering Engine
Provides high-performance analytical, thermal, dielectric, and economic calculations for power transformers.
"""

import math
from engine.constants import CONDUCTOR, CORE_MATERIAL, OIL_PROPERTIES
from engine.electrical import calculate_electrical
from engine.core_design import calculate_core_design
from engine.losses import calculate_losses
from engine.voltage_reg import calculate_voltage_regulation
from engine.short_circuit import calculate_short_circuit
from engine.winding import calculate_winding
from engine.thermal import calculate_thermal
from engine.economic import calculate_economic
from engine.insulation import calculate_insulation
from engine.magnetization import calculate_magnetization

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

def safe_float(v, default=None):
    if v is None or v == '' or v == '—':
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default

def calculate_all(data, metal_prices=None, metal_sources=None):
    """
    Unified entry point for complete transformer characterization.
    
    Args:
        data (dict): Input parameters from form or API request
        metal_prices (dict, optional): Live prices dict {'copper_usd_kg': float, 'aluminum_usd_kg': float, 'usd_try': float}
        metal_sources (dict, optional): URLs for live price citations
    
    Returns:
        dict: Complete JSON-serializable engineering report
    """
    if data is None:
        data = {}

    # Extract & sanitize inputs
    S = safe_float(data.get('S'), 50000.0) # Apparent power in VA
    V1 = safe_float(data.get('V1'), 34500.0)
    V2 = safe_float(data.get('V2'), 400.0)
    phase = int(safe_float(data.get('phase'), 3))
    frequency = safe_float(data.get('frequency'), 50.0)
    uk = safe_float(data.get('uk'), 4.5)
    P0 = safe_float(data.get('P0'), 150.0)
    Pk = safe_float(data.get('Pk'), 900.0)

    oil_type = data.get('oil_type', 'mineral')
    k_constant = safe_float(data.get('k_constant'), 0.45)
    delta_T = safe_float(data.get('delta_T'), 60.0)
    material_hv = data.get('material_hv', 'Cu')
    material_lv = data.get('material_lv', 'Cu')
    core_material = data.get('core_material', 'M4')
    A_factor = safe_float(data.get('A_factor'), 8.0)
    B_factor = safe_float(data.get('B_factor'), 2.0)
    cooling_method = data.get('cooling_method', 'ONAN')
    ambient_temp = safe_float(data.get('ambient_temp'), 30.0)

    S_kVA = S / 1000.0 if S else 50.0

    # Default prices if not passed
    if metal_prices is None:
        metal_prices = {
            "copper_usd_kg": 9.50,
            "aluminum_usd_kg": 2.50,
            "usd_try": 34.00
        }
    if metal_sources is None:
        metal_sources = {"copper": "", "aluminum": "", "usd_try": ""}

    # 1. Module 1 & 3: Electrical Parameters & Equivalent Circuit
    electrical = calculate_electrical(
        S=S, V1=V1, V2=V2, uk=uk, P0=P0, Pk=Pk,
        phase=phase, frequency=frequency, k_constant=k_constant,
        material_hv=material_hv, material_lv=material_lv
    )

    N1 = electrical.get('N1')
    N2 = electrical.get('N2')
    I1 = electrical.get('I1')
    I2 = electrical.get('I2')
    Rk = electrical.get('Rk')
    Xk = electrical.get('Xk')
    Zk = electrical.get('Zk')
    ur_pct = electrical.get('ur_pct')
    ux_pct = electrical.get('ux_pct')
    A1 = electrical.get('A1')
    A2 = electrical.get('A2')

    # 2. Module 2: Core Design
    core_design = calculate_core_design(
        S=S, V1=V1, V2=V2, frequency=frequency,
        phase=phase, core_material=core_material, N1=N1,
        k_constant=k_constant
    )
    core_diameter_mm = core_design.get('core_diameter_mm')
    Bm = core_design.get('Bm')
    core_weight_val = core_design.get('core_weight_kg', 0)

    # 3. Module 4: Losses & Efficiency Grid
    losses = calculate_losses(
        S=S_kVA, P0=P0, Pk=Pk,
        operating_hours=6000, load_factor=0.5,
        energy_price_kwh=0.10, co2_factor=0.47
    )

    # 4. Module 5: Voltage Regulation
    voltage_reg = calculate_voltage_regulation(
        V2=V2, ur_pct=ur_pct, ux_pct=ux_pct, uk=uk
    )

    # 5. Module 6: Short Circuit Analysis
    short_circuit = calculate_short_circuit(
        I1=I1, I2=I2, uk=uk, Rk=Rk, Xk=Xk, Zk=Zk,
        V1=V1, V2=V2, phase=phase, N1=N1, N2=N2,
        core_diameter_mm=core_diameter_mm
    )

    # 6. Module 7: Winding Design
    winding = calculate_winding(
        I1=I1, I2=I2, N1=N1, N2=N2,
        A1_mm2=A1, A2_mm2=A2,
        material_hv=material_hv, material_lv=material_lv,
        frequency=frequency, core_diameter_mm=core_diameter_mm,
        S_kVA=S_kVA
    )

    # 7. Module 8: Thermal Analysis
    thermal = calculate_thermal(
        S=S, P0=P0, Pk=Pk, oil_type=oil_type,
        delta_T=delta_T, cooling_method=cooling_method,
        ambient_temp=ambient_temp, S_kVA=S_kVA,
        material_hv=material_hv, material_lv=material_lv,
        core_material=core_material
    )

    # 8. Module 11: Insulation & Dielectric Standards
    insulation = calculate_insulation(V1=V1, V2=V2, phase=phase)

    # 9. Module 12: Magnetization & Inrush Current
    magnetization = calculate_magnetization(
        V1=V1, I1=I1, P0=P0, S=S, phase=phase, Bm=Bm
    )

    # 10. Cost & Material Bill Calculations
    cu_price = float(metal_prices.get("copper_usd_kg", 9.50))
    al_price = float(metal_prices.get("aluminum_usd_kg", 2.50))

    weight_hv = (S_kVA * 1.2 / 2.0) if material_hv == 'Cu' else (S_kVA * 0.8 / 2.0)
    weight_lv = (S_kVA * 1.2 / 2.0) if material_lv == 'Cu' else (S_kVA * 0.8 / 2.0)

    cost_hv = weight_hv * (cu_price if material_hv == 'Cu' else al_price)
    cost_lv = weight_lv * (cu_price if material_lv == 'Cu' else al_price)
    total_conductor_cost = cost_hv + cost_lv
    total_conductor_weight = weight_hv + weight_lv

    cw_float = float(core_weight_val) if core_weight_val != "—" else 0
    tw_float = float(thermal.get('tank_weight_kg', 0)) if thermal.get('tank_weight_kg') != "—" else 0
    ow_float = float(thermal.get('oil_weight_kg', 0)) if thermal.get('oil_weight_kg') != "—" else 0

    # Total estimated manufacturing purchase price
    purchase_price = (total_conductor_cost * 1.5) + (cw_float * 3.0) + (tw_float * 1.5) + (ow_float * 1.2)

    # 11. Module 10: Economic & TOC Analysis
    economic = calculate_economic(
        S=S_kVA, P0=P0, Pk=Pk,
        A_factor=A_factor, B_factor=B_factor,
        total_purchase_price=purchase_price,
        energy_price_kwh=0.10, discount_rate=0.08,
        transformer_life_years=25, operating_hours=6000, load_factor=0.5
    )

    # Compile Backward-Compatible Objects
    legacy_cost = {
        "prices": {
            "copper": _r(cu_price),
            "aluminum": _r(al_price)
        },
        "sources": metal_sources,
        "weights": {
            "hv": _r(weight_hv),
            "lv": _r(weight_lv),
            "total": _r(total_conductor_weight),
            "core_weight": _r(cw_float),
            "tank_weight": _r(tw_float),
            "dry": _r(thermal.get('dry_weight_kg')),
            "wet": _r(thermal.get('wet_weight_kg'))
        },
        "materials": {
            "hv": material_hv,
            "lv": material_lv
        },
        "total": {
            "hv": _r(cost_hv),
            "lv": _r(cost_lv),
            "total_cost": _r(total_conductor_cost)
        }
    }

    legacy_toc = {
        "loss_cost": _r(economic.get('loss_cost_usd')),
        "toc": _r(economic.get('toc_usd')),
        "core_label": core_design.get('core_label', 'M4 Silisli Sac (Standart)'),
        "core_weight": _r(cw_float, 1)
    }

    legacy_thermo = {
        "total_heat_loss": _r(thermal.get('total_heat_loss_W')),
        "cooling_area_m2": _r(thermal.get('cooling_area_m2')),
        "expansion_volume_L": _r(thermal.get('expansion_volume_L')),
        "oil_volume_L": _r(thermal.get('oil_volume_L')),
        "oil_weight_kg": _r(thermal.get('oil_weight_kg')),
        "oil_density": thermal.get('oil_density', 0.88),
        "expansion_coeff": thermal.get('expansion_coeff', 0.00075)
    }

    return {
        "success": True,
        # Legacy frontend interfaces
        "electrical": electrical,
        "thermo": legacy_thermo,
        "cost": legacy_cost,
        "toc_analysis": legacy_toc,
        "prices": {
            "copper": _r(cu_price),
            "aluminum": _r(al_price),
            "usd_try": metal_prices.get("usd_try", 34.00)
        },
        "sources": metal_sources,

        # Full New Modular Architecture
        "core_design": core_design,
        "losses": losses,
        "voltage_regulation": voltage_reg,
        "short_circuit": short_circuit,
        "winding": winding,
        "thermal": thermal,
        "insulation": insulation,
        "magnetization": magnetization,
        "economic": economic
    }
