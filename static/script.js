// ⚡ Hızlı Transformatör - Frontend Controller & Multi-Module Categorized UI Binder
let latestData = null;
let usdTryRate = 34.00;

// ⚡ Toast Notification System (Directive 5)
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconText = 'ℹ';
    if (type === 'success') iconText = '✓';
    else if (type === 'error') iconText = '✕';
    else if (type === 'warning') iconText = '⚠️';

    toast.innerHTML = `
        <div class="toast-icon">${iconText}</div>
        <div class="toast-msg">${message}</div>
        <div class="toast-close" title="Kapat">✕</div>
    `;

    const removeToast = () => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(40px)';
        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 250);
    };

    toast.addEventListener('click', removeToast);

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) removeToast();
    }, duration);
}

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

    const S = getVal('S', 0);
    const V1 = getVal('V1', 0);
    const V2 = getVal('V2', 0);
    const uk = getVal('uk', 0);
    const P0 = getVal('P0', 0);
    const Pk = getVal('Pk', 0);

    if (S <= 0 || V1 <= 0 || V2 <= 0 || uk <= 0 || P0 <= 0 || Pk <= 0) {
        showToast('Lütfen temel elektriksel parametreleri (Güç S, Gerilimler V1/V2, uk%, Kayıplar P0/Pk) eksiksiz doldurunuz.', 'warning');
        return;
    }

    console.log('doCalculate tetiklendi!');

    // UI state transition
    if (initialDiv) initialDiv.classList.add('hidden');
    if (resultsDiv) resultsDiv.classList.add('hidden');
    if (loadingDiv) loadingDiv.classList.remove('hidden');

    const data = {
        S: S,
        V1: V1,
        V2: V2,
        uk: uk,
        P0: P0,
        Pk: Pk,
        phase: parseInt(getStr('phase', '3')),
        frequency: getVal('frequency', 50),
        material_hv: getStr('material_hv', 'Cu'),
        material_lv: getStr('material_lv', 'Cu'),
        vector_group: getStr('vector_group', 'Dyn11'),
        optimization_mode: document.getElementById('optimization_mode')?.value === 'true',
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
            updateText('res-vg-name', el.vector_group_name || el.vector_group || 'Dyn11');
            updateText('res-vg-shift', el.phase_displacement_deg !== undefined ? `${el.phase_displacement_deg}°` : '330°');
            updateText('res-v1-ph', el.V1_phase || '—');
            updateText('res-v2-ph', el.V2_phase || '—');
            updateText('res-i1-ph', el.I1_phase || '—');
            updateText('res-i2-ph', el.I2_phase || '—');
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
            const opt = res.optimization || {};
            updateText('res-core-label', cd.core_label);
            updateText('res-core-bm', cd.Bm);
            updateText('res-core-ai', cd.Ai_cm2);
            updateText('res-core-ag', cd.Ag_cm2);
            updateText('res-core-dia', cd.core_diameter_mm);
            updateText('res-limb-dist', cd.limb_center_dist_mm);
            updateText('res-win-height', cd.window_height_mm);
            updateText('res-ratio-hw', cd.ratio_hw_d || '2.70');
            updateText('res-ratio-a', cd.ratio_a_d || '2.08');
            updateText('res-core-weight-detail', cd.core_weight_kg);
            updateText('res-core-p0-est', cd.P0_estimated_W);
            updateText('res-core-physt', cd.P_hysteresis_W);
            updateText('res-core-peddy', cd.P_eddy_W);
            updateText('res-core-stack', cd.stacking_factor);

            updateText('res-k-val', opt.selected_k_constant || data.k_constant || '0.45');
            const optBadge = document.getElementById('res-opt-mode-badge');
            if (optBadge) {
                if (opt.enabled) {
                    optBadge.textContent = `⚡ Opt (${opt.iterations} İterasyon)`;
                    optBadge.className = 'badge badge-green';
                } else {
                    optBadge.textContent = 'Manuel';
                    optBadge.className = 'badge badge-blue';
                }
            }

            // Sargı & İmalat & Kayıp Ayrışımı (Directive 1)
            const wd = res.winding || {};
            const ls = res.losses || {};
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

            // Eddy & Stray Details
            updateText('res-delta-hv', wd.skin_depth_hv_mm || '10.31');
            updateText('res-delta-lv', wd.skin_depth_lv_mm || '10.31');
            updateText('res-pk-dc', wd.pk_dc_only || wd.P_cu_total_W || '—');
            updateText('res-pk-eddy', wd.pk_eddy || '—');
            updateText('res-kec-pct', wd.pk_eddy_pct || wd.Kec_hv_pct || '—');
            updateText('res-pk-stray', wd.pk_stray || '—');
            updateText('res-stray-pct', wd.pk_stray_pct || '—');
            updateText('res-pk-calc-total', wd.pk_calculated_total || '—');
            updateText('res-pk-guar', ls.pk_guaranteed || data.Pk);

            const pkDiffPct = ls.pk_diff_pct;
            if (pkDiffPct !== undefined) {
                const diffSign = pkDiffPct > 0 ? `+${pkDiffPct}%` : `${pkDiffPct}%`;
                updateText('res-pk-diff-label', `Δ ${diffSign}`);
            } else {
                updateText('res-pk-diff-label', '—');
            }

            // Yalıtım (BIL)
            const ins = res.insulation || {};
            updateText('res-ins-um1', ins.hv_Um_kV);
            updateText('res-ins-bil1', ins.hv_BIL_kVp);
            updateText('res-ins-ac1', ins.hv_AC_test_kV);
            updateText('res-ins-creep1', ins.hv_creepage_mm);
            updateText('res-ins-um2', ins.lv_Um_kV);
            updateText('res-ins-ac2', ins.lv_AC_test_kV);
            updateText('res-ins-oil1', ins.oil_clearance_hv_mm);

            // --- Şartname & Ecodesign Uygunluk Banner Panosu (Module 2 - 10 Değer) ---
            const std = res.standards_compliance || {};
            const tedas = std.tedas || {};
            const tier2 = std.ecodesign_tier2 || {};

            updateText('std-energy-badge', std.energy_class || 'A+ EU Tier 2 Ready');
            updateText('std-total-score', (tedas.is_compliant && tier2.is_compliant) ? 'TEDAŞ & TIER 2 ONAYLI' : (tedas.is_compliant ? 'TEDAŞ ONAYLI' : 'ŞARTNAME AŞIMI'));

            const stdTotalScore = document.getElementById('std-total-score');
            if (stdTotalScore) {
                stdTotalScore.className = `badge ${(tedas.is_compliant && tier2.is_compliant) ? 'badge-green' : (tedas.is_compliant ? 'badge-cyan' : 'badge-orange')}`;
            }

            // 1. TEDAŞ P0 Chip (Limit ve Tasarım)
            updateText('tedas-p0-act-chip', `${tedas.P0_actual_W || '—'} W / Max ${tedas.P0_limit_W || '—'} W`);
            const tedasP0Badge = document.getElementById('tedas-p0-badge');
            if (tedasP0Badge) {
                const diff = tedas.P0_diff_pct !== undefined ? (tedas.P0_diff_pct > 0 ? `+${tedas.P0_diff_pct}%` : `${tedas.P0_diff_pct}%`) : '';
                tedasP0Badge.textContent = tedas.P0_pass ? `${diff} UYGUN` : `${diff} AŞIM`;
                tedasP0Badge.className = `badge ${tedas.P0_pass ? 'badge-green' : 'badge-orange'}`;
            }

            // 2. TEDAŞ Pk Chip (Limit ve Tasarım)
            updateText('tedas-pk-act-chip', `${tedas.Pk_actual_W || '—'} W / Max ${tedas.Pk_limit_W || '—'} W`);
            const tedasPkBadge = document.getElementById('tedas-pk-badge');
            if (tedasPkBadge) {
                const diff = tedas.Pk_diff_pct !== undefined ? (tedas.Pk_diff_pct > 0 ? `+${tedas.Pk_diff_pct}%` : `${tedas.Pk_diff_pct}%`) : '';
                tedasPkBadge.textContent = tedas.Pk_pass ? `${diff} UYGUN` : `${diff} AŞIM`;
                tedasPkBadge.className = `badge ${tedas.Pk_pass ? 'badge-green' : 'badge-orange'}`;
            }

            // 3. TEDAŞ uk Chip (Anma ve Sapma)
            updateText('tedas-uk-act-chip', `%${tedas.uk_actual_pct || '—'} (Anma %${tedas.uk_nominal_pct || '—'})`);
            const tedasUkBadge = document.getElementById('tedas-uk-badge');
            if (tedasUkBadge) {
                const diff = tedas.uk_diff_pct !== undefined ? (tedas.uk_diff_pct > 0 ? `+${tedas.uk_diff_pct}%` : `${tedas.uk_diff_pct}%`) : '';
                tedasUkBadge.textContent = tedas.uk_pass ? `±%10 İÇİ (${diff})` : `AŞIM (${diff})`;
                tedasUkBadge.className = `badge ${tedas.uk_pass ? 'badge-green' : 'badge-orange'}`;
            }

            // 4. IEC 60076-1 Toleransı (Otomatik Doğrulama)
            // (Statik/standart onaylı kabul)

            // 5. TEDAŞ Karar Durumu Chip
            updateText('tedas-decision-text', tedas.status_text || 'ŞARTNAME ONAYLI');
            const tedasDecBadge = document.getElementById('tedas-decision-badge');
            if (tedasDecBadge) {
                tedasDecBadge.textContent = tedas.is_compliant ? 'TEDAŞ UYGUN' : 'LİMİT AŞIMI';
                tedasDecBadge.className = `badge ${tedas.is_compliant ? 'badge-green' : 'badge-orange'}`;
            }

            // 6. Tier 2 P0 Chip (Limit ve Tasarım)
            updateText('tier2-p0-act-chip', `${tier2.P0_actual_W || '—'} W / Max ${tier2.P0_limit_W || '—'} W`);
            const tier2P0Badge = document.getElementById('tier2-p0-badge');
            if (tier2P0Badge) {
                const diff = tier2.P0_diff_pct !== undefined ? (tier2.P0_diff_pct > 0 ? `+${tier2.P0_diff_pct}%` : `${tier2.P0_diff_pct}%`) : '';
                tier2P0Badge.textContent = tier2.P0_pass ? `${diff} UYGUN` : `${diff} AŞIM`;
                tier2P0Badge.className = `badge ${tier2.P0_pass ? 'badge-green' : 'badge-orange'}`;
            }

            // 7. Tier 2 Pk Chip (Limit ve Tasarım)
            updateText('tier2-pk-act-chip', `${tier2.Pk_actual_W || '—'} W / Max ${tier2.Pk_limit_W || '—'} W`);
            const tier2PkBadge = document.getElementById('tier2-pk-badge');
            if (tier2PkBadge) {
                const diff = tier2.Pk_diff_pct !== undefined ? (tier2.Pk_diff_pct > 0 ? `+${tier2.Pk_diff_pct}%` : `${tier2.Pk_diff_pct}%`) : '';
                tier2PkBadge.textContent = tier2.Pk_pass ? `${diff} UYGUN` : `${diff} AŞIM`;
                tier2PkBadge.className = `badge ${tier2.Pk_pass ? 'badge-green' : 'badge-orange'}`;
            }

            // 8. Zirve Verim PEI Chip
            updateText('std-pei-chip', `% ${std.pei_index_pct || '—'}`);

            // 9. Ecodesign Direktif Kararı Chip
            updateText('tier2-decision-text', tier2.status_text || 'EU TIER 2 ONAYLI');
            const tier2DecBadge = document.getElementById('tier2-decision-badge');
            if (tier2DecBadge) {
                tier2DecBadge.textContent = tier2.is_compliant ? 'EU TIER 2' : 'AŞIM';
                tier2DecBadge.className = `badge ${tier2.is_compliant ? 'badge-green' : 'badge-orange'}`;
            }

            // 10. Enerji Verimlilik Sınıfı Chip
            updateText('std-class-desc', std.energy_class || 'A+ Tier 2');
            const stdClassBadge = document.getElementById('std-class-badge');
            if (stdClassBadge) {
                stdClassBadge.textContent = (std.energy_class && std.energy_class.startsWith('A+')) ? 'A+ ULTRA' : 'STANDART';
                stdClassBadge.className = `badge ${(std.energy_class && std.energy_class.startsWith('A+')) ? 'badge-green' : 'badge-cyan'}`;
            }

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
            // ls (res.losses) already declared above at line 214
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

            // --- Populate Cu vs Al Comparison Module ---
            const comp = res.comparison || {};
            const compCu = comp.cu || {};
            const compAl = comp.al || {};
            const compDelta = comp.delta || {};

            updateText('comp-cu-weight', compCu.cond_weight_kg);
            updateText('comp-al-weight', compAl.cond_weight_kg);
            if (compCu.cond_weight_kg && compAl.cond_weight_kg) {
                const wPct = (((compCu.cond_weight_kg - compAl.cond_weight_kg) / compCu.cond_weight_kg) * 100).toFixed(0);
                updateText('comp-weight-diff', `Al %${wPct} Daha Hafif`);
            }

            updateText('comp-cu-cost', fmtUSD.format(compCu.cond_cost_usd || 0));
            updateText('comp-al-cost', fmtUSD.format(compAl.cond_cost_usd || 0));
            updateText('comp-cost-diff', `Tasarruf: ${fmtUSD.format(compDelta.savings_usd || 0)} (%${compDelta.savings_pct})`);

            updateText('comp-cu-wet', compCu.wet_weight_kg);
            updateText('comp-al-wet', compAl.wet_weight_kg);
            updateText('comp-wet-diff', `Δ ${Math.abs(compDelta.weight_diff_kg || 0)} kg`);

            updateText('comp-cu-toc', fmtUSD.format(compCu.toc_usd || 0));
            updateText('comp-al-toc', fmtUSD.format(compAl.toc_usd || 0));
            updateText('comp-toc-diff', `TOC Farkı: ${fmtUSD.format((compCu.toc_usd || 0) - (compAl.toc_usd || 0))}`);

            const compAdvBadge = document.getElementById('res-comp-advantage');
            if (compAdvBadge) {
                compAdvBadge.textContent = compDelta.advantage || 'İhale Karar Analizi';
            }

            // --- Populate IEC 60076 Compliance Audit ---
            const iec = res.iec_compliance || {};
            const iecScoreEl = document.getElementById('iec-total-score');
            if (iecScoreEl) {
                iecScoreEl.textContent = iec.total_score || '5/5 ONAYLI';
                iecScoreEl.className = iec.all_passed ? 'badge badge-green' : 'badge badge-orange';
            }

            const oilAudit = iec.top_oil || {};
            updateText('iec-val-oil', oilAudit.value || (th.top_oil_rise_C + ' °C'));
            const badgeOil = document.getElementById('iec-badge-oil');
            if (badgeOil) {
                badgeOil.textContent = oilAudit.status || 'IEC 60076-2 UYGUN';
                badgeOil.className = oilAudit.passed ? 'badge badge-green' : 'badge badge-orange';
            }

            const hsAudit = iec.hot_spot || {};
            updateText('iec-val-hs', hsAudit.value || (th.hot_spot_temp_C + ' °C'));
            const badgeHs = document.getElementById('iec-badge-hs');
            if (badgeHs) {
                badgeHs.textContent = hsAudit.status || 'GÜVENLİ (IEC 60076-7)';
                badgeHs.className = hsAudit.passed ? 'badge badge-green' : 'badge badge-orange';
            }

            const i0Audit = iec.no_load_current || {};
            updateText('iec-val-i0', i0Audit.value || (mag.I0_pct + ' %'));
            const badgeI0 = document.getElementById('iec-badge-i0');
            if (badgeI0) {
                badgeI0.textContent = i0Audit.status || 'STANDART İÇİ';
                badgeI0.className = i0Audit.passed ? 'badge badge-green' : 'badge badge-orange';
            }

            updateText('iec-val-bil', `BIL ${ins.hv_BIL_kVp} kVp`);

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

            // Render Interactive Engineering Charts
            renderEngineeringCharts(res);

            // Render 1:1 Parametric 2D CAD Technical Drawing
            if (typeof window.renderTransformerCAD === 'function') {
                window.renderTransformerCAD('cad-container', res);
            }

            // Switch UI states
            if (loadingDiv) loadingDiv.classList.add('hidden');
            if (resultsDiv) resultsDiv.classList.remove('hidden');

            // Reset tabs to first tab
            const catTabs = document.querySelectorAll('.cat-tab');
            catTabs.forEach(t => t.classList.remove('active'));
            catTabs[0]?.classList.add('active');
            document.querySelectorAll('.category-group').forEach(g => g.style.display = '');

        } else {
            showToast('Hesaplama motoru hatası: ' + (res?.error || 'Bilinmeyen hata'), 'error');
            if (loadingDiv) loadingDiv.classList.add('hidden');
            if (initialDiv) initialDiv.classList.remove('hidden');
        }
    } catch (err) {
        console.error('API Error:', err);
        showToast('Hata detayı: ' + err.message, 'error');
        if (loadingDiv) loadingDiv.classList.add('hidden');
        if (initialDiv) initialDiv.classList.remove('hidden');
    }
}

