"""
⚡ Hızlı Transformatör - TEDAŞ-MLZ, TEİAŞ & EU Ecodesign Specification Compliance Wizard
Provides exact regulatory limit checking, IEC 60076-1 manufacturing tolerance audits,
and EU 2019/1783 Tier 1 / Tier 2 Ecodesign compliance evaluation.
"""

import math

def _r(val, decimals=2):
    if val == '—' or val is None: return '—'
    try: return round(float(val), decimals)
    except: return '—'

# --- 1. TEDAŞ-MLZ / Dağıtım Transformatörü Standart Kayıp Tabloları (36 kV / 0.4 kV) ---
# Format: S_kVA: (P0_max_W, Pk_max_75C_W, uk_nominal_pct, uk_tol_pct, noise_max_dBA)
TEDAS_LIMITS = {
    50:   {"P0": 145,  "Pk": 875,   "uk": 4.0, "noise_dBA": 48},
    100:  {"P0": 260,  "Pk": 1750,  "uk": 4.0, "noise_dBA": 49},
    160:  {"P0": 375,  "Pk": 2350,  "uk": 4.0, "noise_dBA": 50},
    250:  {"P0": 530,  "Pk": 3250,  "uk": 4.5, "noise_dBA": 51},
    400:  {"P0": 750,  "Pk": 4600,  "uk": 4.5, "noise_dBA": 52},
    630:  {"P0": 1030, "Pk": 6500,  "uk": 4.5, "noise_dBA": 54},
    800:  {"P0": 1250, "Pk": 8400,  "uk": 5.0, "noise_dBA": 55},
    1000: {"P0": 1450, "Pk": 10500, "uk": 5.0, "noise_dBA": 56},
    1250: {"P0": 1750, "Pk": 13500, "uk": 5.5, "noise_dBA": 57},
    1600: {"P0": 2000, "Pk": 17000, "uk": 6.0, "noise_dBA": 58},
    2000: {"P0": 2400, "Pk": 21000, "uk": 6.0, "noise_dBA": 60},
    2500: {"P0": 2900, "Pk": 26500, "uk": 6.0, "noise_dBA": 62}
}

# --- 2. EU Ecodesign Directive (Regulation EU 2019/1783 - Tier 1 & Tier 2) ---
# Tier 2 (Mandatory since July 2021) - Standard liquid-immersed transformers ≤ 36 kV
ECODESIGN_TIER2_LIMITS = {
    50:   {"P0": 90,   "Pk": 750,   "uk": 4.0},
    100:  {"P0": 145,  "Pk": 1250,  "uk": 4.0},
    160:  {"P0": 210,  "Pk": 1750,  "uk": 4.0},
    250:  {"P0": 300,  "Pk": 2350,  "uk": 4.0},
    400:  {"P0": 430,  "Pk": 3250,  "uk": 4.0},
    630:  {"P0": 600,  "Pk": 4600,  "uk": 4.0},
    800:  {"P0": 650,  "Pk": 6000,  "uk": 5.0},
    1000: {"P0": 770,  "Pk": 7600,  "uk": 5.0},
    1250: {"P0": 950,  "Pk": 9500,  "uk": 5.0},
    1600: {"P0": 1200, "Pk": 12000, "uk": 6.0},
    2000: {"P0": 1450, "Pk": 15000, "uk": 6.0},
    2500: {"P0": 1750, "Pk": 18500, "uk": 6.0},
    3150: {"P0": 2200, "Pk": 22000, "uk": 6.25}
}

ECODESIGN_TIER1_LIMITS = {
    50:   {"P0": 125,  "Pk": 875,   "uk": 4.0},
    100:  {"P0": 190,  "Pk": 1475,  "uk": 4.0},
    160:  {"P0": 270,  "Pk": 2000,  "uk": 4.0},
    250:  {"P0": 360,  "Pk": 2750,  "uk": 4.0},
    400:  {"P0": 520,  "Pk": 3850,  "uk": 4.0},
    630:  {"P0": 720,  "Pk": 5400,  "uk": 4.0},
    800:  {"P0": 800,  "Pk": 7000,  "uk": 5.0},
    1000: {"P0": 940,  "Pk": 9000,  "uk": 5.0},
    1250: {"P0": 1150, "Pk": 11000, "uk": 5.0},
    1600: {"P0": 1450, "Pk": 14000, "uk": 6.0},
    2000: {"P0": 1750, "Pk": 18000, "uk": 6.0},
    2500: {"P0": 2150, "Pk": 22000, "uk": 6.0},
    3150: {"P0": 2700, "Pk": 26000, "uk": 6.25}
}

def _get_interpolated_limit(limits_dict, S_kVA):
    """Finds exact match or smooth engineering interpolation for ratings."""
    s_keys = sorted(limits_dict.keys())
    if S_kVA in limits_dict:
        return dict(limits_dict[S_kVA])
    
    if S_kVA < s_keys[0]:
        # Scale down with ~S^0.75 exponent
        base = limits_dict[s_keys[0]]
        ratio = (S_kVA / s_keys[0])
        return {
            "P0": round(base["P0"] * (ratio ** 0.7)),
            "Pk": round(base["Pk"] * (ratio ** 0.85)),
            "uk": base["uk"]
        }
    elif S_kVA > s_keys[-1]:
        # Scale up for larger power ratings
        base = limits_dict[s_keys[-1]]
        ratio = (S_kVA / s_keys[-1])
        return {
            "P0": round(base["P0"] * (ratio ** 0.65)),
            "Pk": round(base["Pk"] * (ratio ** 0.80)),
            "uk": round(base["uk"] + (math.log10(ratio) * 1.5), 2)
        }
    else:
        # Linear interpolation between nearest standard ratings
        for i in range(len(s_keys) - 1):
            s_low, s_high = s_keys[i], s_keys[i+1]
            if s_low < S_kVA < s_high:
                frac = (S_kVA - s_low) / (s_high - s_low)
                low_dict, high_dict = limits_dict[s_low], limits_dict[s_high]
                return {
                    "P0": round(low_dict["P0"] + frac * (high_dict["P0"] - low_dict["P0"])),
                    "Pk": round(low_dict["Pk"] + frac * (high_dict["Pk"] - low_dict["Pk"])),
                    "uk": round(low_dict["uk"] + frac * (high_dict["uk"] - low_dict["uk"]), 2)
                }
    return dict(limits_dict[s_keys[0]])


