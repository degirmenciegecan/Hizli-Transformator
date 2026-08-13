// Add variable to store latest data for tooltips
let latestData = null;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calc-form');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const initialDiv = document.getElementById('initial-state');
    const sidebar = document.querySelector('.sidebar');
    const parallaxContent = document.getElementById('parallax-content');

    // Fetch live prices on load
    fetch('/api/prices')
        .then(response => response.json())
        .then(res => {
            if (res.success) {
                document.getElementById('cu-price').textContent = res.prices.copper + ' $/kg';
                document.getElementById('al-price').textContent = res.prices.aluminum + ' $/kg';
                if (res.sources.copper) document.getElementById('cu-source').href = res.sources.copper;
                if (res.sources.aluminum) document.getElementById('al-source').href = res.sources.aluminum;
            }
        })
        .catch(console.error);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI State update
        initialDiv.classList.add('hidden');
        resultsDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');

        // Gather form data safely handling empty inputs
        const data = {
            S: document.getElementById('S').value ? parseFloat(document.getElementById('S').value) : null,
            V1: document.getElementById('V1').value ? parseFloat(document.getElementById('V1').value) : null,
            V2: document.getElementById('V2').value ? parseFloat(document.getElementById('V2').value) : null,
            phase: parseInt(document.getElementById('phase').value),
            frequency: document.getElementById('frequency').value ? parseFloat(document.getElementById('frequency').value) : 50.0,
            uk: document.getElementById('uk').value ? parseFloat(document.getElementById('uk').value) : null,
            P0: document.getElementById('P0').value ? parseFloat(document.getElementById('P0').value) : null,
            Pk: document.getElementById('Pk').value ? parseFloat(document.getElementById('Pk').value) : null,
            oil_type: document.getElementById('oil_type').value,
            k_constant: parseFloat(document.getElementById('k_constant').value),
            delta_T: parseFloat(document.getElementById('delta_T').value),
            material_hv: document.getElementById('material_hv').value,
            material_lv: document.getElementById('material_lv').value
        };

        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const res = await response.json();

            if (res.success) {
                // Store globally for tooltips
                latestData = { req: data, res: res };

                // Populate visual diagram initial values
                document.getElementById('vis-v1').textContent = data.V1 + " V";
                document.getElementById('vis-v2').textContent = data.V2 + " V";
                
                const oilSelect = document.getElementById('oil_type');
                const oilTypeName = oilSelect.options[oilSelect.selectedIndex].text.split(' (')[0];
                document.getElementById('vis-oil-type').textContent = oilTypeName;
                
                document.getElementById('vis-oil-weight').textContent = Math.round(res.thermo.oil_weight_kg) + " Kg";

                // Dynamic Width and Color based on Material
                const leftCoil = document.querySelector('.left-coil');
                const rightCoil = document.querySelector('.right-coil');
                
                // HV (Primary / Left)
                if (data.material_hv === 'Al') {
                    leftCoil.style.width = '65px';
                    leftCoil.style.backgroundColor = '#b0bec5'; // Aluminum color
                    leftCoil.querySelectorAll('.mech-wire-out').forEach(w => w.style.backgroundColor = '#b0bec5');
                } else {
                    leftCoil.style.width = '50px';
                    leftCoil.style.backgroundColor = '#f26d21'; // Copper color
                    leftCoil.querySelectorAll('.mech-wire-out').forEach(w => w.style.backgroundColor = '#f26d21');
                }
                
                // LV (Secondary / Right)
                if (data.material_lv === 'Al') {
                    rightCoil.style.width = '65px';
                    rightCoil.style.backgroundColor = '#b0bec5'; // Aluminum color
                    rightCoil.querySelectorAll('.mech-wire-out').forEach(w => w.style.backgroundColor = '#b0bec5');
                } else {
                    rightCoil.style.width = '50px';
                    rightCoil.style.backgroundColor = '#f26d21'; // Copper color
                    rightCoil.querySelectorAll('.mech-wire-out').forEach(w => w.style.backgroundColor = '#f26d21');
                }

                // Populate electrical results
                document.getElementById('res-I1').textContent = res.electrical.I1;
                document.getElementById('res-I2').textContent = res.electrical.I2;
                document.getElementById('res-a').textContent = res.electrical.a;
                document.getElementById('res-Vk').textContent = res.electrical.Vk;
                document.getElementById('res-Zk').textContent = res.electrical.Zk;
                document.getElementById('res-Lk').textContent = res.electrical.Lk_mH;
                document.getElementById('res-eff').textContent = res.electrical.efficiency;



                // Update live prices in header
                document.getElementById('cu-price').textContent = res.cost.prices.copper + ' $/kg';
                document.getElementById('al-price').textContent = res.cost.prices.aluminum + ' $/kg';
                
                if (res.cost.sources.copper) {
                    document.getElementById('cu-source').href = res.cost.sources.copper;
                }
                if (res.cost.sources.aluminum) {
                    document.getElementById('al-source').href = res.cost.sources.aluminum;
                }

                // Populate costs
                document.getElementById('cost-title-hv').textContent = 'Primer Sargı (' + (res.cost.materials.hv === 'Cu' ? 'Bakır' : 'Alüminyum') + ')';
                document.getElementById('res-hv-weight').textContent = res.cost.weights.hv;
                
                document.getElementById('cost-title-lv').textContent = 'Sekonder Sargı (' + (res.cost.materials.lv === 'Cu' ? 'Bakır' : 'Alüminyum') + ')';
                document.getElementById('res-lv-weight').textContent = res.cost.weights.lv;
                
                document.getElementById('res-total-weight').textContent = res.cost.weights.total;

                // Populate Mfg
                document.getElementById('mfg-title-hv').textContent = 'Primer Sargı (' + (res.cost.materials.hv === 'Cu' ? 'Bakır' : 'Alüminyum') + ')';
                document.getElementById('res-hv-turns').textContent = res.electrical.N1;
                document.getElementById('res-hv-area').textContent = res.electrical.A1;
                
                document.getElementById('mfg-title-lv').textContent = 'Sekonder Sargı (' + (res.cost.materials.lv === 'Cu' ? 'Bakır' : 'Alüminyum') + ')';
                document.getElementById('res-lv-turns').textContent = res.electrical.N2;
                document.getElementById('res-lv-area').textContent = res.electrical.A2;
                
                document.getElementById('res-et-val').textContent = res.electrical.Et;
                document.getElementById('res-dry-weight').textContent = res.cost.weights.dry;
                document.getElementById('res-wet-weight').textContent = res.cost.weights.wet;
                
                // Populate Thermo
                document.getElementById('res-total-heat').textContent = res.thermo.total_heat_loss;
                document.getElementById('res-cooling-area').textContent = res.thermo.cooling_area_m2;
                document.getElementById('res-oil-vol').textContent = res.thermo.oil_volume_L;
                document.getElementById('res-exp-vol').textContent = res.thermo.expansion_volume_L;
                document.getElementById('res-oil-den').textContent = res.thermo.oil_density;
                document.getElementById('res-oil-beta').textContent = res.thermo.expansion_coeff;

                // Auto hide sidebar on mobile/smaller screens, or just close it to show results better
                document.querySelector('.sidebar').classList.add('collapsed');

                // Format money nicely for cost results
                const moneyFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
                document.getElementById('res-hv-cost').textContent = moneyFormatter.format(res.cost.total.hv);
                document.getElementById('res-lv-cost').textContent = moneyFormatter.format(res.cost.total.lv);
                document.getElementById('res-total-cost').textContent = moneyFormatter.format(res.cost.total.total_cost);

                // --- POPULATE HIDDEN PDF TEMPLATE ---
                document.getElementById('pdf-I1').textContent = res.electrical.I1 + ' A';
                document.getElementById('pdf-I2').textContent = res.electrical.I2 + ' A';
                document.getElementById('pdf-a').textContent = res.electrical.a;
                document.getElementById('pdf-Vk').textContent = res.electrical.Vk + ' V';
                document.getElementById('pdf-Zk').textContent = res.electrical.Zk + ' Ω';
                document.getElementById('pdf-Lk').textContent = res.electrical.Lk + ' mH';
                document.getElementById('pdf-eff').textContent = res.electrical.efficiency_percent + ' %';

                document.getElementById('pdf-hv-turns').textContent = res.electrical.N1;
                document.getElementById('pdf-hv-area').textContent = res.electrical.Ahv;
                document.getElementById('pdf-lv-turns').textContent = res.electrical.N2;
                document.getElementById('pdf-lv-area').textContent = res.electrical.Alv;
                document.getElementById('pdf-et-val').textContent = res.electrical.Et;
                document.getElementById('pdf-dry-weight').textContent = res.cost.weights.dry;
                document.getElementById('pdf-wet-weight').textContent = res.cost.weights.wet;

                document.getElementById('pdf-total-heat').textContent = res.thermo.total_heat_loss + ' W';
                document.getElementById('pdf-cooling-area').textContent = res.thermo.cooling_area_m2 + ' m²';
                document.getElementById('pdf-oil-vol').textContent = res.thermo.oil_volume_L + ' Litre';
                document.getElementById('pdf-exp-vol').textContent = '+' + res.thermo.expansion_volume_L + ' Litre';
                document.getElementById('pdf-oil-den').textContent = res.thermo.oil_density + ' g/cm³';
                document.getElementById('pdf-oil-beta').textContent = res.thermo.expansion_coeff;

                document.getElementById('pdf-hv-weight').textContent = res.cost.weights.hv + ' kg';
                document.getElementById('pdf-lv-weight').textContent = res.cost.weights.lv + ' kg';
                document.getElementById('pdf-total-weight').textContent = res.cost.weights.total_conductor + ' kg';
                
                document.getElementById('pdf-hv-cost').textContent = moneyFormatter.format(res.cost.total.hv);
                document.getElementById('pdf-lv-cost').textContent = moneyFormatter.format(res.cost.total.lv);
                document.getElementById('pdf-total-cost').textContent = moneyFormatter.format(res.cost.total.total_cost);

                // Show results
                loadingDiv.classList.add('hidden');
                resultsDiv.classList.remove('hidden');
            } else {
                alert('Hesaplama sırasında hata oluştu: ' + res.error);
                loadingDiv.classList.add('hidden');
                initialDiv.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Sunucuya bağlanılamadı. Flask uygulamasının arka planda çalıştığından emin olun.');
            loadingDiv.classList.add('hidden');
            initialDiv.classList.remove('hidden');
        }
    });
    
    // PDF Upload logic
    const pdfUpload = document.getElementById('pdf_upload');
    const pdfStatus = document.getElementById('pdf-status');
    
    if (pdfUpload) {
        pdfUpload.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            pdfStatus.textContent = 'PDF analiz ediliyor...';
            pdfStatus.style.color = '#f26d21';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/parse-pdf', {
                    method: 'POST',
                    body: formData
                });
                
                const res = await response.json();
                
                if (res.success) {
                    // Update fields, clear if missing to indicate lack of data from PDF
                    document.getElementById('S').value = res.data.S || '';
                    document.getElementById('V1').value = res.data.V1 || '';
                    document.getElementById('V2').value = res.data.V2 || '';
                    if (res.data.phase) document.getElementById('phase').value = res.data.phase;
                    if (res.data.frequency) document.getElementById('frequency').value = res.data.frequency;
                    document.getElementById('uk').value = res.data.uk || '';
                    document.getElementById('P0').value = res.data.P0 || '';
                    document.getElementById('Pk').value = res.data.Pk || '';
                    
                    if (res.data.material_hv) document.getElementById('material_hv').value = res.data.material_hv;
                    if (res.data.material_lv) document.getElementById('material_lv').value = res.data.material_lv;
                    
                    pdfStatus.textContent = '✅ Şartname başarıyla ayrıştırıldı. Hesaplama yapılıyor...';
                    pdfStatus.style.color = '#38a169';
                    
                    // Auto submit form
                    setTimeout(() => {
                        document.getElementById('btn-calc').click();
                    }, 500);
                    
                } else {
                    pdfStatus.textContent = '❌ Hata: ' + res.error;
                    pdfStatus.style.color = '#e53e3e';
                }
            } catch (error) {
                console.error('Error:', error);
                pdfStatus.textContent = '❌ Sunucu hatası.';
                pdfStatus.style.color = '#e53e3e';
            }
        });
    }

    // PDF Download logic - using native robust print
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    if (btnDownloadPdf) {
        btnDownloadPdf.addEventListener('click', () => {
            window.print();
        });
    }

    // Reset button logic
    const btnReset = document.getElementById('btn-reset');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            document.getElementById('results').classList.add('hidden');
            document.getElementById('initial-state').classList.remove('hidden');
            
            // Open sidebar if it was collapsed
            const sidebarEl = document.querySelector('.sidebar');
            if (sidebarEl) sidebarEl.classList.remove('collapsed');
        });
    }

    // Tooltip logic
    const tooltip = document.getElementById('diagram-tooltip');
    const leftCoil = document.querySelector('.left-coil');
    const rightCoil = document.querySelector('.right-coil');
    const mechTank = document.querySelector('.mechanical-tank-container');
    
    // Sidebar Toggle Logic
    const toggleBtn = document.getElementById('toggle-sidebar');
    if(toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            document.querySelector('.sidebar').classList.toggle('collapsed');
        });
    }

    function showTooltip(e, type) {
        if (!latestData) return;
        
        // Tooltip div might not exist if it was removed from HTML by accident. Let's make sure it exists.
        let tt = document.getElementById('diagram-tooltip');
        if (!tt) {
            tt = document.createElement('div');
            tt.id = 'diagram-tooltip';
            tt.className = 'diagram-tooltip hidden';
            document.body.appendChild(tt);
        }
        
        let html = '';
        const {req, res} = latestData;
        
        if (type === 'hv') {
            html = `<h4>Primer Tarafı (H.V)</h4>
                    <ul>
                        <li><span>İletken Ağırlığı:</span> <strong>${res.cost.weights.hv} Kg</strong></li>
                        <li><span>Sarım Sayısı (N1):</span> <strong>${res.electrical.N1} Tur</strong></li>
                        <li><span>Kesit Alanı:</span> <strong>${res.electrical.A1} mm²</strong></li>
                    </ul>`;
        } else if (type === 'lv') {
            html = `<h4>Sekonder Tarafı (L.V)</h4>
                    <ul>
                        <li><span>İletken Ağırlığı:</span> <strong>${res.cost.weights.lv} Kg</strong></li>
                        <li><span>Sarım Sayısı (N2):</span> <strong>${res.electrical.N2} Tur</strong></li>
                        <li><span>Kesit Alanı:</span> <strong>${res.electrical.A2} mm²</strong></li>
                    </ul>`;
        } else if (type === 'core') {
            html = `<h4>Trafo Genel Analizi</h4>
                    <ul>
                        <li><span>Görünür Güç:</span> <strong>${req.S} VA</strong></li>
                        <li><span>Volt/Tur (Et):</span> <strong>${res.electrical.Et} V/Tur</strong></li>
                        <li><span>Boşta Kayıp (P0):</span> <strong>${req.P0} W</strong></li>
                        <li><span>Kısa Devre (Pk):</span> <strong>${req.Pk} W</strong></li>
                        <li><span>Isı Üretimi:</span> <strong>${res.thermo.total_heat_loss} W</strong></li>
                        <li><span>Önerilen Yağ:</span> <strong>${res.thermo.oil_volume_L} Litre</strong></li>
                    </ul>`;
        }
        
        tt.innerHTML = html;
        tt.classList.add('visible');
        
        const rect = e.currentTarget.getBoundingClientRect();
        
        tt.style.left = (rect.left + (rect.width/2) - 100) + 'px';
        tt.style.top = (rect.top - tt.offsetHeight - 15) + 'px';
    }

    function hideTooltip() {
        const tt = document.getElementById('diagram-tooltip');
        if(tt) tt.classList.remove('visible');
    }

    if (leftCoil) {
        leftCoil.addEventListener('mouseenter', (e) => showTooltip(e, 'hv'));
        leftCoil.addEventListener('mouseleave', hideTooltip);
    }
    
    if (rightCoil) {
        rightCoil.addEventListener('mouseenter', (e) => showTooltip(e, 'lv'));
        rightCoil.addEventListener('mouseleave', hideTooltip);
    }
    
    if (mechTank) {
        // Just as an example, double clicking or hovering empty space could show core stats
        // We'll bind it to the flatbars instead
        const topFlatbar = document.querySelector('.mech-flatbar.top');
        if (topFlatbar) {
            topFlatbar.addEventListener('mouseenter', (e) => showTooltip(e, 'core'));
            topFlatbar.addEventListener('mouseleave', hideTooltip);
        }
    }
});
