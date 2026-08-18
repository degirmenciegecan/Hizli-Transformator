import math

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

def calculate_losses(S, P0, Pk, operating_hours=6000, load_factor=0.5, energy_price_kwh=0.10, co2_factor=0.47):
    """
    Calculates advanced losses and efficiency parameters.
    S: apparent power in kVA
    P0: no-load loss in W
    Pk: load-loss in W
    """
    try:
        S_VA = float(S) * 1000
        P0 = float(P0)
        Pk = float(Pk)
        operating_hours = float(operating_hours)
        load_factor = float(load_factor)
        energy_price_kwh = float(energy_price_kwh)
        co2_factor = float(co2_factor)
    except (TypeError, ValueError):
        return {}

    efficiency_table = []
    for x in [0.25, 0.50, 0.75, 1.00]:
        row = {"load": x}
        for cos_phi in [1.0, 0.9, 0.8]:
            out_power = x * S_VA * cos_phi
            losses = P0 + (x ** 2) * Pk
            if out_power + losses > 0:
                eff = (out_power / (out_power + losses)) * 100
            else:
                eff = 0
            row[f"cos_{cos_phi}"] = _r(eff, 3)
        efficiency_table.append(row)

    if Pk > 0:
        x_max = math.sqrt(P0 / Pk)
        loss_ratio = P0 / Pk
    else:
        x_max = 0
        loss_ratio = 0

    max_out_power = x_max * S_VA * 1.0
    max_losses = P0 + (x_max ** 2) * Pk
    if max_out_power + max_losses > 0:
        max_eff_value = (max_out_power / (max_out_power + max_losses)) * 100
    else:
        max_eff_value = 0

    annual_loss_kWh = (P0 * 8760 + Pk * (load_factor ** 2) * operating_hours) / 1000.0
    annual_cost_usd = annual_loss_kWh * energy_price_kwh
    co2_kg_year = annual_loss_kWh * co2_factor

    return {
        "efficiency_table": efficiency_table,
        "max_eff_load": _r(x_max, 4),
        "max_eff_value": _r(max_eff_value, 3),
        "annual_loss_kWh": _r(annual_loss_kWh),
        "annual_cost_usd": _r(annual_cost_usd),
        "co2_kg_year": _r(co2_kg_year),
        "loss_ratio": _r(loss_ratio, 4)
    }
