"""Economic analysis, TOC and Life Cycle Cost (Module 10)"""
import math

def _r(val, decimals=2):
    """Safely round values or return '—' for missing/invalid input."""
    if val == "—" or val is None: return "—"
    try: return round(float(val), decimals)
    except: return "—"

def calculate_economic(S, P0, Pk, A_factor=None, B_factor=None, total_purchase_price=0, energy_price_kwh=0.10, discount_rate=0.08, transformer_life_years=25, operating_hours=6000, load_factor=0.5):
    """
    Calculate economic analysis factors including Loss Capitalization, TOC and Life Cycle Cost (LCC).
    """
    try:
        P0_val = float(P0) if P0 != "—" and P0 is not None else 0
        Pk_val = float(Pk) if Pk != "—" and Pk is not None else 0
        total_price = float(total_purchase_price) if total_purchase_price != "—" and total_purchase_price is not None else 0
        energy_price = float(energy_price_kwh) if energy_price_kwh else 0.10
        r = float(discount_rate) if discount_rate else 0.08
        n = float(transformer_life_years) if transformer_life_years else 25
        hours = float(operating_hours) if operating_hours else 6000
        lf = float(load_factor) if load_factor else 0.5
    except (TypeError, ValueError):
        return {}

    # 1. Capital Recovery Factor (CRF)
    CRF = (r * ((1.0 + r) ** n)) / (((1.0 + r) ** n) - 1.0) if r > 0 and n > 0 else (1.0 / n if n > 0 else 0.08)

    # 2 & 3. Calculated A and B factors (USD/W)
    A_factor_calc = (energy_price * 8760.0 * CRF) / 1000.0
    B_factor_calc = (energy_price * (lf ** 2) * hours * CRF) / 1000.0

    # 4. Loss capitalization cost
    A_used = float(A_factor) if A_factor is not None and A_factor != "—" else (A_factor_calc if A_factor_calc > 0 else 8.0)
    B_used = float(B_factor) if B_factor is not None and B_factor != "—" else (B_factor_calc if B_factor_calc > 0 else 2.0)

    loss_cost_usd = (A_used * P0_val) + (B_used * Pk_val)

    # 5. Total Cost of Ownership (TOC)
    toc_usd = total_price + loss_cost_usd

    # 6. Annual operating loss cost
    annual_operating_cost_usd = ((P0_val * 8760.0 + Pk_val * (lf ** 2) * hours) / 1000.0) * energy_price

    # 7. Life Cycle Cost (LCC)
    lcc_usd = total_price + (annual_operating_cost_usd / CRF if CRF > 0 else 0)

    return {
        "CRF": _r(CRF, 4),
        "A_factor_calc": _r(A_factor_calc, 2),
        "B_factor_calc": _r(B_factor_calc, 2),
        "A_factor_used": _r(A_used, 2),
        "B_factor_used": _r(B_used, 2),
        "loss_cost_usd": _r(loss_cost_usd, 2),
        "purchase_price_usd": _r(total_price, 2),
        "toc_usd": _r(toc_usd, 2),
        "annual_operating_cost_usd": _r(annual_operating_cost_usd, 2),
        "lcc_usd": _r(lcc_usd, 2)
    }
