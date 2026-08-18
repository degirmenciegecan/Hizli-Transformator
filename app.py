from flask import Flask, render_template, request, jsonify, Response
import time
import requests
import re
import pymupdf  # fitz

from engine import calculate_all
from engine.pdf_report import build_pdf_report

app = Flask(__name__)

# In-memory cache for metal prices to optimize response latency
_PRICES_CACHE = {
    "prices": {"copper_usd_kg": 9.50, "aluminum_usd_kg": 2.50, "usd_try": 34.00},
    "sources": {"copper": "", "aluminum": "", "usd_try": ""},
    "timestamp": 0
}
CACHE_TTL_SECONDS = 30  # 30 seconds fresh cache

def get_metal_prices(force=False):
    """
    Retrieves live commodity prices (Cu, Al) and USD/TRY exchange rate from Yahoo Finance.
    Results are cached in-memory for 30 seconds for live market responsiveness.
    """
    now = time.time()
    if not force and _PRICES_CACHE["timestamp"] > 0 and (now - _PRICES_CACHE["timestamp"]) < CACHE_TTL_SECONDS:
        return _PRICES_CACHE["prices"], _PRICES_CACHE["sources"]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    prices = {"copper_usd_kg": 9.50, "aluminum_usd_kg": 2.50, "usd_try": 34.00}
    sources = {"copper": "", "aluminum": "", "usd_try": ""}

    try:
        url_try = "https://query1.finance.yahoo.com/v8/finance/chart/TRY=X"
        response_try = requests.get(url_try, headers=headers, timeout=4)
        if response_try.status_code == 200:
            data_try = response_try.json()
            val = data_try['chart']['result'][0]['meta']['regularMarketPrice']
            if val:
                prices["usd_try"] = float(val)
                sources["usd_try"] = url_try
    except Exception:
        pass

    try:
        url_cu = "https://query1.finance.yahoo.com/v8/finance/chart/HG=F"
        response_cu = requests.get(url_cu, headers=headers, timeout=4)
        if response_cu.status_code == 200:
            data_cu = response_cu.json()
            price_lb = data_cu['chart']['result'][0]['meta']['regularMarketPrice']
            if price_lb:
                prices["copper_usd_kg"] = float(price_lb) / 0.453592
                sources["copper"] = url_cu
    except Exception:
        pass

    try:
        url_al = "https://query1.finance.yahoo.com/v8/finance/chart/ALI=F"
        response_al = requests.get(url_al, headers=headers, timeout=4)
        if response_al.status_code == 200:
            data_al = response_al.json()
            price_ton = data_al['chart']['result'][0]['meta']['regularMarketPrice']
            if price_ton:
                prices["aluminum_usd_kg"] = float(price_ton) / 1000.0
                sources["aluminum"] = url_al
    except Exception:
        pass

    _PRICES_CACHE["prices"] = prices
    _PRICES_CACHE["sources"] = sources
    _PRICES_CACHE["timestamp"] = now
    return prices, sources

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prices', methods=['GET'])
def get_prices():
    force = request.args.get('force', 'false').lower() == 'true'
    prices, sources = get_metal_prices(force=force)
    now_str = time.strftime("%H:%M:%S")
    return jsonify({
        "success": True,
        "prices": {
            "copper": round(prices.get("copper_usd_kg", 9.50), 2),
            "aluminum": round(prices.get("aluminum_usd_kg", 2.50), 2),
            "usd_try": round(prices.get("usd_try", 34.00), 2)
        },
        "time": now_str,
        "sources": sources
    })

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json or {}
        prices, sources = get_metal_prices()
        result = calculate_all(data, metal_prices=prices, metal_sources=sources)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/download-pdf', methods=['POST', 'GET'])
def download_pdf():
    try:
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
            
        prices, sources = get_metal_prices()
        calc_result = calculate_all(data, metal_prices=prices, metal_sources=sources)
        pdf_bytes = build_pdf_report(calc_result, data)
        
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': 'inline; filename="Transformator_Muhendislik_Raporu.pdf"',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        )
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
            
        doc = pymupdf.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            
        data = {}
        
        # S (kVA -> VA)
        s_match = re.search(r'kVA\)\s*(\d+)', text)
        if not s_match:
            s_match = re.search(r'G.*?c.*?\(\S+\)\s*(\d+)', text)
        if s_match:
            data['S'] = float(s_match.group(1)) * 1000.0
            
        # V1
        v1_match = re.search(r'Primer Gerilim.*?(\d+(?:\.\d+)?)', text, re.IGNORECASE | re.DOTALL)
        if v1_match:
            val = float(v1_match.group(1))
            if 'kV' in text[v1_match.end():v1_match.end()+10]:
                val *= 1000.0
            elif val < 1000:
                val *= 1000.0
            data['V1'] = val
            
        # V2
        v2_match = re.search(r'Sekonder Gerilim.*?(\d+)', text, re.IGNORECASE | re.DOTALL)
        if v2_match:
            data['V2'] = float(v2_match.group(1))
            
        # uk
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
