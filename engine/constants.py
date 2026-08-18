"""Material constants, lookup tables, and physical properties for transformer calculations."""

# Conductor properties
CONDUCTOR = {
    'Cu': {
        'resistivity_20': 1.724e-8,    # Ω·m at 20°C
        'temp_coeff': 0.00393,          # 1/°C
        'density': 8900,                # kg/m³
        'J_default_hv': 2.0,            # A/mm² (HV winding current density)
        'J_default_lv': 2.3,            # A/mm² (LV foil/strip current density)
        'J_default': 2.15,
    },
    'Al': {
        'resistivity_20': 2.826e-8,
        'temp_coeff': 0.00403,
        'density': 2700,
        'J_default_hv': 1.2,
        'J_default_lv': 1.4,
        'J_default': 1.3,
    }
}

# Core material properties
CORE_MATERIAL = {
    'M3': {
        'name': 'Hi-B Silisli Sac',
        'Bm_typical': 1.70,       # Tesla
        'Bm_max': 1.75,
        'specific_loss_1_7T': 0.85,  # W/kg at 1.7T, 50Hz
        'stacking_factor': 0.97,
        'build_factor': 1.15,
        'density': 7650,          # kg/m³
    },
    'M4': {
        'name': 'M4 Silisli Sac (Standart)',
        'Bm_typical': 1.65,
        'Bm_max': 1.72,
        'specific_loss_1_7T': 1.00,
        'stacking_factor': 0.96,
        'build_factor': 1.20,
        'density': 7650,
    },
    'M5': {
        'name': 'M5 Silisli Sac (Yüksek Kayıp)',
        'Bm_typical': 1.60,
        'Bm_max': 1.70,
        'specific_loss_1_7T': 1.30,
        'stacking_factor': 0.95,
        'build_factor': 1.25,
        'density': 7650,
    },
    'Amorf': {
        'name': 'Amorf Metal (Ultra Düşük Kayıp)',
        'Bm_typical': 1.35,
        'Bm_max': 1.40,
        'specific_loss_1_7T': 0.20,
        'stacking_factor': 0.82,
        'build_factor': 1.15,
        'density': 7180,
    }
}

# Oil properties
OIL_PROPERTIES = {
    'mineral': {'name': 'Mineral Yağ', 'density': 0.88, 'beta': 0.00075, 'specific_heat': 1.88},
    'natural_ester': {'name': 'Doğal Ester', 'density': 0.915, 'beta': 0.00074, 'specific_heat': 2.00},
    'silicone': {'name': 'Silikon Yağ', 'density': 0.96, 'beta': 0.00104, 'specific_heat': 1.50},
    'synthetic_ester': {'name': 'Sentetik Ester', 'density': 0.97, 'beta': 0.00075, 'specific_heat': 1.95}
}

# BIL (Basic Insulation Level) lookup table - IEC 60076-3
# Key: max rated voltage (kV), Value: (BIL kVp, AC test kV rms, test duration minutes)
BIL_TABLE = [
    (0.6,    None,   3,    1),
    (1.1,    None,   6,    1),
    (3.6,    20,     10,   1),
    (7.2,    40,     20,   1),
    (12,     60,     28,   1),
    (17.5,   75,     38,   1),
    (24,     95,     50,   1),
    (36,     170,    70,   1),
    (52,     250,    95,   1),
    (72.5,   325,    140,  1),
    (100,    450,    185,  1),
    (145,    550,    230,  1),
    (170,    650,    275,  1),
    (245,    850,    360,  1),
]

# Cooling method properties
COOLING_METHODS = {
    'ONAN': {'name': 'Doğal Yağ / Doğal Hava', 'q_specific': 400, 'oil_exponent': 0.8, 'winding_exponent': 0.8, 'max_power_MVA': 30},
    'ONAF': {'name': 'Doğal Yağ / Zorlanmış Hava', 'q_specific': 600, 'oil_exponent': 0.9, 'winding_exponent': 0.8, 'max_power_MVA': 60},
    'OFAF': {'name': 'Zorlanmış Yağ / Zorlanmış Hava', 'q_specific': 800, 'oil_exponent': 1.0, 'winding_exponent': 0.8, 'max_power_MVA': 200},
    'ODAF': {'name': 'Yönlendirilmiş Yağ / Zorlanmış Hava', 'q_specific': 1000, 'oil_exponent': 1.0, 'winding_exponent': 1.0, 'max_power_MVA': 500},
}

# Stepping factor for core cross-section (number of steps -> factor)
CORE_STEPPING = {
    3: 0.60,
    5: 0.70,
    7: 0.75,
    9: 0.78,
    11: 0.80,
}

# Short circuit asymmetry factor (X/R ratio -> K_asymmetry), from IEC 60076-5
ASYMMETRY_FACTORS = [
    (1, 1.51), (2, 1.62), (3, 1.76), (4, 1.85), (5, 1.90),
    (6, 1.95), (8, 2.03), (10, 2.10), (14, 2.20), (20, 2.30),
    (30, 2.40), (50, 2.50), (100, 2.55),
]

# Turkey grid CO2 emission factor
CO2_EMISSION_FACTOR = 0.47  # kg CO2 / kWh (Turkey average)

