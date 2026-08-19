from flask import Flask, render_template, request, jsonify, Response
import time
import urllib.request
import re
import pymupdf  # fitz

from engine import calculate_all
from engine.pdf_report import build_pdf_report
from engine.excel_report import build_excel_report

import threading
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'prices_cache.json')

# In-memory cache for metal and energy prices with persistence & fallback (Directive 6)
_DEFAULT_PRICES = {
    "copper_usd_kg": 9.50,
    "aluminum_usd_kg": 2.50,
    "usd_try": 34.00,
    "electricity_usd_kwh": 0.103,
    "electricity_try_kwh": 3.50
}
_DEFAULT_SOURCES = {
    "copper": "https://query1.finance.yahoo.com/v8/finance/chart/HG=F",
    "aluminum": "https://query1.finance.yahoo.com/v8/finance/chart/ALI=F",
    "usd_try": "https://query1.finance.yahoo.com/v8/finance/chart/TRY=X",
    "electricity": "https://www.epdk.gov.tr/"
}

def _http_get_json(url, headers=None, timeout=3):
    """Standart kütüphane urllib ile güvenli JSON GET isteği atar."""
    try:
        hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8', errors='ignore'))
    except Exception:
        pass
    return None

def _load_cache_from_disk():
    """Disk önbelleğinden son kaydedilen piyasa fiyatlarını yükler."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "prices": data.get("prices", _DEFAULT_PRICES),
                    "sources": data.get("sources", _DEFAULT_SOURCES),
                    "timestamp": data.get("timestamp", time.time())
                }
        except Exception:
            pass
    return {
        "prices": dict(_DEFAULT_PRICES),
        "sources": dict(_DEFAULT_SOURCES),
        "timestamp": time.time()
    }

def _save_cache_to_disk(cache_data):
    """Güncel piyasa verilerini yerel disk önbellek dosyasına kaydeder."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        pass

_PRICES_CACHE = _load_cache_from_disk()
_PRICE_LOCK = threading.Lock()
_FAILURE_COUNT = 0

def _fetch_secondary_fallback(prices, sources):
    """
    İkincil / yedek ücretsiz API üzerinden döviz kuru verilerini çeker (Directive 6).
    """
    try:
        url_sec = "https://api.frankfurter.app/latest?from=USD&to=TRY"
        data = _http_get_json(url_sec, timeout=3)
        if data:
            val = data.get('rates', {}).get('TRY')
            if val:
                prices["usd_try"] = float(val)
                sources["usd_try"] = url_sec
                if prices["usd_try"] > 0:
                    prices["electricity_usd_kwh"] = round(3.50 / prices["usd_try"], 3)
                return True
    except Exception:
        pass
    return False