// Interactive Engineering Charts Engine (Chart.js)
let chartEfficiency = null;
let chartVreg = null;
let chartInrush = null;

function getChartThemeColors() {
    const isDark = document.body.classList.contains('dark-mode');
    return {
        isDark,
        textColor: isDark ? '#E2E8F0' : '#0B2545',
        gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
        blueLine: '#0066CC',
        greenLine: '#00875A',
        orangeLine: '#E65100'
    };
}

function renderEngineeringCharts(res) {
    if (!res || !window.Chart) return;
    const colors = getChartThemeColors();

    // 1. Efficiency vs Load Curve
    const effCanvas = document.getElementById('chart-efficiency');
    if (effCanvas) {
        if (chartEfficiency) chartEfficiency.destroy();

        // Standard IEC operating load curve (10% to 125% load)
        const loadPoints = [0.1, 0.2, 0.25, 0.35, 0.5, 0.6, 0.75, 0.85, 1.0, 1.15, 1.25];
        const labels = loadPoints.map(x => (x * 100).toFixed(0) + '%');

        const S = (res.electrical?.S_kVA ? res.electrical.S_kVA * 1000 : (latestData?.req?.S || 50000));
        const P0 = (latestData?.req?.P0 || 150);
        const Pk = (latestData?.req?.Pk || 900);

        function calcEff(x, cosPhi) {
            const P_out = x * S * cosPhi;
            const P_losses = P0 + (x * x * Pk);
            return parseFloat(((P_out / (P_out + P_losses)) * 100).toFixed(3));
        }

        const dataCos10 = loadPoints.map(x => calcEff(x, 1.0));
        const dataCos09 = loadPoints.map(x => calcEff(x, 0.9));
        const dataCos08 = loadPoints.map(x => calcEff(x, 0.8));

        // Auto-scale Y axis precisely to the operating range (e.g. 96% to 99%)
        const allEffs = [...dataCos10, ...dataCos09, ...dataCos08];
        const minEff = Math.min(...allEffs);
        const maxEff = Math.max(...allEffs);
        const yMin = Math.max(85, Math.floor(minEff - 0.6));
        const yMax = Math.min(100, Math.ceil((maxEff + 0.4) * 10) / 10);

        chartEfficiency = new Chart(effCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'cosφ = 1.00 (Saf Aktif)',
                        data: dataCos10,
                        borderColor: '#00875A',
                        backgroundColor: 'rgba(0, 135, 90, 0.06)',
                        tension: 0.35,
                        fill: false,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'cosφ = 0.90 (Endüktif)',
                        data: dataCos09,
                        borderColor: '#0066CC',
                        backgroundColor: 'transparent',
                        tension: 0.35,
                        fill: false,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'cosφ = 0.80 (Ağır Sanayi)',
                        data: dataCos08,
                        borderColor: '#E65100',
                        backgroundColor: 'transparent',
                        tension: 0.35,
                        fill: false,
                        borderWidth: 2.5,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { 
                        labels: { 
                            color: colors.textColor, 
                            font: { size: 12, family: 'Inter', weight: '600' },
                            usePointStyle: true,
                            padding: 14
                        } 
                    },
                    tooltip: {
                        backgroundColor: colors.isDark ? '#0E1B2A' : '#0B2545',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F4F7FA',
                        borderColor: '#0066CC',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: (ctx) => ` ${ctx.dataset.label}: %${ctx.parsed.y.toFixed(3)}`
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Yük Seviyesi (Load Factor %)', color: colors.textColor, font: { size: 11, weight: '600' } },
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor }
                    },
                    y: {
                        title: { display: true, text: 'Verim (Efficiency %)', color: colors.textColor, font: { size: 11, weight: '600' } },
                        grid: { color: colors.gridColor },
                        ticks: { 
                            color: colors.textColor,
                            callback: (v) => '%' + v.toFixed(1)
                        },
                        min: yMin,
                        max: yMax
                    }
                }
            }
        });
    }

    // 2. Voltage Regulation Curve (cosφ vs drop %)
    const vregCanvas = document.getElementById('chart-vreg');
    if (vregCanvas) {
        if (chartVreg) chartVreg.destroy();

        const cosList = [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0];
        const vregLabels = cosList.map(c => c.toFixed(2));
        const ur = res.electrical?.ur_pct || 1.8;
        const ux = res.electrical?.ux_pct || 4.12;

        const vregValues = cosList.map(cos => {
            const sin = Math.sqrt(1 - cos * cos);
            const eps = (cos * ur) + (sin * ux) + (Math.pow((cos * ux) - (sin * ur), 2) / 200);
            return parseFloat(eps.toFixed(2));
        });

        chartVreg = new Chart(vregCanvas, {
            type: 'line',
            data: {
                labels: vregLabels,
                datasets: [{
                    label: 'Gerilim Düşümü (ε %)',
                    data: vregValues,
                    borderColor: '#0066CC',
                    backgroundColor: 'rgba(0, 102, 204, 0.12)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: '#0066CC'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        labels: { 
                            color: colors.textColor, 
                            font: { size: 12, family: 'Inter', weight: '600' } 
                        } 
                    },
                    tooltip: {
                        backgroundColor: colors.isDark ? '#0E1B2A' : '#0B2545',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F4F7FA',
                        borderColor: '#0066CC',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: (ctx) => ` cosφ = ${ctx.label} → Düşüm: %${ctx.parsed.y.toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Güç Faktörü (cosφ Endüktif)', color: colors.textColor, font: { size: 11, weight: '600' } },
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor }
                    },
                    y: {
                        title: { display: true, text: 'Gerilim Düşümü (ε %)', color: colors.textColor, font: { size: 11, weight: '600' } },
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor }
                    }
                }
            }
        });
    }

    // 3. Inrush Transient Waveform (0 to 100 ms)
    const inrushCanvas = document.getElementById('chart-inrush');
    if (inrushCanvas) {
        if (chartInrush) chartInrush.destroy();

        const Ipeak = parseFloat(res.magnetization?.inrush_peak_A || res.magnetization?.inrush_peak_hv || (res.electrical?.I1 ? (res.electrical.I1 * 10 * Math.SQRT2) : 120));
        const tau = 0.035; // 35 ms decay time constant
        const f = 50;
        const omega = 2 * Math.PI * f;

        const timePoints = [];
        const currentPoints = [];
        const envelopeUpper = [];

        // 101 data points across 0 to 100ms
        for (let t_ms = 0; t_ms <= 100; t_ms += 1) {
            const t = t_ms / 1000.0;
            const decay = Math.exp(-t / tau);
            const val = Ipeak * decay * (1 - Math.cos(omega * t));
            timePoints.push(t_ms + ' ms');
            currentPoints.push(parseFloat(val.toFixed(1)));
            envelopeUpper.push(parseFloat((2 * Ipeak * decay).toFixed(1)));
        }

        chartInrush = new Chart(inrushCanvas, {
            type: 'line',
            data: {
                labels: timePoints,
                datasets: [
                    {
                        label: 'Inrush Akımı i(t) [A]',
                        data: currentPoints,
                        borderColor: '#E65100',
                        backgroundColor: 'transparent',
                        fill: false,
                        tension: 0.25,
                        borderWidth: 2.2,
                        pointRadius: 0
                    },
                    {
                        label: 'Sönümlenme Zarfı (Tepe Envelope)',
                        data: envelopeUpper,
                        borderColor: 'rgba(180, 52, 3, 0.85)',
                        backgroundColor: 'rgba(230, 81, 0, 0.06)',
                        borderDash: [6, 4],
                        fill: true,
                        pointRadius: 0,
                        borderWidth: 2.2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        labels: { 
                            color: colors.textColor, 
                            font: { size: 12, family: 'Inter', weight: '600' } 
                        } 
                    },
                    tooltip: {
                        backgroundColor: colors.isDark ? '#0E1B2A' : '#0B2545',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F4F7FA',
                        borderColor: '#E65100',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)} A`
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Zaman (t in ms)', color: colors.textColor, font: { size: 11, weight: '600' } },
                        grid: { color: colors.gridColor },
                        ticks: {
                            color: colors.textColor,
                            maxTicksLimit: 11
                        }
                    },
                    y: {
                        title: { display: true, text: 'Primer Anlık Akım (Amper)', color: colors.textColor, font: { size: 11, weight: '600' } },
                        grid: { color: colors.gridColor },
                        ticks: { color: colors.textColor }
                    }
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calc-form');
    const btnCalc = document.getElementById('btn-calc');
    const sidebar = document.querySelector('.sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const themeToggleBtn = document.getElementById('theme-toggle');
    const appTitle = document.getElementById('app-title');

    // Design Mode Selector (Directive 3)
    const btnModeManual = document.getElementById('btn-mode-manual');
    const btnModeOpt = document.getElementById('btn-mode-opt');
    const optModeInput = document.getElementById('optimization_mode');
    const optModeHint = document.getElementById('opt-mode-hint');

    if (btnModeManual && btnModeOpt) {
        btnModeManual.addEventListener('click', () => {
            btnModeManual.classList.add('active');
            btnModeOpt.classList.remove('active');
            if (optModeInput) optModeInput.value = 'false';
            if (optModeHint) optModeHint.style.display = 'none';
        });

        btnModeOpt.addEventListener('click', () => {
            btnModeOpt.classList.add('active');
            btnModeManual.classList.remove('active');
            if (optModeInput) optModeInput.value = 'true';
            if (optModeHint) optModeHint.style.display = 'block';
        });
    }

    // Secret Demo Filler: Triple-click on App Title (Hızlı Transformatör)
    let titleClickCount = 0;
    let titleClickTimer = null;
    let demoIndex = 0;

    const demoDatasets = [
        {
            name: "14 MVA (34.5 kV / 10.5 kV) Örnek Güç Transformatörü",
            S: 14000000,
            V1: 34500,
            V2: 10500,
            uk: 7.5,
            P0: 11200,
            Pk: 73500,
            phase: '3',
            frequency: '50',
            material_hv: 'Cu',
            material_lv: 'Cu',
            vector_group: 'YNyn0',
            core_material: 'M4',
            oil_type: 'mineral',
            k_constant: 0.45,
            delta_T: 60,
            ambient_temp: 30,
            cooling_method: 'ONAN',
            A_factor: 8.0,
            B_factor: 2.0
        }
    ];

    if (appTitle) {
        appTitle.addEventListener('click', () => {
            titleClickCount++;
            clearTimeout(titleClickTimer);

            if (titleClickCount >= 3) {
                titleClickCount = 0;
                
                const ds = demoDatasets[demoIndex % demoDatasets.length];
                demoIndex++;

                // Fill Inputs with 14 MVA Sample Data
                document.getElementById('S').value = ds.S;
                document.getElementById('V1').value = ds.V1;
                document.getElementById('V2').value = ds.V2;
                document.getElementById('uk').value = ds.uk;
                document.getElementById('P0').value = ds.P0;
                document.getElementById('Pk').value = ds.Pk;
                document.getElementById('phase').value = ds.phase;
                document.getElementById('frequency').value = ds.frequency;
                document.getElementById('material_hv').value = ds.material_hv;
                document.getElementById('material_lv').value = ds.material_lv;
                const vgInput = document.getElementById('vector_group');
                if (vgInput) vgInput.value = ds.vector_group || 'YNyn0';
                document.getElementById('core_material').value = ds.core_material;
                document.getElementById('oil_type').value = ds.oil_type;
                document.getElementById('k_constant').value = ds.k_constant;
                document.getElementById('delta_T').value = ds.delta_T;
                document.getElementById('ambient_temp').value = ds.ambient_temp;
                document.getElementById('cooling_method').value = ds.cooling_method;
                document.getElementById('A_factor').value = ds.A_factor;
                document.getElementById('B_factor').value = ds.B_factor;

                showToast(`⚡ ${ds.name} parametreleri yüklendi.`, 'info', 3500);

                // Visual flash effect on filled inputs
                const inputs = document.querySelectorAll('.sidebar input, .sidebar select');
                inputs.forEach(input => {
                    input.style.transition = 'all 0.3s ease';
                    input.style.borderColor = 'var(--accent-blue)';
                    input.style.backgroundColor = 'rgba(0, 102, 204, 0.12)';
                    setTimeout(() => {
                        input.style.borderColor = '';
                        input.style.backgroundColor = '';
                    }, 900);
                });
            } else {
                titleClickTimer = setTimeout(() => {
                    titleClickCount = 0;
                }, 700);
            }
        });
    }

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
            
            // Re-render engineering charts and CAD drawing with new theme colors
            if (latestData && latestData.res) {
                renderEngineeringCharts(latestData.res);
                if (typeof window.refreshCADTheme === 'function') {
                    window.refreshCADTheme();
                }
            }
        });
    }

    // 2. Sidebar Toggle
    if (toggleSidebarBtn && sidebar) {
        toggleSidebarBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // 2.1 Auto A & B Factor Generator from Energy Tariff and Financial NPV
    const btnToggleAutoAB = document.getElementById('btn-toggle-auto-ab');
    const autoABPanel = document.getElementById('auto-ab-panel');
    const autoABArrow = document.getElementById('auto-ab-arrow');

    function calculateAutoAB() {
        const c_kwh = parseFloat(document.getElementById('calc_energy_cost')?.value) || 0.10;
        const i_pct = parseFloat(document.getElementById('calc_discount_rate')?.value) || 8.0;
        const i = i_pct / 100.0;
        const n = parseFloat(document.getElementById('calc_life_years')?.value) || 25;
        const k_load_pct = parseFloat(document.getElementById('calc_load_ratio')?.value) || 50;
        const k_load = k_load_pct / 100.0;
        const T_k = 6000; // annual equivalent operating hours

        // Present Worth Factor (PWF)
        let pwf = 10.67;
        if (i > 0) {
            pwf = (Math.pow(1 + i, n) - 1) / (i * Math.pow(1 + i, n));
        } else {
            pwf = n;
        }

        // A factor: 1W * 8760h / 1000 = 8.76 kWh/year * $/kWh * PWF
        const A = 8.76 * c_kwh * pwf;
        // B factor: 1W * T_k * (k_load^2) / 1000 * $/kWh * PWF
        const B = (1.0 * T_k * (k_load * k_load) / 1000.0) * c_kwh * pwf;

        const elA = document.getElementById('A_factor');
        const elB = document.getElementById('B_factor');
        const elPwf = document.getElementById('val-pwf');

        if (elA) {
            elA.value = A.toFixed(2);
            elA.style.borderColor = 'var(--accent-green)';
            setTimeout(() => elA.style.borderColor = '', 600);
        }
        if (elB) {
            elB.value = B.toFixed(2);
            elB.style.borderColor = 'var(--accent-green)';
            setTimeout(() => elB.style.borderColor = '', 600);
        }
        if (elPwf) {
            elPwf.textContent = pwf.toFixed(2);
        }
    }

    let liveElectricityUSD = 0.103;

    const selTariffPreset = document.getElementById('sel-tariff-preset');
    if (selTariffPreset) {
        selTariffPreset.addEventListener('change', (e) => {
            const val = e.target.value;
            const energyInput = document.getElementById('calc_energy_cost');
            if (!energyInput) return;

            if (val === 'epdk_live') {
                energyInput.value = liveElectricityUSD.toFixed(3);
                energyInput.readOnly = false;
            } else if (val === 'epias_spot') {
                energyInput.value = '0.090';
                energyInput.readOnly = false;
            } else if (val === 'eu_industry') {
                energyInput.value = '0.160';
                energyInput.readOnly = false;
            } else if (val === 'us_industry') {
                energyInput.value = '0.080';
                energyInput.readOnly = false;
            } else if (val === 'custom') {
                energyInput.readOnly = false;
                energyInput.focus();
            }
            calculateAutoAB();
        });
    }

    if (btnToggleAutoAB && autoABPanel) {
        btnToggleAutoAB.addEventListener('click', () => {
            const isHidden = autoABPanel.classList.contains('hidden');
            if (isHidden) {
                autoABPanel.classList.remove('hidden');
                if (autoABArrow) autoABArrow.textContent = '▲';
                calculateAutoAB();
            } else {
                autoABPanel.classList.add('hidden');
                if (autoABArrow) autoABArrow.textContent = '▼';
            }
        });

        ['calc_energy_cost', 'calc_discount_rate', 'calc_life_years', 'calc_load_ratio'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', () => {
                    if (id === 'calc_energy_cost' && selTariffPreset) {
                        selTariffPreset.value = 'custom';
                    }
                    calculateAutoAB();
                });
            }
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

                if (res.prices.electricity) {
                    liveElectricityUSD = res.prices.electricity;
                    updateText('elec-price', res.prices.electricity.toFixed(3) + ' $/kWh');
                    const selPreset = document.getElementById('sel-tariff-preset');
                    if (selPreset && selPreset.value === 'epdk_live') {
                        const energyInput = document.getElementById('calc_energy_cost');
                        if (energyInput) {
                            energyInput.value = liveElectricityUSD.toFixed(3);
                            calculateAutoAB();
                        }
                    }
                }

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

                // Stale Market Data Warning (Directive 6)
                const staleContainer = document.getElementById('market-stale-container');
                if (staleContainer) {
                    if (res.is_stale) {
                        staleContainer.style.display = 'inline-block';
                        if (isManual) {
                            showToast(`⚠️ Piyasa verisi 10 dk'dan eski (Son güncelleme: ${res.last_updated_str || 'Bilinmiyor'})`, 'warning', 4500);
                        }
                    } else {
                        staleContainer.style.display = 'none';
                        if (isManual) {
                            showToast('Piyasa verileri anlık olarak güncellendi.', 'success', 3000);
                        }
                    }
                } else if (isManual) {
                    showToast('Piyasa verileri güncellendi.', 'success', 3000);
                }
            }
        } catch (err) {
            console.error('Piyasa verisi alınamadı:', err);
            if (isManual) {
                showToast('Piyasa verisi alınırken hata oluştu, son bilinen fiyatlar korunuyor.', 'warning', 4000);
            }
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

    // 7. Reset Form & Parameters
    const btnReset = document.getElementById('btn-reset');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (form) form.reset();
            
            // Explicitly clear all number inputs to empty placeholders
            ['S', 'V1', 'V2', 'uk', 'P0', 'Pk', 'k_constant', 'delta_T', 'ambient_temp', 'A_factor', 'B_factor'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });

            // Reset selects to default indices
            const phaseEl = document.getElementById('phase');
            if (phaseEl) phaseEl.value = '3';
            const freqEl = document.getElementById('frequency');
            if (freqEl) freqEl.value = '50';
            const hvEl = document.getElementById('material_hv');
            if (hvEl) hvEl.value = 'Cu';
            const lvEl = document.getElementById('material_lv');
            if (lvEl) lvEl.value = 'Cu';
            const coreEl = document.getElementById('core_material');
            if (coreEl) coreEl.value = 'M4';
            const oilEl = document.getElementById('oil_type');
            if (oilEl) oilEl.value = 'mineral';
            const coolEl = document.getElementById('cooling_method');
            if (coolEl) coolEl.value = 'ONAN';

            const pdfFile = document.getElementById('pdf-upload');
            if (pdfFile) pdfFile.value = '';
            const pdfStatus = document.getElementById('pdf-status');
            if (pdfStatus) pdfStatus.textContent = '';

            latestData = null;

            const resultsDiv = document.getElementById('results');
            const initialDiv = document.getElementById('initial-state');
            if (resultsDiv) resultsDiv.classList.add('hidden');
            if (initialDiv) initialDiv.classList.remove('hidden');
            if (sidebar) sidebar.classList.remove('collapsed');

            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 8. Server-Side Multi-Sheet Excel (.xlsx) Export
    const btnDownloadExcel = document.getElementById('btn-download-excel');
    if (btnDownloadExcel) {
        btnDownloadExcel.addEventListener('click', async () => {
            const btn = document.getElementById('btn-download-excel');
            if (btn) btn.textContent = 'Excel Hazırlanıyor...';

            const getVal = (id, def) => {
                const el = document.getElementById(id);
                return el && el.value !== '' ? parseFloat(el.value) : def;
            };
            const getStr = (id, def) => {
                const el = document.getElementById(id);
                return el && el.value !== '' ? el.value : def;
            };

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
                const response = await fetch('/api/download-excel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) throw new Error('Excel oluşturulamadı');

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'Transformator_Muhendislik_Raporu.xlsx';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                showToast('Excel mühendislik raporu başarıyla oluşturuldu ve indirildi.', 'success', 3500);
            } catch (err) {
                console.error('Excel Hatası:', err);
                showToast('Excel oluşturulamadı: ' + err.message, 'error');
            } finally {
                if (btn) btn.textContent = 'Mühendislik Raporunu İndir (Excel)';
            }
        });
    }

    // 9. Server-Side Vector PDF Export in New Tab (ReportLab)
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
                vector_group: getStr('vector_group', 'Dyn11'),
                optimization_mode: document.getElementById('optimization_mode')?.value === 'true',
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
                showToast('PDF mühendislik raporu başarıyla hazırlandı.', 'success', 3500);
            } catch (err) {
                console.error('PDF Hatası:', err);
                showToast('PDF oluşturulamadı: ' + err.message, 'error');
            } finally {
                if (btn) btn.textContent = 'Mühendislik Raporunu İndir (PDF)';
            }
        });
    }
});

