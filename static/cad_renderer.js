/**
 * ⚡ Hızlı Transformatör - Parametric 2D CAD Technical Blueprint Renderer
 * - +20% Magnified Scaled Silhouette (Crisp, large, fully visible)
 * - Full Tank Body Background Hitbox (Active on entire tank area, core & windings take priority)
 * - Side-By-Side Workbench Layout (Left: Scaled SVG CAD Canvas / Right: Live Component Inspector & Specs)
 * - Isolated Non-Overlapping Dimension Badges in Meters (m)
 * - Direct Native Event Listeners on All Parts (100% Cross-Browser Reliable)
 * - True-To-Life Electrical Colors (AG: Radiant Amber Gold, YG: Electric Cobalt Blue)
 */

(function(window) {
    'use strict';

    let _lastData = null;
    let _lastContainerId = null;

    function renderTransformerCAD(containerId, data) {
        if (!containerId || !data) return;
        _lastContainerId = containerId;
        _lastData = data;

        const container = document.getElementById(containerId);
        if (!container) return;

        const isDark = document.body.classList.contains('dark-mode');

        const geom = data.cad_geometry || {};
        const core = geom.core || { D_mm: 150, A_mm: 312, Hw_mm: 405, total_width_mm: 774, total_height_mm: 705, yoke_height_mm: 142, limb_centers: [-312, 0, 312] };
        const win = geom.windings || { lv: { radial_mm: 25, height_mm: 350, inner_r_mm: 87, outer_r_mm: 112 }, hv: { radial_mm: 35, height_mm: 330, inner_r_mm: 127, outer_r_mm: 162 }, duct_gap_mm: 15 };
        const tank = geom.tank || { length_mm: 914, width_mm: 444, height_mm: 865, oil_level_mm: 795, oil_volume_L: 500 };
        const el = data.electrical || {};
        const cd = data.core_design || {};

        const D_mm = core.D_mm || 150;
        const A_mm = core.A_mm || 312;
        const Hw_mm = core.Hw_mm || 405;
        const coreW_mm = core.total_width_mm || 774;
        const coreH_mm = core.total_height_mm || 705;
        const yokeH_mm = core.yoke_height_mm || (D_mm * 0.95);
        const tankL_mm = tank.length_mm || 914;
        const tankH_mm = tank.height_mm || 865;
        const tankW_mm = tank.width_mm || 450;
        const oilLevel_mm = tank.oil_level_mm || (tankH_mm * 0.9);

        // Metric strings in Meters (m)
        const mTankL = (tankL_mm / 1000).toFixed(2);
        const mTankH = (tankH_mm / 1000).toFixed(2);
        const mTankW = (tankW_mm / 1000).toFixed(2);
        const mOil = (oilLevel_mm / 1000).toFixed(2);
        const mA = (A_mm / 1000).toFixed(2);
        const mHw = (Hw_mm / 1000).toFixed(2);
        const mD = (D_mm / 1000).toFixed(2);

        // Theme Palette
        const bgCanvas = isDark ? '#090d14' : '#f8fafc';
        const gridColor = isDark ? 'rgba(56, 189, 248, 0.10)' : 'rgba(100, 116, 139, 0.14)';
        const textDimColor = isDark ? '#f1f5f9' : '#0f172a';
        const badgeBg = isDark ? '#1e293b' : '#ffffff';
        const badgeBorder = isDark ? '#475569' : '#cbd5e1';
        const tankStroke = isDark ? '#475569' : '#64748b';
        const tankBg = isDark ? '#0d131a' : '#ffffff';
        const oilFill = isDark ? 'rgba(14, 165, 233, 0.12)' : 'rgba(14, 165, 233, 0.08)';
        const oilLine = '#0284c7';
        const coreStroke = isDark ? '#1e293b' : '#334155';

        // 1. FIXED COORDINATE CANVAS: 800 x 520
        const canvasW = 800;
        const canvasH = 520;

        // Drawing target envelope inside canvas (Fills the area generously)
        const targetW = 590;
        const targetH = 405;
        const scale = Math.min(targetW / tankL_mm, targetH / tankH_mm);

        const originX = canvasW / 2; // 400
        const originY = (canvasH / 2) + (tankH_mm * scale / 2) - 6; // Bottom base of tank

        // Scaled coordinates
        const sTankL = tankL_mm * scale;
        const sTankH = tankH_mm * scale;
        const sTankLeft = originX - (sTankL / 2);
        const sTankTop = originY - sTankH;
        const sOilY = originY - (oilLevel_mm * scale);

        const sCoreW = coreW_mm * scale;
        const sCoreH = coreH_mm * scale;
        const sD = D_mm * scale;
        const sA = A_mm * scale;
        const sHw = Hw_mm * scale;
        const sYokeH = yokeH_mm * scale;

        const sCoreBottomY = originY - (24 * scale);
        const sCoreTopY = sCoreBottomY - sCoreH;
        const sWindowBottomY = sCoreBottomY - sYokeH;
        const sWindowTopY = sWindowBottomY - sHw;

        const sLimbX = [
            originX - sA,
            originX,
            originX + sA
        ];

        let svg = `
        <svg id="transformer-cad-svg" viewBox="0 0 ${canvasW} ${canvasH}" preserveAspectRatio="xMidYMid meet" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: ${bgCanvas}; border-radius: 8px; font-family: 'Inter', system-ui, sans-serif;">
            <defs>
                <!-- Steel Core Gradient -->
                <linearGradient id="coreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="${isDark ? '#334155' : '#64748b'}" />
                    <stop offset="50%" stop-color="${isDark ? '#475569' : '#94a3b8'}" />
                    <stop offset="100%" stop-color="${isDark ? '#1e293b' : '#475569'}" />
                </linearGradient>

                <!-- LV Secondary Winding: Radiant Amber Gold -->
                <linearGradient id="lvGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#d97706" />
                    <stop offset="50%" stop-color="#fde047" />
                    <stop offset="100%" stop-color="#b45309" />
                </linearGradient>

                <!-- HV Primary Winding: Electric Royal Cobalt Blue -->
                <linearGradient id="hvGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#1d4ed8" />
                    <stop offset="50%" stop-color="#60a5fa" />
                    <stop offset="100%" stop-color="#1e40af" />
                </linearGradient>
            </defs>

            <!-- 1. Technical Grid Lines -->
            <g opacity="0.6" pointer-events="none">
                <line x1="25" y1="${originY}" x2="${canvasW - 25}" y2="${originY}" stroke="${gridColor}" stroke-width="1" stroke-dasharray="6,4" />
                <line x1="${originX}" y1="15" x2="${originX}" y2="${canvasH - 15}" stroke="${gridColor}" stroke-width="1" stroke-dasharray="6,4" />
            </g>

            <!-- 2. Transformer Tank Background & Frame (ACTIVE HITBOX ON BODY) -->
            <g id="cad-part-tank" class="cad-part" data-dim-target="dim-group-tank" data-icon="🛢️" data-title="Kazan Gövdesi & Radyatörler" data-category="Mekanik Gövde" data-spec="Dış Ölçü (L×W×H): ${mTankL} × ${mTankW} × ${mTankH} m<br>Milimetrik Ölçü: ${tankL_mm.toFixed(0)} × ${tankW_mm.toFixed(0)} × ${tankH_mm.toFixed(0)} mm<br>Yağ Hacmi: ${tank.oil_volume_L} Litre<br>Çelik Et Kalınlığı: 6 mm">
                <!-- Tank Full Background Fill (Catches mouse on empty tank areas) -->
                <rect class="part-shape tank-body-rect" x="${sTankLeft}" y="${sTankTop}" width="${sTankL}" height="${sTankH}" fill="${tankBg}" stroke="${tankStroke}" stroke-width="2.5" rx="6" />
                
                <!-- Oil Fluid Layer -->
                <rect x="${sTankLeft + 2}" y="${sOilY}" width="${sTankL - 4}" height="${originY - sOilY - 2}" fill="${oilFill}" rx="3" pointer-events="none" />
                <line x1="${sTankLeft + 4}" y1="${sOilY}" x2="${sTankLeft + sTankL - 4}" y2="${sOilY}" stroke="${oilLine}" stroke-width="2" stroke-dasharray="6,4" pointer-events="none" />

                <!-- Base Beams -->
                <rect class="part-shape" x="${sTankLeft + 25}" y="${originY}" width="90" height="14" fill="${isDark ? '#334155' : '#cbd5e1'}" stroke="${tankStroke}" stroke-width="1.5" rx="3" />
                <rect class="part-shape" x="${sTankLeft + sTankL - 115}" y="${originY}" width="90" height="14" fill="${isDark ? '#334155' : '#cbd5e1'}" stroke="${tankStroke}" stroke-width="1.5" rx="3" />

                <!-- Cover Flange -->
                <rect class="part-shape" x="${sTankLeft - 10}" y="${sTankTop - 10}" width="${sTankL + 20}" height="10" fill="${isDark ? '#475569' : '#94a3b8'}" stroke="${tankStroke}" stroke-width="1.5" rx="3" />
            </g>

            <!-- 3. Magnetic Core (Top/Bottom Yokes + 3 Limbs - OVERLAYS TANK) -->
            <g id="cad-part-core" class="cad-part" data-dim-target="dim-group-core" data-icon="🧲" data-title="3 Bacaklı Silisli Manyetik Nüve" data-category="Manyetik Çekirdek" data-spec="Sac Cinsi: ${cd.core_label || 'M4 Silisli Sac (0.27mm)'}<br>Bacak Çapı: Ø ${mD} m (${D_mm.toFixed(0)} mm)<br>Eksen Aralığı: ${mA} m (${A_mm.toFixed(0)} mm)<br>Pencere Yüksekliği: ${mHw} m (${Hw_mm.toFixed(0)} mm)<br>Hesapsal Ağırlık: ${cd.core_weight_kg || '—'} kg">
                <!-- Bottom Yoke -->
                <rect class="part-shape" x="${originX - (sCoreW / 2)}" y="${sWindowBottomY}" width="${sCoreW}" height="${sYokeH}" fill="url(#coreGrad)" stroke="${coreStroke}" stroke-width="1.5" rx="3" />
                <!-- Top Yoke -->
                <rect class="part-shape" x="${originX - (sCoreW / 2)}" y="${sCoreTopY}" width="${sCoreW}" height="${sYokeH}" fill="url(#coreGrad)" stroke="${coreStroke}" stroke-width="1.5" rx="3" />
                
                <!-- 3 Vertical Limbs -->
                ${sLimbX.map((cx, idx) => `
                    <rect class="part-shape" x="${cx - (sD / 2)}" y="${sWindowTopY}" width="${sD}" height="${sHw}" fill="url(#coreGrad)" stroke="${coreStroke}" stroke-width="1.2" />
                    <line x1="${cx}" y1="${sCoreTopY - 12}" x2="${cx}" y2="${sCoreBottomY + 12}" stroke="${textDimColor}" stroke-width="1" stroke-dasharray="6,3,2,3" opacity="0.5" pointer-events="none" />
                `).join('')}
            </g>

            <!-- 4. Windings (Gold AG & Cobalt Blue YG - OVERLAYS CORE & TANK) -->
            <g id="cad-windings">
                ${sLimbX.map((cx, idx) => {
                    const sLvW = Math.max(9, win.lv.radial_mm * scale);
                    const sLvH = Math.max(22, win.lv.height_mm * scale);
                    const sLvLeftX = cx - (win.lv.outer_r_mm * scale);
                    const sLvRightX = cx + (win.lv.inner_r_mm * scale);
                    const sLvY = sWindowTopY + ((sHw - sLvH) / 2);

                    const sHvW = Math.max(13, win.hv.radial_mm * scale);
                    const sHvH = Math.max(20, win.hv.height_mm * scale);
                    const sHvLeftX = cx - (win.hv.outer_r_mm * scale);
                    const sHvRightX = cx + (win.hv.inner_r_mm * scale);
                    const sHvY = sWindowTopY + ((sHw - sHvH) / 2);

                    return `
                    <!-- Phase ${idx + 1} LV (Sekonder) Winding: GOLD -->
                    <g id="cad-part-lv-${idx+1}" class="cad-part" data-dim-target="dim-group-core" data-icon="🟡" data-title="Faz ${idx + 1} AG (Sekonder) Sargısı" data-category="Alçak Gerilim Sargısı" data-spec="Sarım Sayısı: ${win.lv.turns} Tur<br>İletken Kesiti: ${win.lv.area_mm2} mm² (${el.material_lv || 'Cu'})<br>Sargı Boyu: ${(win.lv.height_mm/1000).toFixed(2)} m (${win.lv.height_mm.toFixed(0)} mm)<br>Anma Gerilimi: ${el.V2 || '—'} V">
                        <rect class="part-shape" x="${sLvLeftX}" y="${sLvY}" width="${sLvW}" height="${sLvH}" fill="url(#lvGrad)" stroke="#854d0e" stroke-width="1.2" rx="2" />
                        <rect class="part-shape" x="${sLvRightX}" y="${sLvY}" width="${sLvW}" height="${sLvH}" fill="url(#lvGrad)" stroke="#854d0e" stroke-width="1.2" rx="2" />
                    </g>

                    <!-- Phase ${idx + 1} HV (Primer) Winding: ROYAL BLUE -->
                    <g id="cad-part-hv-${idx+1}" class="cad-part" data-dim-target="dim-group-core" data-icon="🔵" data-title="Faz ${idx + 1} YG (Primer) Sargısı" data-category="Yüksek Gerilim Sargısı" data-spec="Sarım Sayısı: ${win.hv.turns} Tur<br>İletken Kesiti: ${win.hv.area_mm2} mm² (${el.material_hv || 'Cu'})<br>Sargı Boyu: ${(win.hv.height_mm/1000).toFixed(2)} m (${win.hv.height_mm.toFixed(0)} mm)<br>Anma Gerilimi: ${el.V1 || '—'} V">
                        <rect class="part-shape" x="${sHvLeftX}" y="${sHvY}" width="${sHvW}" height="${sHvH}" fill="url(#hvGrad)" stroke="#1e3a8a" stroke-width="1.2" rx="2" />
                        <rect class="part-shape" x="${sHvRightX}" y="${sHvY}" width="${sHvH}" fill="url(#hvGrad)" stroke="#1e3a8a" stroke-width="1.2" rx="2" />
                    </g>
                    `;
                }).join('')}
            </g>

            <!-- 5. Non-Overlapping Dimension Badges in Meters (m) -->
            <g id="cad-dimensions" font-size="12" font-weight="700">
                <!-- Group: Core Dimensions -->
                <g id="dim-group-core" class="cad-dim-group">
                    <!-- Bacak Eksen Mesafesi A (Top center margin) -->
                    <line class="dim-line" x1="${sLimbX[0]}" y1="${sCoreTopY - 20}" x2="${sLimbX[1]}" y2="${sCoreTopY - 20}" stroke="#0284c7" stroke-width="1.5" />
                    <line class="dim-line" x1="${sLimbX[0]}" y1="${sCoreTopY - 28}" x2="${sLimbX[0]}" y2="${sCoreTopY - 6}" stroke="#0284c7" stroke-width="1" />
                    <line class="dim-line" x1="${sLimbX[1]}" y1="${sCoreTopY - 28}" x2="${sLimbX[1]}" y2="${sCoreTopY - 6}" stroke="#0284c7" stroke-width="1" />
                    <g class="cad-dim-badge" id="badge-dim-a">
                        <rect class="badge-box" x="${(sLimbX[0] + sLimbX[1]) / 2 - 45}" y="${sCoreTopY - 32}" width="90" height="22" rx="4" fill="${badgeBg}" stroke="${badgeBorder}" stroke-width="1.2" />
                        <text class="badge-text" x="${(sLimbX[0] + sLimbX[1]) / 2}" y="${sCoreTopY - 17}" text-anchor="middle" fill="${textDimColor}">A = ${mA} m</text>
                    </g>

                    <!-- Pencere Boyu Hw (Right side margin) -->
                    <line class="dim-line" x1="${originX + (sCoreW / 2) + 14}" y1="${sWindowTopY}" x2="${originX + (sCoreW / 2) + 14}" y2="${sWindowBottomY}" stroke="#0284c7" stroke-width="1.5" />
                    <line class="dim-line" x1="${originX + (sCoreW / 2) + 5}" y1="${sWindowTopY}" x2="${originX + (sCoreW / 2) + 23}" y2="${sWindowTopY}" stroke="#0284c7" stroke-width="1" />
                    <line class="dim-line" x1="${originX + (sCoreW / 2) + 5}" y1="${sWindowBottomY}" x2="${originX + (sCoreW / 2) + 23}" y2="${sWindowBottomY}" stroke="#0284c7" stroke-width="1" />
                    <g class="cad-dim-badge" id="badge-dim-hw">
                        <rect class="badge-box" x="${originX + (sCoreW / 2) + 20}" y="${sWindowTopY + (sHw / 2) - 12}" width="96" height="24" rx="4" fill="${badgeBg}" stroke="${badgeBorder}" stroke-width="1.2" />
                        <text class="badge-text" x="${originX + (sCoreW / 2) + 68}" y="${sWindowTopY + (sHw / 2) + 4}" text-anchor="middle" fill="${textDimColor}">Hw = ${mHw} m</text>
                    </g>

                    <!-- Bacak Çapı D (Inside lower yoke area) -->
                    <line class="dim-line" x1="${sLimbX[0] - (sD / 2)}" y1="${sWindowBottomY + (sYokeH / 2)}" x2="${sLimbX[0] + (sD / 2)}" y2="${sWindowBottomY + (sYokeH / 2)}" stroke="#0284c7" stroke-width="2" />
                    <g class="cad-dim-badge" id="badge-dim-d">
                        <rect class="badge-box" x="${sLimbX[0] - 38}" y="${sWindowBottomY + (sYokeH / 2) - 12}" width="76" height="24" rx="4" fill="${badgeBg}" stroke="#0284c7" stroke-width="1.2" />
                        <text class="badge-text" x="${sLimbX[0]}" y="${sWindowBottomY + (sYokeH / 2) + 5}" text-anchor="middle" fill="#0284c7">Ø ${mD} m</text>
                    </g>
                </g>

                <!-- Group: Tank Dimensions in Meters -->
                <g id="dim-group-tank" class="cad-dim-group">
                    <!-- Oil Level Badge (Top Right of tank) -->
                    <g class="cad-dim-badge" id="badge-oil">
                        <rect class="badge-box" x="${sTankLeft + sTankL - 145}" y="${sOilY - 22}" width="135" height="19" rx="4" fill="${badgeBg}" stroke="${oilLine}" stroke-width="1.2" />
                        <text class="badge-text" x="${sTankLeft + sTankL - 78}" y="${sOilY - 9}" fill="${oilLine}" font-size="10" text-anchor="middle">YAĞ SEVİYESİ: ${mOil} m</text>
                    </g>

                    <!-- Dış Kazan Yüksekliği H (Left side margin) -->
                    <line class="dim-line" x1="${sTankLeft - 18}" y1="${sTankTop}" x2="${sTankLeft - 18}" y2="${originY}" stroke="#0284c7" stroke-width="1.5" />
                    <line class="dim-line" x1="${sTankLeft - 26}" y1="${sTankTop}" x2="${sTankLeft - 10}" y2="${sTankTop}" stroke="#0284c7" stroke-width="1" />
                    <line class="dim-line" x1="${sTankLeft - 26}" y1="${originY}" x2="${sTankLeft - 10}" y2="${originY}" stroke="#0284c7" stroke-width="1" />
                    <g class="cad-dim-badge" id="badge-dim-tank-h">
                        <g transform="translate(${sTankLeft - 20}, ${sTankTop + (sTankH / 2)}) rotate(-90)">
                            <rect class="badge-box" x="-85" y="-12" width="170" height="24" rx="4" fill="${badgeBg}" stroke="#0284c7" stroke-width="1.2" />
                            <text class="badge-text" x="0" y="4" text-anchor="middle" fill="#0284c7">KAZAN BOYU = ${mTankH} m</text>
                        </g>
                    </g>

                    <!-- Dış Kazan Uzunluğu L (Bottom margin) -->
                    <line class="dim-line" x1="${sTankLeft}" y1="${originY + 20}" x2="${sTankLeft + sTankL}" y2="${originY + 20}" stroke="#0284c7" stroke-width="1.5" />
                    <line class="dim-line" x1="${sTankLeft}" y1="${originY + 12}" x2="${sTankLeft}" y2="${originY + 28}" stroke="#0284c7" stroke-width="1" />
                    <line class="dim-line" x1="${sTankLeft + sTankL}" y1="${originY + 12}" x2="${sTankLeft + sTankL}" y2="${originY + 28}" stroke="#0284c7" stroke-width="1" />
                    <g class="cad-dim-badge" id="badge-dim-tank-l">
                        <rect class="badge-box" x="${originX - 95}" y="${originY + 9}" width="190" height="24" rx="4" fill="${badgeBg}" stroke="#0284c7" stroke-width="1.2" />
                        <text class="badge-text" x="${originX}" y="${originY + 25}" text-anchor="middle" fill="#0284c7">KAZAN UZUNLUĞU = ${mTankL} m</text>
                    </g>
                </g>
            </g>
        </svg>
        `;

        container.innerHTML = `
            <div class="cad-viewer-wrapper">
                <div class="cad-header-bar">
                    <div class="cad-title">
                        <span class="cad-icon">📐</span>
                        <strong>1:1 Parametrik 2D Teknik Kesit Çizimi (CAD Blueprint)</strong>
                    </div>
                    <div class="cad-legend">
                        <span class="legend-item"><span class="legend-dot dot-ag"></span> <strong>AG (Sekonder)</strong></span>
                        <span class="legend-item"><span class="legend-dot dot-yg"></span> <strong>YG (Primer)</strong></span>
                        <span class="legend-item"><span class="legend-dot dot-core"></span> <strong>Nüve (Sac)</strong></span>
                        <button type="button" class="btn-cad-dl" id="btn-dl-cad-svg" title="Vektörel SVG Formatında İndir">⬇ SVG İndir</button>
                    </div>
                </div>

                <!-- SIDE-BY-SIDE CAD WORKBENCH -->
                <div class="cad-workbench-layout">
                    <!-- Left Column: Scaled SVG Drawing Canvas -->
                    <div class="cad-svg-container" id="cad-svg-holder">
                        ${svg}
                        <!-- Floating Tooltip Bubble -->
                        <div id="cad-floating-bubble" class="cad-floating-bubble">
                            <div class="bubble-header">
                                <span class="bubble-icon" id="cad-bubble-icon">⚡</span>
                                <strong id="cad-bubble-title">Parça Adı</strong>
                            </div>
                            <div class="bubble-desc" id="cad-bubble-desc">Parça bilgileri</div>
                        </div>
                    </div>

                    <!-- Right Column: Component Inspector & Dimension Sidebar -->
                    <div class="cad-sidebar-panel">
                        <!-- Active Component Inspector Card -->
                        <div class="cad-inspector-box" id="cad-inspector-box">
                            <div class="cad-inspector-header">
                                <span class="inspector-badge" id="cad-insp-cat">Parça İnceleyici</span>
                                <strong id="cad-insp-title">Üzerine Gelin: Parça Detayı</strong>
                            </div>
                            <div class="cad-inspector-desc" id="cad-insp-desc">
                                Çizimdeki nüveye, sarı AG sargısına, mavi YG sargısına veya kazana geldiğinizde detaylar burada ve çizimde canlı listelenir.
                            </div>
                        </div>

                        <!-- Metric Specifications List -->
                        <div class="cad-specs-list">
                            <div class="cad-spec-row">
                                <span class="spec-label">Nüve Bacak Çapı (D):</span>
                                <span class="spec-val">Ø ${mD} m (${D_mm.toFixed(0)} mm)</span>
                            </div>
                            <div class="cad-spec-row">
                                <span class="spec-label">Bacak Eksen Aralığı (A):</span>
                                <span class="spec-val">${mA} m (${A_mm.toFixed(0)} mm)</span>
                            </div>
                            <div class="cad-spec-row">
                                <span class="spec-label">Pencere Boyu (Hw):</span>
                                <span class="spec-val">${mHw} m (${Hw_mm.toFixed(0)} mm)</span>
                            </div>
                            <div class="cad-spec-row">
                                <span class="spec-label">Kazan Boyutları (L×W×H):</span>
                                <span class="spec-val">${mTankL} × ${mTankW} × ${mTankH} m</span>
                            </div>
                            <div class="cad-spec-row">
                                <span class="spec-label">Toplam Yağ Hacmi:</span>
                                <span class="spec-val">${tank.oil_volume_L} Litre</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Direct & 100% Cross-Browser Tooltip & SVG Visual Highlight Engine
        const svgHolder = document.getElementById('cad-svg-holder');
        const bubble = document.getElementById('cad-floating-bubble');
        const bubbleIcon = document.getElementById('cad-bubble-icon');
        const bubbleTitle = document.getElementById('cad-bubble-title');
        const bubbleDesc = document.getElementById('cad-bubble-desc');

        const inspCat = document.getElementById('cad-insp-cat');
        const inspTitle = document.getElementById('cad-insp-title');
        const inspDesc = document.getElementById('cad-insp-desc');

        const partElements = container.querySelectorAll('.cad-part');

        function clearVisualHighlights() {
            container.querySelectorAll('.cad-part .part-shape').forEach(shape => {
                shape.style.stroke = '';
                shape.style.strokeWidth = '';
                shape.style.filter = '';
            });

            container.querySelectorAll('.cad-dim-badge').forEach(b => {
                const box = b.querySelector('.badge-box');
                const txt = b.querySelector('.badge-text');
                if (box) {
                    box.style.fill = '';
                    box.style.stroke = '';
                    box.style.strokeWidth = '';
                }
                if (txt) {
                    txt.style.fill = '';
                    txt.style.fontWeight = '';
                }
            });

            container.querySelectorAll('.dim-line').forEach(l => {
                l.style.stroke = '#0284c7';
                l.style.strokeWidth = '1.5';
            });

            if (bubble) {
                bubble.style.display = 'none';
                bubble.style.opacity = '0';
            }
        }

        function highlightPart(targetPart, e) {
            clearVisualHighlights();

            // 1. Highlight Shape in SVG with native stroke and glow
            targetPart.querySelectorAll('.part-shape').forEach(shape => {
                shape.style.stroke = '#0284c7';
                shape.style.strokeWidth = '2.5px';
                shape.style.filter = 'drop-shadow(0 0 6px #0284c7)';
            });

            // 2. Highlight Associated Dimension Badges & Lines
            const dimTargetId = targetPart.getAttribute('data-dim-target');
            if (dimTargetId) {
                const dimGroup = document.getElementById(dimTargetId);
                if (dimGroup) {
                    dimGroup.querySelectorAll('.dim-line').forEach(l => {
                        l.style.stroke = '#38bdf8';
                        l.style.strokeWidth = '2.5px';
                    });
                    dimGroup.querySelectorAll('.cad-dim-badge').forEach(b => {
                        const box = b.querySelector('.badge-box');
                        const txt = b.querySelector('.badge-text');
                        if (box) {
                            box.style.fill = '#0284c7';
                            box.style.stroke = '#38bdf8';
                            box.style.strokeWidth = '2px';
                        }
                        if (txt) {
                            txt.style.fill = '#ffffff';
                            txt.style.fontWeight = '800';
                        }
                    });
                }
            }

            // 3. Update Right Sidebar Inspector
            const cat = targetPart.getAttribute('data-category') || 'Bileşen';
            const title = targetPart.getAttribute('data-title') || '';
            const spec = targetPart.getAttribute('data-spec') || '';
            const icon = targetPart.getAttribute('data-icon') || '⚡';

            if (inspCat) inspCat.textContent = cat;
            if (inspTitle) inspTitle.textContent = title;
            if (inspDesc) inspDesc.innerHTML = spec;

            // 4. Update Floating Tooltip Bubble
            if (bubble) {
                bubbleIcon.textContent = icon;
                bubbleTitle.textContent = title;
                bubbleDesc.innerHTML = spec;
                bubble.style.display = 'block';
                bubble.style.opacity = '1';

                if (svgHolder && e) {
                    const rect = svgHolder.getBoundingClientRect();
                    let posX = e.clientX - rect.left + 15;
                    let posY = e.clientY - rect.top + 15;

                    if (posX + 260 > rect.width) {
                        posX = e.clientX - rect.left - 270;
                    }
                    if (posY + 80 > rect.height) {
                        posY = e.clientY - rect.top - 85;
                    }
                    if (posY < 10) posY = 10;

                    bubble.style.left = `${Math.round(posX)}px`;
                    bubble.style.top = `${Math.round(posY)}px`;
                }
            }
        }

        // Direct event listener binding to each part
        partElements.forEach(part => {
            part.addEventListener('pointerenter', (e) => highlightPart(part, e));
            part.addEventListener('pointermove', (e) => {
                if (bubble && svgHolder) {
                    const rect = svgHolder.getBoundingClientRect();
                    let posX = e.clientX - rect.left + 15;
                    let posY = e.clientY - rect.top + 15;

                    if (posX + 260 > rect.width) {
                        posX = e.clientX - rect.left - 270;
                    }
                    if (posY + 80 > rect.height) {
                        posY = e.clientY - rect.top - 85;
                    }
                    if (posY < 10) posY = 10;

                    bubble.style.left = `${Math.round(posX)}px`;
                    bubble.style.top = `${Math.round(posY)}px`;
                }
            });
            part.addEventListener('pointerleave', () => clearVisualHighlights());
        });

        // Download SVG Handler
        const btnDl = document.getElementById('btn-dl-cad-svg');
        if (btnDl) {
            btnDl.addEventListener('click', () => {
                const svgEl = document.getElementById('transformer-cad-svg');
                if (!svgEl) return;
                const svgData = new XMLSerializer().serializeToString(svgEl);
                const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Trafo_2D_Teknik_Kesit_${data.electrical?.S_kVA || '800'}kVA.svg`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            });
        }
    }

    // Theme observer: re-render CAD when user switches light/dark mode
    function refreshOnThemeChange() {
        if (_lastContainerId && _lastData) {
            renderTransformerCAD(_lastContainerId, _lastData);
        }
    }

    window.renderTransformerCAD = renderTransformerCAD;
    window.refreshCADTheme = refreshOnThemeChange;

})(window);