def _fetch_yahoo_market_data():
    """
    Birincil ve ikincil kaynaklardan emtia ve döviz kurlarını arka planda çeker.
    3 başarısız denemeden sonra otomatik fallback moduna geçer (Directive 6).
    """
    global _FAILURE_COUNT
    
    with _PRICE_LOCK:
        prices = dict(_PRICES_CACHE["prices"])
        sources = dict(_PRICES_CACHE["sources"])

    any_success = False

    # 1. USD / TRY Kuru
    try:
        url_try = "https://query1.finance.yahoo.com/v8/finance/chart/TRY=X"
        data = _http_get_json(url_try, timeout=3)
        if data and 'chart' in data and data['chart'].get('result'):
            val = data['chart']['result'][0]['meta'].get('regularMarketPrice')
            if val:
                prices["usd_try"] = float(val)
                sources["usd_try"] = url_try
                if prices["usd_try"] > 0:
                    prices["electricity_usd_kwh"] = round(3.50 / prices["usd_try"], 3)
                any_success = True
        else:
            if _FAILURE_COUNT >= 3 and _fetch_secondary_fallback(prices, sources):
                any_success = True
    except Exception:
        if _FAILURE_COUNT >= 3 and _fetch_secondary_fallback(prices, sources):
            any_success = True

    # 2. Bakır Fiyatı (LME Copper HG=F)
    try:
        url_cu = "https://query1.finance.yahoo.com/v8/finance/chart/HG=F"
        data = _http_get_json(url_cu, timeout=3)
        if data and 'chart' in data and data['chart'].get('result'):
            val = data['chart']['result'][0]['meta'].get('regularMarketPrice')
            if val:
                prices["copper_usd_kg"] = float(val) / 0.453592
                sources["copper"] = url_cu
                any_success = True
    except Exception:
        pass

    # 3. Alüminyum Fiyatı (LME Aluminum ALI=F)
    try:
        url_al = "https://query1.finance.yahoo.com/v8/finance/chart/ALI=F"
        data = _http_get_json(url_al, timeout=3)
        if data and 'chart' in data and data['chart'].get('result'):
            val = data['chart']['result'][0]['meta'].get('regularMarketPrice')
            if val:
                prices["aluminum_usd_kg"] = float(val) / 1000.0
                sources["aluminum"] = url_al
                any_success = True
    except Exception:
        pass

    now_ts = time.time()
    if any_success:
        _FAILURE_COUNT = 0
        with _PRICE_LOCK:
            _PRICES_CACHE["prices"] = prices
            _PRICES_CACHE["sources"] = sources
            _PRICES_CACHE["timestamp"] = now_ts
        _save_cache_to_disk(_PRICES_CACHE)
    else:
        _FAILURE_COUNT += 1

def _background_price_worker():
    """Background daemon thread that periodically refreshes live market quotes."""
    while True:
        try:
            _fetch_yahoo_market_data()
        except Exception:
            pass
        time.sleep(45)  # Refresh every 45 seconds

# Start the background daemon worker on app startup
_bg_thread = threading.Thread(target=_background_price_worker, daemon=True)
_bg_thread.start()

def get_metal_prices(force=False):
    """
    Returns live prices in 0.0001 seconds from in-memory cache.
    Never blocks calculations with external network I/O.
    """
    if force:
        threading.Thread(target=_fetch_yahoo_market_data, daemon=True).start()
        
    with _PRICE_LOCK:
        return dict(_PRICES_CACHE["prices"]), dict(_PRICES_CACHE["sources"]), _PRICES_CACHE.get("timestamp", time.time())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prices', methods=['GET'])
def get_prices():
    force = request.args.get('force', 'false').lower() == 'true'
    prices, sources, ts = get_metal_prices(force=force)
    now_ts = time.time()
    is_stale = (now_ts - ts) > 600  # Older than 10 minutes
    
    last_upd_str = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    now_str = time.strftime("%H:%M:%S")

    return jsonify({
        "success": True,
        "prices": {
            "copper": round(prices.get("copper_usd_kg", 9.50), 2),
            "aluminum": round(prices.get("aluminum_usd_kg", 2.50), 2),
            "usd_try": round(prices.get("usd_try", 34.00), 2),
            "electricity": round(prices.get("electricity_usd_kwh", 0.103), 3),
            "electricity_try": round(prices.get("electricity_try_kwh", 3.50), 2)
        },
        "time": now_str,
        "last_updated": ts,
        "last_updated_str": last_upd_str,
        "is_stale": is_stale,
        "sources": sources
    })

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json or {}
        prices, sources, _ = get_metal_prices()
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
            
        prices, sources, _ = get_metal_prices()
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

@app.route('/api/download-excel', methods=['POST', 'GET'])
def download_excel():
    try:
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
            
        prices, sources, _ = get_metal_prices()
        calc_result = calculate_all(data, metal_prices=prices, metal_sources=sources)
        excel_buf = build_excel_report(data, calc_result)
        
        return Response(
            excel_buf.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': 'attachment; filename="Transformator_Muhendislik_Raporu.xlsx"',
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