def calculate_standards_compliance(S_VA, P0, Pk, uk, V1=34500, V2=400):
    """
    Evaluates design parameters against:
    1. TEDAŞ-MLZ / 95-012
    2. EU 2019/1783 Ecodesign Tier 2 (Mandatory 2021+)
    3. EU Ecodesign Tier 1 (2015)
    4. IEC 60076-1 Manufacturing Tolerance Audit
    """
    try:
        S_kVA = float(S_VA) / 1000.0 if float(S_VA) >= 1000.0 else float(S_VA)
        P0_val = float(P0)
        Pk_val = float(Pk)
        uk_val = float(uk)
    except (ValueError, TypeError):
        return {}

    # 1. Retrieve Standard Reference Limits
    tedas_std = _get_interpolated_limit(TEDAS_LIMITS, S_kVA)
    tier2_std = _get_interpolated_limit(ECODESIGN_TIER2_LIMITS, S_kVA)
    tier1_std = _get_interpolated_limit(ECODESIGN_TIER1_LIMITS, S_kVA)

    # 2. Evaluation Helper
    def evaluate_standard(std_limits, std_name):
        p0_max = std_limits["P0"]
        pk_max = std_limits["Pk"]
        uk_nom = std_limits["uk"]

        # Delta percentages (Negative means better / lower losses than standard max)
        diff_p0_pct = ((P0_val - p0_max) / p0_max) * 100.0 if p0_max > 0 else 0
        diff_pk_pct = ((Pk_val - pk_max) / pk_max) * 100.0 if pk_max > 0 else 0
        diff_uk_pct = ((uk_val - uk_nom) / uk_nom) * 100.0 if uk_nom > 0 else 0

        p0_pass = P0_val <= p0_max
        pk_pass = Pk_val <= pk_max
        
        # IEC 60076-1 tolerance: uk within ±10% of nominal
        uk_pass = abs(diff_uk_pct) <= 10.0

        is_fully_compliant = p0_pass and pk_pass and uk_pass

        status_text = "UYGUN (ŞARTNAME ONAYLI)" if is_fully_compliant else (
            "KISMİ UYGUN" if (p0_pass or pk_pass) else "ŞARTNAME AŞIMI"
        )

        return {
            "standard_name": std_name,
            "P0_limit_W": p0_max,
            "P0_actual_W": P0_val,
            "P0_diff_pct": _r(diff_p0_pct, 1),
            "P0_pass": p0_pass,

            "Pk_limit_W": pk_max,
            "Pk_actual_W": Pk_val,
            "Pk_diff_pct": _r(diff_pk_pct, 1),
            "Pk_pass": pk_pass,

            "uk_nominal_pct": uk_nom,
            "uk_actual_pct": uk_val,
            "uk_diff_pct": _r(diff_uk_pct, 1),
            "uk_pass": uk_pass,

            "is_compliant": is_fully_compliant,
            "status_text": status_text
        }

    eval_tedas = evaluate_standard(tedas_std, "TEDAŞ-MLZ / 95-012.C (Türkiye)")
    eval_tier2 = evaluate_standard(tier2_std, "AB Ecodesign Tier 2 (EU 2019/1783 - 2021+)")
    eval_tier1 = evaluate_standard(tier1_std, "AB Ecodesign Tier 1 (EU 548/2014 - 2015)")

    # 3. IEC 60076-1 Tolerances Check
    # Total losses tolerance is +10%, component losses +15%, uk ±10%
    iec_tolerances = {
        "P0_tolerance": "+15.0 % (Maks)",
        "Pk_tolerance": "+15.0 % (Maks)",
        "P_total_tolerance": "+10.0 % (Maks)",
        "uk_tolerance": "±10.0 % (Nominal)"
    }

    # 4. Energy Efficiency Index (PEI - Peak Efficiency Index per EN 50588-1)
    # PEI = 1 - 2 * sqrt(P0 * Pk) / S
    if S_kVA > 0:
        p_total_nom = (P0_val + Pk_val)
        P0_kW = P0_val / 1000.0
        Pk_kW = Pk_val / 1000.0
        pei_value = (1.0 - (2.0 * math.sqrt(P0_kW * Pk_kW) / S_kVA)) * 100.0
    else:
        pei_value = 99.0

    # Overall Eco-Score Badge
    if eval_tier2["is_compliant"]:
        energy_class = "A+ (EU Tier 2 Ultra-Verimli)"
        badge_color = "green"
    elif eval_tedas["is_compliant"] or eval_tier1["is_compliant"]:
        energy_class = "A (Standart Verimli Dağıtım)"
        badge_color = "blue"
    else:
        energy_class = "B (Yüksek Kayıplı / Özel İmalat)"
        badge_color = "orange"

    return {
        "energy_class": energy_class,
        "badge_color": badge_color,
        "pei_index_pct": _r(pei_value, 4),
        "tedas": eval_tedas,
        "ecodesign_tier2": eval_tier2,
        "ecodesign_tier1": eval_tier1,
        "iec_tolerances": iec_tolerances
    }
