// ⚡ Hızlı Transformatör - Frontend Controller & Multi-Module Categorized UI Binder
let latestData = null;
let usdTryRate = 34.00;

function updateText(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = (value !== undefined && value !== null && value !== '') ? value : '—';
    }
}

function getVal(id, fallback = 0) {
    const el = document.getElementById(id);
    if (!el || el.value === undefined || el.value === '') return fallback;
    const v = parseFloat(el.value);
    return isNaN(v) ? fallback : v;
}

function getStr(id, fallback = '') {
    const el = document.getElementById(id);
    return (el && el.value) ? el.value : fallback;
}

window.doCalculate = doCalculate;

async function doCalculate(e) {
    if (e && e.preventDefault) e.preventDefault();

    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const initialDiv = document.getElementById('initial-state');

    console.log('⚡ doCalculate tetiklendi!');

    // UI state transition
    if (initialDiv) initialDiv.classList.add('hidden');
    if (resultsDiv) resultsDiv.classList.add('hidden');
    if (loadingDiv) loadingDiv.classList.remove('hidden');

    const data = {
        S: getVal('S', 50000),
        V1: getVal('V1', 34500),
        V2: getVal('V2', 400),
        uk: getVal('uk', 4.5),
        P0: getVal('P0', 150),
        Pk: getVal('Pk', 900),
        phase: parseInt(getStr('phase', '3')),
        frequency: getVal('frequency', 50),
        material_hv: getStr('material_hv', 'Cu'),
        material_lv: getStr('material_lv', 'Cu'),
        core_material: getStr('core_material', 'M4'),
        oil_type: getStr('oil_type', 'mineral'),
        k_constant: getVal('k_constant', 0.45),
        delta_T: getVal('delta_T', 60),
        ambient_temp: getVal('ambient_temp', 30),
        cooling_method: getStr('cooling_method', 'ONAN'),
        A_factor: getVal('A_factor', 8.0),
        B_factor: getVal('B_factor', 2.0)
    };

    console.log('Gönderilen Parametreler:', data);

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const res = await response.json();
        console.log('API Yanıtı:', res);

        if (res && res.success) {
            latestData = { req: data, res: res };

            // Formatters
            const fmtUSD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
            const fmtTRY = new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

            // --- KATEGORİ 1: Elektriksel Analiz ---
            const el = res.electrical || {};
            updateText('res-I1', el.I1);
            updateText('res-I2', el.I2);
            updateText('res-a', el.a);
            updateText('res-Vk', el.Vk);
            updateText('res-Zk', el.Zk);
            updateText('res-Rk', el.Rk);
            updateText('res-Xk', el.Xk);
            updateText('res-Lk', el.Lk_mH);
            updateText('res-ur', el.ur_pct);
            updateText('res-ux', el.ux_pct);
            updateText('res-eff', el.efficiency);

            // Gerilim Regülasyonu
            const vr = res.voltage_regulation || {};
            updateText('res-vreg-08', el.voltage_reg_08 || (vr.regulation_table?.[2]?.regulation_pct));
            updateText('res-max-reg-cos', vr.max_reg_cos_phi);

            const tbodyVreg = document.getElementById('tbody-vreg');
            if (tbodyVreg && vr.regulation_table) {
                tbodyVreg.innerHTML = '';
                vr.regulation_table.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>cosφ = ${row.cos_phi.toFixed(2)}</td>
                        <td><strong>% ${row.regulation_pct}</strong></td>
                        <td>${row.V2_loaded} V</td>
                    `;
                    tbodyVreg.appendChild(tr);
                });
            }

            // Mıknatıslanma & Inrush
            const mag = res.magnetization || {};
            updateText('res-mag-ic', mag.Ic_A);
            updateText('res-mag-im', mag.Im_A);
            updateText('res-mag-i0', mag.I0_A);
            updateText('res-mag-i0pct', mag.I0_pct);
            updateText('res-mag-cos0', mag.cos_phi_0);
            updateText('res-mag-inrush', mag.inrush_peak_A);

            // --- KATEGORİ 2: İmalat & Manyetik Tasarım ---
            const cd = res.core_design || {};
            updateText('res-core-label', cd.core_label);
            updateText('res-core-bm', cd.Bm);
            updateText('res-core-ai', cd.Ai_cm2);
            updateText('res-core-ag', cd.Ag_cm2);
            updateText('res-core-dia', cd.core_diameter_mm);
            updateText('res-core-weight-detail', cd.core_weight_kg);
            updateText('res-core-p0-est', cd.P0_estimated_W);
            updateText('res-core-physt', cd.P_hysteresis_W);
            updateText('res-core-peddy', cd.P_eddy_W);
            updateText('res-core-stack', cd.stacking_factor);

            // Sargı & İmalat
            const wd = res.winding || {};
            updateText('res-et-val', el.Et);
            updateText('res-hv-turns', el.N1);
            updateText('res-lv-turns', el.N2);
            updateText('res-hv-area', el.A1);
            updateText('res-lv-area', el.A2);
            updateText('res-hv-dia', wd.d_conductor_hv_mm);
            updateText('res-lv-dia', wd.d_conductor_lv_mm);
            updateText('res-par-hv', wd.n_parallel_hv);
            updateText('res-par-lv', wd.n_parallel_lv);
            updateText('res-mlt-hv', wd.MLT_hv_mm);
            updateText('res-mlt-lv', wd.MLT_lv_mm);
            updateText('res-r75-hv', wd.R_hv_75);
            updateText('res-r75-lv', wd.R_lv_75);
            updateText('res-len-hv', wd.total_conductor_length_hv_m);
            updateText('res-len-lv', wd.total_conductor_length_lv_m);

            // Yalıtım (BIL)
            const ins = res.insulation || {};
            updateText('res-ins-um1', ins.hv_Um_kV);
            updateText('res-ins-bil1', ins.hv_BIL_kVp);
            updateText('res-ins-ac1', ins.hv_AC_test_kV);
            updateText('res-ins-creep1', ins.hv_creepage_mm);
            updateText('res-ins-um2', ins.lv_Um_kV);
            updateText('res-ins-ac2', ins.lv_AC_test_kV);
            updateText('res-ins-oil1', ins.oil_clearance_hv_mm);

            // --- KATEGORİ 3: Termodinamik & Güvenlik ---
            const th = res.thermal || res.thermo || {};
            updateText('res-total-heat', th.total_heat_loss_W || th.total_heat_loss);
            updateText('res-cooling-area', th.cooling_area_m2);
            updateText('res-oil-vol', th.oil_volume_L);
            updateText('res-oil-weight', th.oil_weight_kg);
            updateText('res-exp-vol', th.expansion_volume_L);
            updateText('res-top-oil-rise', th.top_oil_rise_C);
            updateText('res-hotspot', th.hot_spot_temp_C);
            updateText('res-thermal-tau', th.thermal_time_constant_h);
            updateText('res-conservator', th.conservator_volume_L);
            updateText('res-cooling-rec', th.recommended_cooling || 'ONAN');

            const hotspotBox = document.getElementById('res-hotspot-box');
            if (hotspotBox) {
                if (th.hot_spot_warning) {
                    hotspotBox.style.color = '#EF4444';
                    hotspotBox.title = 'Uyarı: Sıcak nokta 98°C IEC sınırının üzerindedir!';
                } else {
                    hotspotBox.style.color = 'var(--text-primary)';
                }
            }

            // Kısa Devre & Kuvvetler
            const sc = res.short_circuit || {};
            updateText('res-sc-isc1', sc.Isc_A);
            updateText('res-sc-isc2', sc.Isc2_A);
            updateText('res-sc-ipeak1', sc.Ipeak_A);
            updateText('res-sc-ipeak2', sc.Ipeak2_A);
            updateText('res-sc-xr', sc.xr_ratio);
            updateText('res-sc-k', sc.K_asymmetry);
            updateText('res-sc-faxial', sc.F_axial_N ? Number(sc.F_axial_N).toLocaleString('tr-TR') : '—');
            updateText('res-sc-fradial', sc.F_radial_N ? Number(sc.F_radial_N).toLocaleString('tr-TR') : '—');

            // --- KATEGORİ 4: Gelişmiş Verim & Yük Matrisi ---
            const ls = res.losses || {};
            updateText('res-max-eff-load', ls.max_eff_load ? (ls.max_eff_load * 100).toFixed(1) : '—');
            updateText('res-max-eff-val', ls.max_eff_value);
            updateText('res-annual-loss', ls.annual_loss_kWh ? Math.round(ls.annual_loss_kWh).toLocaleString('tr-TR') : '—');
            updateText('res-annual-co2', ls.co2_kg_year ? Math.round(ls.co2_kg_year).toLocaleString('tr-TR') : '—');

            const tbodyEff = document.getElementById('tbody-efficiency');
            if (tbodyEff && ls.efficiency_table) {
                tbodyEff.innerHTML = '';
                ls.efficiency_table.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>%${Math.round(row.load * 100)} Yük (${(row.load * (data.S/1000)).toFixed(1)} kVA)</strong></td>
                        <td><strong>% ${row['cos_1.0'] || '—'}</strong></td>
                        <td>% ${row['cos_0.9'] || '—'}</td>
                        <td>% ${row['cos_0.8'] || '—'}</td>
                    `;
                    tbodyEff.appendChild(tr);
                });
            }

            // --- KATEGORİ 5: Maliyet, TOC & LCC ---
            const cost = res.cost || {};
            const eco = res.economic || {};

            const totalCostUSD = cost.total?.total_cost || 0;
            const lossCostUSD = eco.loss_cost_usd || res.toc_analysis?.loss_cost || 0;
            const tocUSD = eco.toc_usd || res.toc_analysis?.toc || 0;
            const lccUSD = eco.lcc_usd || 0;

            updateText('res-total-cost', fmtUSD.format(totalCostUSD));
            updateText('res-total-cost-try', fmtTRY.format(totalCostUSD * usdTryRate));
            updateText('res-loss-cost', fmtUSD.format(lossCostUSD));
            updateText('res-loss-cost-try', fmtTRY.format(lossCostUSD * usdTryRate));
            updateText('res-toc', fmtUSD.format(tocUSD));
            updateText('res-toc-try', fmtTRY.format(tocUSD * usdTryRate));
            updateText('res-lcc', fmtUSD.format(lccUSD));

            updateText('res-hv-weight', cost.weights?.hv);
            updateText('res-hv-cost', fmtUSD.format(cost.total?.hv || 0));
            updateText('res-hv-cost-try', fmtTRY.format((cost.total?.hv || 0) * usdTryRate));

            updateText('res-lv-weight', cost.weights?.lv);
            updateText('res-lv-cost', fmtUSD.format(cost.total?.lv || 0));
            updateText('res-lv-cost-try', fmtTRY.format((cost.total?.lv || 0) * usdTryRate));

            updateText('res-core-weight', cost.weights?.core_weight || cd.core_weight_kg);
            updateText('res-tank-weight', cost.weights?.tank_weight || th.tank_weight_kg);
            updateText('res-dry-weight', cost.weights?.dry || th.dry_weight_kg);
            updateText('res-wet-weight', cost.weights?.wet || th.wet_weight_kg);
            updateText('res-annual-cost', fmtUSD.format(eco.annual_operating_cost_usd || 0));

            // --- Populate PDF Hidden Template ---
            updateText('pdf-I1', el.I1 + ' A');
            updateText('pdf-I2', el.I2 + ' A');
            updateText('pdf-a', el.a);
            updateText('pdf-Vk', el.Vk + ' V');
            updateText('pdf-Zk', el.Zk + ' Ω');
            updateText('pdf-Rk', el.Rk + ' Ω');
            updateText('pdf-Xk', el.Xk + ' Ω');
            updateText('pdf-Lk', el.Lk_mH + ' mH');
            updateText('pdf-ur', el.ur_pct + ' %');
            updateText('pdf-eff', el.efficiency + ' %');

            updateText('pdf-core-label', cd.core_label);
            updateText('pdf-core-bm', cd.Bm + ' T');
            updateText('pdf-core-ai', cd.Ai_cm2 + ' cm²');
            updateText('pdf-core-dia', cd.core_diameter_mm + ' mm');
            updateText('pdf-core-weight', cd.core_weight_kg + ' kg');
            updateText('pdf-core-p0', cd.P0_estimated_W + ' W');

            updateText('pdf-hv-turns', el.N1);
            updateText('pdf-hv-area', el.A1);
            updateText('pdf-lv-turns', el.N2);
            updateText('pdf-lv-area', el.A2);
            updateText('pdf-ins-bil1', ins.hv_BIL_kVp + ' kVp');
            updateText('pdf-ins-ac1', ins.hv_AC_test_kV + ' kV');
            updateText('pdf-total-cond-weight', cost.weights?.total + ' kg');
            updateText('pdf-dry-weight', cost.weights?.dry);
            updateText('pdf-wet-weight', cost.weights?.wet);

            updateText('pdf-oil-vol', th.oil_volume_L);
            updateText('pdf-exp-vol', th.expansion_volume_L);
            updateText('pdf-top-oil', th.top_oil_rise_C);
            updateText('pdf-hotspot', th.hot_spot_temp_C);
            updateText('pdf-sc-isc', sc.Isc_A + ' A');
            updateText('pdf-sc-ipeak', sc.Ipeak_A + ' A');
            updateText('pdf-sc-faxial', sc.F_axial_N + ' N');
            updateText('pdf-sc-fradial', sc.F_radial_N + ' N');

            updateText('pdf-total-cost', fmtUSD.format(totalCostUSD));
            updateText('pdf-loss-cost', fmtUSD.format(lossCostUSD));
            updateText('pdf-toc', fmtUSD.format(tocUSD));
            updateText('pdf-lcc', fmtUSD.format(lccUSD));

            // Switch UI states
            if (loadingDiv) loadingDiv.classList.add('hidden');
            if (resultsDiv) resultsDiv.classList.remove('hidden');

            // Reset tabs to 'all'
            const catTabs = document.querySelectorAll('.cat-tab');
            catTabs.forEach(t => t.classList.remove('active'));
            catTabs[0]?.classList.add('active');
            document.querySelectorAll('.category-group').forEach(g => g.style.display = '');

        } else {
            alert('Hesaplama motoru hatası: ' + (res?.error || 'Bilinmeyen hata'));
            if (loadingDiv) loadingDiv.classList.add('hidden');
            if (initialDiv) initialDiv.classList.remove('hidden');
        }
    } catch (err) {
        console.error('API Error:', err);
        alert('Hata detayı: ' + err.message);
        if (loadingDiv) loadingDiv.classList.add('hidden');
        if (initialDiv) initialDiv.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calc-form');
    const btnCalc = document.getElementById('btn-calc');
    const sidebar = document.querySelector('.sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const themeToggleBtn = document.getElementById('theme-toggle');

    // 1. Theme Management
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeToggleBtn) themeToggleBtn.textContent = 'Aydınlık Mod';
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            themeToggleBtn.textContent = isDark ? 'Aydınlık Mod' : 'Karanlık Mod';
        });
    }

    // 2. Sidebar Toggle
    if (toggleSidebarBtn && sidebar) {
        toggleSidebarBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // 3. Category Nav Smooth-Scroll & Highlight Pulse
    const catTabs = document.querySelectorAll('.cat-tab');
    catTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = tab.getAttribute('data-target');
            const targetGroup = document.getElementById(targetId);

            if (targetGroup) {
                catTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                targetGroup.scrollIntoView({ behavior: 'smooth', block: 'start' });
                targetGroup.classList.add('highlight-pulse');
                setTimeout(() => targetGroup.classList.remove('highlight-pulse'), 1200);
            }
        });
    });

    // 4. ScrollSpy with IntersectionObserver
    const resultsArea = document.querySelector('.results-area');
    const categoryGroups = document.querySelectorAll('.category-group');

    if ('IntersectionObserver' in window && resultsArea) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    catTabs.forEach(tab => {
                        if (tab.getAttribute('data-target') === id) {
                            tab.classList.add('active');
                        } else {
                            tab.classList.remove('active');
                        }
                    });
                }
            });
        }, {
            root: resultsArea,
            rootMargin: '-20px 0px -65% 0px',
            threshold: 0.05
        });

        categoryGroups.forEach(group => observer.observe(group));
    }

    // Real-time ticking digital clock (updates every second)
    function updateLiveClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const liveTimeEl = document.getElementById('live-time');
        if (liveTimeEl) {
            liveTimeEl.textContent = `CANLI ${hours}:${minutes}:${seconds}`;
        }
    }
    updateLiveClock();
    setInterval(updateLiveClock, 1000);

    // 4. Live Metal & Currency Market Tracker with Dynamic Recalculation (Every 30s)
    async function fetchPrices(isManual = false) {
        const btn = document.getElementById('btn-refresh-prices');
        if (btn && isManual) btn.textContent = 'Güncelleniyor...';

        try {
            const url = isManual ? '/api/prices?force=true' : '/api/prices';
            const response = await fetch(url);
            const res = await response.json();

            if (res && res.success && res.prices) {
                updateText('cu-price', res.prices.copper.toFixed(2) + ' $/kg');
                updateText('al-price', res.prices.aluminum.toFixed(2) + ' $/kg');
                updateText('usd-try-price', res.prices.usd_try.toFixed(2));
                usdTryRate = res.prices.usd_try || 34.00;

                const cuSrc = document.getElementById('cu-source');
                const alSrc = document.getElementById('al-source');
                if (cuSrc && res.sources?.copper) cuSrc.href = res.sources.copper;
                if (alSrc && res.sources?.aluminum) alSrc.href = res.sources.aluminum;

                // Live dynamic recalculation if results are currently visible
                if (latestData && latestData.res && latestData.res.cost) {
                    const fmtUSD = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
                    const fmtTRY = new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

                    const cuP = res.prices.copper;
                    const alP = res.prices.aluminum;
                    const req = latestData.req;
                    const cost = latestData.res.cost;
                    const eco = latestData.res.economic;

                    const hvWeight = cost.weights?.hv || 0;
                    const lvWeight = cost.weights?.lv || 0;
                    const hvCostUSD = hvWeight * (req.material_hv === 'Cu' ? cuP : alP);
                    const lvCostUSD = lvWeight * (req.material_lv === 'Cu' ? cuP : alP);
                    const totalCostUSD = hvCostUSD + lvCostUSD;
                    const lossCostUSD = eco?.loss_cost_usd || 0;
                    const tocUSD = totalCostUSD + lossCostUSD;
                    const lccLossDiff = (eco?.lcc_usd || 0) - (cost.total?.total_cost || 0);
                    const lccUSD = totalCostUSD + (lccLossDiff > 0 ? lccLossDiff : 0);

                    updateText('res-total-cost', fmtUSD.format(totalCostUSD));
                    updateText('res-total-cost-try', fmtTRY.format(totalCostUSD * usdTryRate));
                    updateText('res-loss-cost', fmtUSD.format(lossCostUSD));
                    updateText('res-loss-cost-try', fmtTRY.format(lossCostUSD * usdTryRate));
                    updateText('res-toc', fmtUSD.format(tocUSD));
                    updateText('res-toc-try', fmtTRY.format(tocUSD * usdTryRate));
                    updateText('res-lcc', fmtUSD.format(lccUSD));

                    updateText('res-hv-cost', fmtUSD.format(hvCostUSD));
                    updateText('res-hv-cost-try', fmtTRY.format(hvCostUSD * usdTryRate));
                    updateText('res-lv-cost', fmtUSD.format(lvCostUSD));
                    updateText('res-lv-cost-try', fmtTRY.format(lvCostUSD * usdTryRate));

                    // Visual pulse flash on Category 5 Cost Card
                    const costCard = document.querySelector('#cat-5 .card');
                    if (costCard) {
                        costCard.classList.remove('price-flash');
                        void costCard.offsetWidth;
                        costCard.classList.add('price-flash');
                    }
                }
            }
        } catch (err) {
            console.error('Piyasa verisi alınamadı:', err);
        } finally {
            if (btn && isManual) btn.textContent = 'Piyasayı Güncelle';
        }
    }

    // Initial fetch & 30-second live polling
    fetchPrices(false);
    setInterval(() => fetchPrices(false), 30000);

    const btnRefreshPrices = document.getElementById('btn-refresh-prices');
    if (btnRefreshPrices) {
        btnRefreshPrices.addEventListener('click', () => fetchPrices(true));
    }

    // 5. PDF Specification Auto-Fill
    const pdfUpload = document.getElementById('pdf-upload');
    const pdfStatus = document.getElementById('pdf-status');
    
    if (pdfUpload) {
        pdfUpload.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            if (pdfStatus) {
                pdfStatus.textContent = 'Şartname analiz ediliyor...';
                pdfStatus.style.color = 'var(--accent-blue)';
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/parse-pdf', {
                    method: 'POST',
                    body: formData
                });
                const res = await response.json();

                if (res && res.success && res.data) {
                    if (res.data.S) document.getElementById('S').value = res.data.S;
                    if (res.data.V1) document.getElementById('V1').value = res.data.V1;
                    if (res.data.V2) document.getElementById('V2').value = res.data.V2;
                    if (res.data.uk) document.getElementById('uk').value = res.data.uk;
                    if (res.data.P0) document.getElementById('P0').value = res.data.P0;
                    if (res.data.Pk) document.getElementById('Pk').value = res.data.Pk;
                    if (res.data.phase) document.getElementById('phase').value = res.data.phase;
                    if (res.data.frequency) document.getElementById('frequency').value = res.data.frequency;
                    if (res.data.material_hv) document.getElementById('material_hv').value = res.data.material_hv;
                    if (res.data.material_lv) document.getElementById('material_lv').value = res.data.material_lv;

                    if (pdfStatus) {
                        pdfStatus.textContent = 'Şartname başarıyla ayrıştırıldı. Hesaplama başlatılıyor...';
                        pdfStatus.style.color = 'var(--accent-green)';
                    }
                    
                    setTimeout(() => doCalculate(), 300);
                } else {
                    if (pdfStatus) {
                        pdfStatus.textContent = 'Hata: ' + (res.error || 'Ayrıştırma başarısız');
                        pdfStatus.style.color = '#EF4444';
                    }
                }
            } catch (err) {
                if (pdfStatus) {
                    pdfStatus.textContent = 'Hata: Sunucu hatası';
                    pdfStatus.style.color = '#EF4444';
                }
            }
        });
    }

    // 6. Bind Calculation on Both Form Submit & Button Click
    if (form) {
        form.addEventListener('submit', doCalculate);
    }
    if (btnCalc) {
        btnCalc.addEventListener('click', (e) => {
            e.preventDefault();
            doCalculate(e);
        });
    }

    // 7. Reset Form
    const btnReset = document.getElementById('btn-reset');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            const resultsDiv = document.getElementById('results');
            const initialDiv = document.getElementById('initial-state');
            if (resultsDiv) resultsDiv.classList.add('hidden');
            if (initialDiv) initialDiv.classList.remove('hidden');
            if (sidebar) sidebar.classList.remove('collapsed');
        });
    }

    // 8. Server-Side Vector PDF Export in New Tab (ReportLab)
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    if (btnDownloadPdf) {
        btnDownloadPdf.addEventListener('click', async () => {
            const btn = document.getElementById('btn-download-pdf');
            if (btn) btn.textContent = 'Rapor Hazırlanıyor...';

            const data = {
                S: getVal('S', 50000),
                V1: getVal('V1', 34500),
                V2: getVal('V2', 400),
                uk: getVal('uk', 4.5),
                P0: getVal('P0', 150),
                Pk: getVal('Pk', 900),
                phase: parseInt(getStr('phase', '3')),
                frequency: getVal('frequency', 50),
                material_hv: getStr('material_hv', 'Cu'),
                material_lv: getStr('material_lv', 'Cu'),
                core_material: getStr('core_material', 'M4'),
                oil_type: getStr('oil_type', 'mineral'),
                k_constant: getVal('k_constant', 0.45),
                delta_T: getVal('delta_T', 60),
                ambient_temp: getVal('ambient_temp', 30),
                cooling_method: getStr('cooling_method', 'ONAN'),
                A_factor: getVal('A_factor', 8.0),
                B_factor: getVal('B_factor', 2.0)
            };

            try {
                const response = await fetch('/api/download-pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) throw new Error('PDF oluşturulamadı');

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const win = window.open(url, '_blank');
                if (!win) {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'Transformator_Muhendislik_Raporu.pdf';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            } catch (err) {
                console.error('PDF Hatası:', err);
                alert('PDF oluşturulamadı: ' + err.message);
            } finally {
                if (btn) btn.textContent = 'Mühendislik Raporunu İndir (PDF)';
            }
        });
    }
});

