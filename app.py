from flask import Flask, render_template, request, jsonify
import math
import requests
import re
import pymupdf  # fitz

app = Flask(__name__)

def get_metal_prices():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    prices = {"copper_usd_kg": 9.50, "aluminum_usd_kg": 2.50, "usd_try": 33.50}
    sources = {"copper": "", "aluminum": "", "usd_try": ""}
    
    try:
        url_try = "https://query1.finance.yahoo.com/v8/finance/chart/TRY=X"
        response_try = requests.get(url_try, headers=headers, timeout=5)
        if response_try.status_code == 200:
            data_try = response_try.json()
            prices["usd_try"] = data_try['chart']['result'][0]['meta']['regularMarketPrice']
            sources["usd_try"] = url_try
    except Exception:
        pass
    
    try:
        url_cu = "https://query1.finance.yahoo.com/v8/finance/chart/HG=F"
        response_cu = requests.get(url_cu, headers=headers, timeout=5)
        if response_cu.status_code == 200:
            data_cu = response_cu.json()
            price_lb = data_cu['chart']['result'][0]['meta']['regularMarketPrice']
            prices["copper_usd_kg"] = price_lb / 0.453592
            sources["copper"] = url_cu
    except Exception:
        pass
        
    try:
        url_al = "https://query1.finance.yahoo.com/v8/finance/chart/ALI=F"
        response_al = requests.get(url_al, headers=headers, timeout=5)
        if response_al.status_code == 200:
            data_al = response_al.json()
            price_ton = data_al['chart']['result'][0]['meta']['regularMarketPrice']
            prices["aluminum_usd_kg"] = price_ton / 1000.0
            sources["aluminum"] = url_al
    except Exception:
        pass
        
    return prices, sources

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prices', methods=['GET'])
def get_prices():
    prices, sources = get_metal_prices()
    return jsonify({
        "success": True,
        "prices": {
            "copper": round(prices.get("copper_usd_kg", 0), 2),
            "aluminum": round(prices.get("aluminum_usd_kg", 0), 2),
            "usd_try": round(prices.get("usd_try", 33.50), 2)
        },
        "sources": sources
    })

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        
        def safe_float(v):
            if v is None or v == '': return None
            try: return float(v)
            except: return None

        S = safe_float(data.get('S'))
        V1 = safe_float(data.get('V1'))
        V2 = safe_float(data.get('V2'))
        uk = safe_float(data.get('uk'))
        P0 = safe_float(data.get('P0'))
        Pk = safe_float(data.get('Pk'))
        
        oil_type = data.get('oil_type', 'mineral')
        k_constant = float(data.get('k_constant', 0.45))
        delta_T = float(data.get('delta_T', 60))
        material_hv = data.get('material_hv', 'Cu')
        material_lv = data.get('material_lv', 'Cu')
        core_material = data.get('core_material', 'M4')
        A_factor = safe_float(data.get('A_factor')) or 8.0
        B_factor = safe_float(data.get('B_factor')) or 2.0
        
        if None in [S, V1, V2]:
            S_kVA, Et, N1, N2, I1, I2, a = ("—",) * 7
        else:
            S_kVA = S / 1000.0
            Et = k_constant * math.sqrt(S_kVA)
            if Et <= 0: Et = 1
            N1 = round(V1 / Et)
            N2 = round(V2 / Et)
            
            phase = int(data.get('phase', 3))
            if phase == 3:
                I1 = S / (math.sqrt(3) * V1)
                I2 = S / (math.sqrt(3) * V2)
            else:
                I1 = S / V1
                I2 = S / V2
                
            a = V1 / V2

        if None in [S, V1, I1, uk, Pk] or I1 == "—":
            Vk, Zk, Rk, Xk = ("—",) * 4
        else:
            Vk = V1 * (uk / 100.0)
            Zk = Vk / I1
            Rk = Pk / (I1**2)
            if Zk**2 >= Rk**2:
                Xk = math.sqrt(Zk**2 - Rk**2)
            else:
                Xk = 0
                
        f = float(data.get('frequency', 50.0))
        Lk = Xk / (2 * math.pi * f) if Xk != "—" else "—"
        
        if None in [S, P0, Pk]:
            efficiency = "—"
        else:
            efficiency = (S / (S + P0 + Pk)) * 100.0
        
        # Current Density (J) A/mm2 assumption based on material
        J_hv = 3.0 if material_hv == 'Cu' else 1.5
        J_lv = 3.0 if material_lv == 'Cu' else 1.5
        
        # Cross Sectional Areas (mm2)
        A1_mm2 = I1 / J_hv if I1 != "—" else "—"
        A2_mm2 = I2 / J_lv if I2 != "—" else "—"
        
        def r2(val):
            if val == "—" or val is None: return "—"
            try: return round(float(val), 2)
            except: return "—"
            
        def r4(val):
            if val == "—" or val is None: return "—"
            try: return round(float(val), 4)
            except: return "—"

        electrical = {
            "I1": r2(I1),
            "I2": r2(I2),
            "a": r4(a),
            "Vk": r2(Vk),
            "Zk": r4(Zk),
            "Rk": r4(Rk) if 'Rk' in locals() else "—",
            "Xk": r4(Xk),
            "Lk_mH": r2(Lk * 1000) if Lk != "—" else "—",
            "efficiency": r2(efficiency),
            "Et": r4(Et),
            "N1": N1,
            "N2": N2,
            "A1": r2(A1_mm2),
            "A2": r2(A2_mm2)
        }
        
        if S is not None and S_kVA != "—":
            prices, sources = get_metal_prices()
            weight_hv = (S_kVA * 1.2 / 2) if material_hv == 'Cu' else (S_kVA * 0.8 / 2)
            weight_lv = (S_kVA * 1.2 / 2) if material_lv == 'Cu' else (S_kVA * 0.8 / 2)
            cost_hv = weight_hv * (prices["copper_usd_kg"] if material_hv == 'Cu' else prices["aluminum_usd_kg"])
            cost_lv = weight_lv * (prices["copper_usd_kg"] if material_lv == 'Cu' else prices["aluminum_usd_kg"])
            total_conductor_weight = weight_hv + weight_lv
            # Core physics based on material
            base_core_weight = (S_kVA ** 0.75) * 8.5
            if core_material == 'M5':
                core_weight = base_core_weight * 1.05
                core_label = "M5 Silisli Sac (Yüksek Kayıp)"
            elif core_material == 'Amorf':
                core_weight = base_core_weight * 0.95
                core_label = "Amorf Metal (Ultra Düşük Kayıp)"
            else: # M4
                core_weight = base_core_weight
                core_label = "M4 Silisli Sac (Standart)"
            
            tank_weight = (S_kVA ** 0.7) * 6.5
            if material_hv == 'Al' or material_lv == 'Al':
                core_weight *= 1.15
                tank_weight *= 1.10
                
            dry_weight = total_conductor_weight + core_weight + tank_weight
            oil_volume = (S_kVA ** 0.8) * 4.5
            if material_hv == 'Al' or material_lv == 'Al':
                oil_volume *= 1.15
        else:
            prices, sources = {"copper_usd_kg": 0, "aluminum_usd_kg": 0}, {}
            weight_hv, weight_lv, cost_hv, cost_lv, total_conductor_weight, dry_weight, oil_volume = ("—",)*7
            core_weight, tank_weight, core_label = "—", "—", "—"
        
        # Thermodynamic Calculations
        oil_props = {
            'mineral': {'density': 0.88, 'beta': 0.00075},
            'natural_ester': {'density': 0.915, 'beta': 0.00074},
            'silicone': {'density': 0.96, 'beta': 0.00104},
            'synthetic_ester': {'density': 0.97, 'beta': 0.00075}
        }
        props = oil_props.get(oil_type, oil_props['mineral'])
        oil_density = props['density']
        expansion_coeff = props['beta']
        
        if oil_volume != "—":
            oil_weight = oil_volume * oil_density
            expansion_volume = oil_volume * expansion_coeff * delta_T
            wet_weight = dry_weight + oil_weight
        else:
            oil_weight, expansion_volume, wet_weight = ("—",)*3
            
        if None not in [P0, Pk]:
            total_heat_loss = P0 + Pk
            cooling_area = total_heat_loss / 400.0
        else:
            total_heat_loss, cooling_area = ("—",)*2
        
        thermo = {
            "total_heat_loss": r2(total_heat_loss),
            "cooling_area_m2": r2(cooling_area),
            "expansion_volume_L": r2(expansion_volume),
            "oil_volume_L": r2(oil_volume),
            "oil_weight_kg": r2(oil_weight),
            "oil_density": r2(oil_density),
            "expansion_coeff": expansion_coeff
        }
        
        cost = {
            "prices": {
                "copper": r2(prices.get("copper_usd_kg", 0)),
                "aluminum": r2(prices.get("aluminum_usd_kg", 0))
            },
            "sources": sources,
            "weights": {
                "hv": r2(weight_hv),
                "lv": r2(weight_lv),
                "total": r2(total_conductor_weight),
                "core_weight": r2(core_weight),
                "tank_weight": r2(tank_weight),
                "dry": r2(dry_weight),
                "wet": r2(wet_weight)
            },
            "materials": {
                "hv": material_hv,
                "lv": material_lv
            },
            "total": {
                "hv": r2(cost_hv),
                "lv": r2(cost_lv),
                "total_cost": r2((cost_hv if cost_hv != "—" else 0) + (cost_lv if cost_lv != "—" else 0)) if cost_hv != "—" else "—"
            }
        }
        
        # TOC Calculation
        loss_cost = 0
        if P0 != "—" and P0 is not None and Pk != "—" and Pk is not None:
            loss_cost = (A_factor * P0) + (B_factor * Pk)
            
        total_material_cost = cost["total"]["total_cost"] if cost["total"]["total_cost"] != "—" else 0
        cw = core_weight if core_weight != "—" else 0
        tw = tank_weight if tank_weight != "—" else 0
        ow = oil_weight if oil_weight != "—" else 0
        
        purchase_price = (total_material_cost * 1.5) + (cw * 3.0) + (tw * 1.5) + (ow * 1.2)
        toc = purchase_price + loss_cost
        
        toc_analysis = {
            "loss_cost": round(loss_cost, 2),
            "toc": round(toc, 2),
            "core_label": core_label,
            "core_weight": round(core_weight, 1) if core_weight != "—" else "—"
        }

        return jsonify({
            "success": True,
            "electrical": electrical,
            "thermo": thermo,
            "cost": cost,
            "prices": {
                "copper": r2(prices.get("copper_usd_kg", 0)),
                "aluminum": r2(prices.get("aluminum_usd_kg", 0)),
                "usd_try": prices.get("usd_try", 34.00)
            },
            "sources": sources,
            "toc_analysis": toc_analysis
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/parse-pdf', methods=['POST'])
def parse_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Dosya bulunamadı'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Dosya seçilmedi'})
            
        # Read PDF from memory
        doc = pymupdf.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            
        # Parse data using regex
        data = {}
        
        # S (kVA -> VA) - matches "kVA) \n 50" or "Anma Gücü (S) \n 100 kVA"
        s_match = re.search(r'kVA\)\s*(\d+)', text)
        if not s_match:
            s_match = re.search(r'G.*?c.*?\(\S+\)\s*(\d+)', text)
        if s_match:
            data['S'] = float(s_match.group(1)) * 1000.0
            
        # V1 - matches "Primer Gerilimi \n 31500" or "Primer Gerilim \n 12.47 kV"
        v1_match = re.search(r'Primer Gerilim.*?(\d+(?:\.\d+)?)', text, re.IGNORECASE | re.DOTALL)
        if v1_match:
            val = float(v1_match.group(1))
            # Check if it was kV
            if 'kV' in text[v1_match.end():v1_match.end()+10]:
                val *= 1000.0
            elif val < 1000:
                val *= 1000.0 # Just in case it's 12.47 without kV immediately after
            data['V1'] = val
            
        # V2 - matches "Sekonder Gerilimi \n 400" or "480Y / 277 V" -> 480
        v2_match = re.search(r'Sekonder Gerilim.*?(\d+)', text, re.IGNORECASE | re.DOTALL)
        if v2_match:
            data['V2'] = float(v2_match.group(1))
            
        # uk - matches "Empedans (% \n 4.5" or "%4.5"
        uk_match = re.search(r'Empedans.*?%?\s*(\d+\.\d+|\d+)', text, re.IGNORECASE | re.DOTALL)
        if uk_match:
            data['uk'] = float(uk_match.group(1))
            
        # Frequency
        freq_match = re.search(r'Frekans.*?\)\s*(\d+)', text, re.DOTALL)
        if freq_match:
            data['frequency'] = float(freq_match.group(1))
            
        # Pk
        pk_match = re.search(r'Pk\)[\s:]*(\d+)', text)
        if not pk_match:
            pk_match = re.search(r'\(Pk\)\s*(\d+)', text, re.IGNORECASE)
        if pk_match:
            data['Pk'] = float(pk_match.group(1))
            
        # P0
        p0_match = re.search(r'P[0oO]\)[\s:]*(\d+)', text)
        if not p0_match:
            p0_match = re.search(r'\(Po\)\s*(\d+)', text, re.IGNORECASE)
        if p0_match:
            data['P0'] = float(p0_match.group(1))
            
        # Phase count
        phase_count = 1 if re.search(r'Tek Fazl', text, re.IGNORECASE) else 3
        data['phase'] = phase_count
            
        # Material
        mat_match = re.search(r'Sarg.\s*Malzemesi\s*([^\n]+)', text, re.IGNORECASE)
        if mat_match:
            mat_str = mat_match.group(1)
            if 'Bak' in mat_str or 'Cu' in mat_str:
                data['material_hv'] = 'Cu'
                data['material_lv'] = 'Cu'
            elif 'Al' in mat_str:
                data['material_hv'] = 'Al'
                data['material_lv'] = 'Al'
                
        return jsonify({'success': True, 'data': data, 'raw_text_debug': text[:500]})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