# IEC 60076-2 thermal limits
THERMAL_LIMITS = {
    'top_oil_rise_65K': 65,     # °C above ambient
    'hot_spot_78K': 78,         # °C above ambient
    'ambient_standard': 20,     # °C (IEC weighted annual average)
    'ambient_max': 40,          # °C
    'hot_spot_absolute_max': 98, # °C (for 65K rise class)
}

# Standard Three-Phase Transformer Vector Groups (IEC 60076-1)
VECTOR_GROUPS = {
    'Dyn11': {
        'code': 'Dyn11',
        'name': 'Dyn11 (Üçgen / Nötrlü Yıldız - 330°)',
        'primary_conn': 'D',
        'secondary_conn': 'yn',
        'phase_displacement_deg': 330,
        'clock': 11,
        'description': 'Standart Dağıtım Transformatörü (En Yaygın Şebeke Grubu)'
    },
    'Dyn1': {
        'code': 'Dyn1',
        'name': 'Dyn1 (Üçgen / Nötrlü Yıldız - 30°)',
        'primary_conn': 'D',
        'secondary_conn': 'yn',
        'phase_displacement_deg': 30,
        'clock': 1,
        'description': 'Üçgen / Yıldız (30° Faz Gecikmeli)'
    },
    'Yyn0': {
        'code': 'Yyn0',
        'name': 'Yyn0 (Yıldız / Nötrlü Yıldız - 0°)',
        'primary_conn': 'Y',
        'secondary_conn': 'yn',
        'phase_displacement_deg': 0,
        'clock': 0,
        'description': 'Yıldız / Yıldız Sıfır Faz Kayması'
    },
    'YNyn0': {
        'code': 'YNyn0',
        'name': 'YNyn0 (Nötrlü Yıldız / Nötrlü Yıldız - 0°)',
        'primary_conn': 'YN',
        'secondary_conn': 'yn',
        'phase_displacement_deg': 0,
        'clock': 0,
        'description': 'Çift Nötrlü İletim & Dağıtım Transformatörü'
    },
    'Yd11': {
        'code': 'Yd11',
        'name': 'Yd11 (Yıldız / Üçgen - 330°)',
        'primary_conn': 'Y',
        'secondary_conn': 'd',
        'phase_displacement_deg': 330,
        'clock': 11,
        'description': 'Santral Step-Up / Yükseltici Transformatör'
    },
    'Yd1': {
        'code': 'Yd1',
        'name': 'Yd1 (Yıldız / Üçgen - 30°)',
        'primary_conn': 'Y',
        'secondary_conn': 'd',
        'phase_displacement_deg': 30,
        'clock': 1,
        'description': 'Yıldız / Üçgen (30° Faz Gecikmeli)'
    },
    'Dd0': {
        'code': 'Dd0',
        'name': 'Dd0 (Üçgen / Üçgen - 0°)',
        'primary_conn': 'D',
        'secondary_conn': 'd',
        'phase_displacement_deg': 0,
        'clock': 0,
        'description': 'Üçgen / Üçgen Endüstriyel Transformatör'
    }
}

# Transformer Core & Window Geometric Proportions by Power Range (Directive 4)
CORE_GEOMETRY_RATIOS = [
    {'min_kVA': 25, 'max_kVA': 100, 'hw_d_range': (2.2, 2.5), 'a_d_range': (1.8, 2.0)},
    {'min_kVA': 100, 'max_kVA': 630, 'hw_d_range': (2.5, 2.8), 'a_d_range': (2.0, 2.2)},
    {'min_kVA': 630, 'max_kVA': 2500, 'hw_d_range': (2.8, 3.2), 'a_d_range': (2.2, 2.4)},
    {'min_kVA': 2500, 'max_kVA': 50000, 'hw_d_range': (3.2, 3.6), 'a_d_range': (2.3, 2.5)},
]

def get_core_geometry_ratios(S_kVA):
    """
    Interpolates window height ratio (Hw/d) and limb center distance ratio (A/d)
    based on transformer power rating (kVA).
    """
    try:
        s = float(S_kVA) if S_kVA is not None and S_kVA != "—" else 50.0
    except:
        s = 50.0

    if s <= 25.0:
        return 2.20, 1.80
    elif s <= 100.0:
        t = (s - 25.0) / (100.0 - 25.0)
        hw_d = 2.20 + t * (2.50 - 2.20)
        a_d = 1.80 + t * (2.00 - 1.80)
        return hw_d, a_d
    elif s <= 630.0:
        t = (s - 100.0) / (630.0 - 100.0)
        hw_d = 2.50 + t * (2.80 - 2.50)
        a_d = 2.00 + t * (2.20 - 2.00)
        return hw_d, a_d
    elif s <= 2500.0:
        t = (s - 630.0) / (2500.0 - 630.0)
        hw_d = 2.80 + t * (3.20 - 2.80)
        a_d = 2.20 + t * (2.40 - 2.20)
        return hw_d, a_d
    else:
        t = min(1.0, (s - 2500.0) / (50000.0 - 2500.0))
        hw_d = 3.20 + t * (3.60 - 3.20)
        a_d = 2.30 + t * (2.50 - 2.30)
        return hw_d, a_d

