// EV4 Sistema IA - JavaScript

let currentTab = 'dashboard';

function showTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    loadTabContent(tab);
}

function showDbTab(tabName) {
    // Update tabs
    document.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`tab-btn-${tabName}`).classList.add('active');

    // Update content
    document.querySelectorAll('.db-view').forEach(v => v.style.display = 'none');
    document.getElementById(`view-${tabName}`).style.display = 'block';
}

function showWebTab(tabName) {
    document.querySelectorAll('.sub-tab-web').forEach(t => t.classList.remove('active'));
    document.getElementById(`wtab-${tabName}`).classList.add('active');

    document.getElementById('web-controls').style.display = tabName === 'controls' ? 'block' : 'none';
    document.getElementById('web-data').style.display = tabName === 'data' ? 'block' : 'none';

    if (tabName === 'data') loadKnowledgeData();
}

async function loadTabContent(tab) {
    const content = document.getElementById('content');
    content.innerHTML = '<div class="loading">Cargando...</div>';

    try {
        if (tab === 'dashboard') await loadDashboard();
        else if (tab === 'db') await loadDatabase();
        else if (tab === 'ia') await loadVisualizer(); // Redirect IA Control to Visualizer
        else if (tab === 'settings') await loadSettings();
    } catch (error) {
        content.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function loadDashboard() {
    const [stats, analytics] = await Promise.all([
        fetch('/api/ia-dashboard/estadisticas/').then(r => r.json()),
        fetch('/api/analytics/resumen_general/').then(r => r.json())
    ]);

    const html = `
        <div class="dashboard-header">
            <div class="stat-card">
                <h3>Total Equipos</h3>
                <div class="stat-value">${analytics.equipos?.total || 0}</div>
                <div class="stat-trend trend-down">${analytics.equipos?.criticos || 0} críticos</div>
            </div>
            <div class="stat-card">
                <h3>Mantenimientos</h3>
                <div class="stat-value">${analytics.mantenimientos?.total || 0}</div>
                <div class="stat-trend trend-up">${analytics.mantenimientos?.pendientes || 0} pendientes</div>
            </div>
            <div class="stat-card">
                <h3>Eficacia IA</h3>
                <div class="stat-value">${((analytics.ia?.precision_promedio || 0) * 100).toFixed(1)}%</div>
                <div class="stat-trend trend-up">+${analytics.ia?.aprendizajes || 0} este mes</div>
            </div>
        </div>

        <div class="charts-container">
            <div class="chart-box">
                <h4>Estado de Equipos / Mantenimientos</h4>
                <canvas id="chartEquipos"></canvas>
            </div>
            <div class="chart-box">
                <h4>Distribución de Recursos</h4>
                <canvas id="chartRecursos"></canvas>
            </div>
        </div>

        <div class="recommendations-box">
            <h4>Recomendaciones Recientes IA</h4>
            <div id="rec-list" class="rec-list">
                <!-- Se llenará dinámicamente -->
                <div class="loading-mini">Cargando recomendaciones...</div>
            </div>
        </div>
    `;

    document.getElementById('content').innerHTML = html;

    // Render Charts
    renderCharts(analytics);
    // Load recommendations separately
    loadRecentRecommendations();
}

async function renderCharts(data) {
    const ctx1 = document.getElementById('chartEquipos');
    if (ctx1) {
        new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: ['Equipos Totales', 'Críticos', 'Mantenimientos', 'Pendientes', 'Completados'],
                datasets: [{
                    label: 'Métricas Generales',
                    data: [
                        data.equipos?.total || 0,
                        data.equipos?.criticos || 0,
                        data.mantenimientos?.total || 0,
                        data.mantenimientos?.pendientes || 0,
                        data.mantenimientos?.completados || 0
                    ],
                    backgroundColor: [
                        '#36a2eb', '#ff6384', '#ffcd56', '#ff9f40', '#4bc0c0'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Second chart: Recursos or IA Trends
    const ctx2 = document.getElementById('chartRecursos');
    if (ctx2) {
        // Fetch recursos stats if possible or use dummy distribution
        // For now using IA stats visualization
        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Aprendizajes', 'Web Learning', 'Estados', 'Acciones'],
                datasets: [{
                    data: [
                        data.ia?.aprendizajes || 10,
                        data.ia?.conocimiento_web || 5,
                        data.ia?.estados_explorados || 20,
                        data.ia?.acciones_tomadas || 15
                    ],
                    backgroundColor: [
                        '#4bc0c0', '#9966ff', '#ff9f40', '#36a2eb'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

async function loadRecentRecommendations() {
    try {
        const res = await fetch('/api/v2/recomendaciones/');
        const recs = await res.json();
        const container = document.getElementById('rec-list');

        if (!recs || recs.results?.length === 0) {
            container.innerHTML = '<div class="empty-state">No hay recomendaciones activas. Use "IA Control" -> "Generar Recomendaciones".</div>';
            return;
        }

        const listHtml = recs.results?.slice(0, 5).map(r => `
            <div class="rec-item priority-${(r.prioridad || 1).toString()}">
                <div class="rec-header">
                    <span class="rec-type">${r.tipo || 'General'}</span>
                    <span class="rec-conf">${(r.confianza * 100).toFixed(0)}% Confianza</span>
                </div>
                <h5>${r.titulo}</h5>
                <p>${r.descripcion}</p>
                <div class="rec-action">Sugerencia: ${r.accion_sugerida}</div>
            </div>
        `).join('');

        container.innerHTML = listHtml;
    } catch {
        document.getElementById('rec-list').innerHTML = '<div class="error-text">Error cargando recomendaciones</div>';
    }
}

async function loadDatabase() {
    const [equipos, mantenimientos, recursos, eventos] = await Promise.all([
        fetch('/api/equipos/').then(r => r.json()),
        fetch('/api/mantenimientos/').then(r => r.json()),
        fetch('/api/recursos/').then(r => r.json()),
        fetch('/api/eventos/').then(r => r.json())
    ]);

    const html = `
        <h2 class="section-title">Visor de Base de Datos</h2>
        
        <div class="sub-tabs">
            <button id="tab-btn-equipos" class="sub-tab active" onclick="showDbTab('equipos')">Equipos (${equipos.length})</button>
            <button id="tab-btn-mantenimientos" class="sub-tab" onclick="showDbTab('mantenimientos')">Mantenimientos (${mantenimientos.length})</button>
            <button id="tab-btn-recursos" class="sub-tab" onclick="showDbTab('recursos')">Recursos (${recursos.length})</button>
            <button id="tab-btn-eventos" class="sub-tab" onclick="showDbTab('eventos')">Eventos (${eventos.length})</button>
        </div>

        <div id="view-equipos" class="db-view">
            <div class="table-container">
                <table class="table-compact">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre</th>
                            <th>Empresa</th>
                            <th>Categoría</th>
                            <th>Estado</th>
                            <th>Ubicación</th>
                            <th>Instalación</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${equipos.slice(0, 100).map(eq => `
                            <tr>
                                <td>${eq.id}</td>
                                <td><strong>${eq.nombre}</strong></td>
                                <td>${eq.empresa_nombre}</td>
                                <td>${eq.categoria_display || eq.categoria}</td>
                                <td><span class="badge badge-success">${eq.estado}</span></td>
                                <td>${eq.ubicacion}</td>
                                <td>${new Date(eq.fecha_instalacion).toLocaleDateString()}</td>
                            </tr>
                        `).join('') || '<tr><td colspan="7" style="text-align: center; padding: 20px;">Sin datos</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="view-mantenimientos" class="db-view" style="display: none;">
            <div class="table-container">
                <table class="table-compact">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Equipo</th>
                            <th>Tipo</th>
                            <th>Prioridad</th>
                            <th>Estado</th>
                            <th>Costo</th>
                            <th>Programada</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${mantenimientos.slice(0, 100).map(m => {
        const badgeClass = m.prioridad > 70 ? 'badge-error' : m.prioridad > 40 ? 'badge-warning' : 'badge-success';
        return `
                                <tr>
                                    <td>${m.id}</td>
                                    <td>${m.equipo}</td>
                                    <td>${m.tipo}</td>
                                    <td><span class="badge ${badgeClass}">${m.prioridad}</span></td>
                                    <td>${m.estado}</td>
                                    <td>$${parseFloat(m.costo || 0).toFixed(2)}</td>
                                    <td>${new Date(m.fecha_programada).toLocaleDateString()}</td>
                                </tr>
                            `;
    }).join('') || '<tr><td colspan="7" style="text-align: center; padding: 20px;">Sin datos</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="view-recursos" class="db-view" style="display: none;">
            <div class="table-container">
                <table class="table-compact">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tipo</th>
                            <th>Nombre</th>
                            <th>Stock</th>
                            <th>Min</th>
                            <th>Costo Inv.</th>
                            <th>Disponible</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${recursos.slice(0, 100).map(r => `
                            <tr>
                                <td>${r.id}</td>
                                <td>${r.tipo}</td>
                                <td><strong>${r.nombre}</strong></td>
                                <td>${r.stock || '-'}</td>
                                <td>${r.stock_minimo || '-'}</td>
                                <td>${r.costo ? '$' + r.costo : '-'}</td>
                                <td>${r.disponible ? 'Si' : 'No'}</td>
                            </tr>
                        `).join('') || '<tr><td colspan="7" style="text-align: center; padding: 20px;">Sin datos</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="view-eventos" class="db-view" style="display: none;">
            <div class="table-container">
                <table class="table-compact">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tipo</th>
                            <th>Equipo</th>
                            <th>Severidad</th>
                            <th>Descripción</th>
                            <th>Resuelto</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${eventos.slice(0, 100).map(e => `
                            <tr>
                                <td>${e.id}</td>
                                <td>${e.tipo}</td>
                                <td>${e.equipo || '-'}</td>
                                <td><span class="badge ${e.severidad > 7 ? 'badge-error' : 'badge-warning'}">${e.severidad}</span></td>
                                <td>${e.descripcion?.substring(0, 80)}...</td>
                                <td>${e.resuelto ? 'Si' : 'No'}</td>
                            </tr>
                        `).join('') || '<tr><td colspan="6" style="text-align: center; padding: 20px;">Sin datos</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    document.getElementById('content').innerHTML = html;
}

async function loadIAControl() {
    const [stats, metricas] = await Promise.all([
        fetch('/api/sistema/estadisticas/').then(r => r.json()),
        fetch('/api/analytics/metricas_ml/').then(r => r.json()).catch(() => ({ sistema: {}, metricas: {} }))
    ]);

    const rustStatus = stats.estadisticas?.rust_habilitado;

    const html = `
        <h2 class="section-title">Control de Sistema IA</h2>
        
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Generación Total</div>
                <div class="card-value">${stats.estadisticas?.total_acciones || 0}</div>
                <div class="card-subtitle">Acciones simuladas</div>
            </div>
            <div class="card">
                <div class="card-title">Conocimiento Web</div>
                <div class="card-value">${data.total || 0}</div>
                <div class="card-subtitle">Fuentes de aprendizaje</div>
            </div>
        </div>

        <h3 class="section-title">Generación de Datos & Entrenamiento</h3>
        <div class="ia-controls">
            <div class="control-group" style="width:100%; border:1px solid #333; padding:15px; border-radius:8px;">
                <h4 style="margin-top:0;">1. Configurar Generación</h4>
                <p style="color:#888; font-size:0.9rem; margin-bottom:10px;">
                    La IA generará equipos y mantenimientos basados en el conocimiento adquirido.
                </p>
                <div style="display:flex; gap:10px; align-items:center;">
                    <button class="control-btn" onclick="previewDataGeneration(10)">Vista Previa (10)</button>
                    <button class="control-btn" onclick="previewDataGeneration(50)">Vista Previa (50)</button>
                    <button class="tab" onclick="loadIAControl()">Control de IA</button>
            <button class="tab" onclick="loadDatabase()">Base de Datos</button>
            <button class="tab" onclick="loadSettings()">Configuración</button>
        </div>        </div>
            </div>
        </div>

        <!-- Preview Modal Container -->
        <div id="preview-modal" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); 
                                      background:#1e1e1e; padding:20px; border:1px solid #444; z-index:1000; 
                                      width:80%; max-height:80vh; overflow-y:auto; box-shadow:0 0 20px rgba(0,0,0,0.8);">
            <h3>Vista Previa de Datos Generados</h3>
            <div id="preview-content"></div>
            <div style="margin-top:20px; text-align:right;">
                <button class="btn danger" onclick="document.getElementById('preview-modal').style.display='none'">Cancelar</button>
                <button class="btn btn-primary" onclick="confirmDataGeneration()">Confirmar e Insertar en BD</button>
            </div>
        </div>



        </div>
    `;

    document.getElementById('content').innerHTML = html;
}

async function loadAnalytics() {
    const [criticos, conocimiento, predicciones] = await Promise.all([
        fetch('/api/analytics/equipos_criticos/').then(r => r.json()),
        fetch('/api/analytics/conocimiento_web/').then(r => r.json()),
        fetch('/api/analytics/predicciones_ia/').then(r => r.json())
    ]);

    const html = `
        <h2 class="section-title">Analytics y Consultas</h2>
        
        <div class="table-container">
            <div class="table-header">
                <h3>Equipos Críticos con Mantenimientos Pendientes</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Equipo</th>
                        <th>Empresa</th>
                        <th>Pendientes</th>
                        <th>Prioridad Promedio</th>
                    </tr>
                </thead>
                <tbody>
                    ${criticos.equipos?.slice(0, 10).map(eq => `
                        <tr>
                            <td>${eq.nombre}</td>
                            <td>${eq.empresa}</td>
                            <td><span class="badge badge-warning">${eq.mantenimientos_pendientes}</span></td>
                            <td>${eq.prioridad_maxima.toFixed(1)}</td>
                        </tr>
                    `).join('') || '<tr><td colspan="4" style="text-align: center; padding: 40px;">No hay equipos críticos</td></tr>'}
                </tbody>
            </table>
        </div>
    `;

    document.getElementById('content').innerHTML = html;
}

async function loadKnowledgeData() {
    try {
        const res = await fetch('/api/analytics/conocimiento_list/');
        const data = await res.json();

        const tbody = document.getElementById('knowledge-table-body');
        if (!tbody) return;

        tbody.innerHTML = data.map(item => `
            <tr>
                <td><input type="checkbox" class="k-check" value="${item.id}"></td>
                <td><strong>${item.titulo}</strong></td>
                <td><a href="${item.fuente}" target="_blank" style="color:#4bc0c0;">Enlace</a></td>
                <td>${new Date(item.fecha).toLocaleString()}</td>
                <td>${item.resumen}</td>
            </tr>
        `).join('') || '<tr><td colspan="5" style="text-align:center;">Sin datos recopilados</td></tr>';
    } catch (e) {
        console.error(e);
    }
}

// Global variable to store preview quantity
let pendingGenerationQty = 0;

async function previewDataGeneration(qty) {
    pendingGenerationQty = qty;
    const modal = document.getElementById('preview-modal');
    const content = document.getElementById('preview-content');

    content.innerHTML = '<div class="loading">Generando simulación...</div>';
    modal.style.display = 'block';

    try {
        const res = await fetch('/api/sistema/generar_datos_prueba/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cantidad: qty, preview: true })
        });
        const data = await res.json();

        let html = '<table class="table-compact"><thead><tr><th>Equipo</th><th>Mantenimiento (IA Generated)</th><th>Costo Est.</th></tr></thead><tbody>';
        data.mantenimientos.slice(0, 10).forEach(m => {
            html += `<tr>
                <td>${m.equipo}</td>
                <td>${m.descripcion}</td>
                <td>$${m.costo.toFixed(2)}</td>
            </tr>`;
        });
        html += '</tbody></table>';

        if (data.mantenimientos.length > 10) {
            html += `<p style="text-align:center; color:#888;">... y ${data.mantenimientos.length - 10} más</p>`;
        }

        content.innerHTML = html;

    } catch (e) {
        content.innerHTML = `<div class="error-text">Error: ${e.message}</div>`;
    }
}

async function confirmDataGeneration() {
    if (!pendingGenerationQty) return;
    const modal = document.getElementById('preview-modal');
    modal.style.display = 'none';
    generarDatos(pendingGenerationQty); // Calls the original function which saves
}

async function deleteSelectedKnowledge() {
    const selected = Array.from(document.querySelectorAll('.k-check:checked')).map(cb => cb.value);
    if (selected.length === 0) return alert("Seleccione items para eliminar");

    if (confirm(`¿Eliminar ${selected.length} elementos de conocimiento?`)) {
        try {
            const res = await fetch('/api/sistema/gestionar_conocimiento/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'delete', ids: selected })
            });
            const result = await res.json();
            alert(result.mensaje);
            loadKnowledgeData(); // Refresh
        } catch (e) {
            alert("Error al eliminar");
        }
    }
}

async function loadVisualizer() {
    // 1. Fetch Knowledge Stats
    let knowledgeData = [];
    try {
        const res = await fetch('/api/analytics/conocimiento_list/');
        knowledgeData = await res.json();
    } catch (e) { console.error("Error stats", e); }

    const html = `
        <h2 class="section-title">Visualizador: Flujo de Aprendizaje IA</h2>
        <div class="pipeline-container">
            <!-- Step 1: Input / Scraping -->
            <div class="pipeline-step" id="step-1">
                <div class="pipeline-icon"><i class="fas fa-globe"></i></div>
                <h3>1. Rastreo Web (Input)</h3>
                <div class="step-content" id="p-step-1">
                    <p style="color:#888; text-align:center; font-size:0.9rem;">Esperando instrucción...</p>
                </div>
                <div class="pipeline-actions">
                    <button class="btn" onclick="simulateScrapingUI()">Simular Búsqueda</button>
                    <div class="input-group" style="margin-top:10px;">
                         <input type="text" id="viz-prompt" placeholder="Tema..." style="width:100%; padding:5px; background:#111; border:1px solid #333; color:white;">
                         <button class="btn btn-primary" style="width:100%; margin-top:5px;" onclick="scrapearCustomViz()">Buscar Real</button>
                    </div>
                </div>
            </div>

            <div class="step-arrow"><i class="fas fa-arrow-right"></i></div>

            <!-- Step 2: Knowledge Base -->
            <div class="pipeline-step active-step" id="step-2">
                <div class="pipeline-icon"><i class="fas fa-brain"></i></div>
                <h3>2. Base de Conocimiento (Staging)</h3>
                <div class="step-content" id="p-step-2">
                    ${knowledgeData.length > 0
            ? knowledgeData.map(k => `
                            <div class="data-chip">
                                <strong>${k.titulo}</strong>
                                <small>${k.fuente.substring(0, 30)}...</small>
                            </div>
                          `).join('')
            : '<p style="text-align:center; color:#888;">Base de conocimiento vacía</p>'
        }
                </div>
                <div class="pipeline-actions">
                    <small>Total: ${knowledgeData.length} reglas</small>
                    <button class="btn" style="width:100%; margin-top:5px;" onclick="openKnowledgeModal()">Ver & Editar Datos</button>
                </div>
            </div>

            <div class="step-arrow"><i class="fas fa-arrow-right"></i></div>

            <!-- Step 3: Generation / Production -->
            <div class="pipeline-step" id="step-3">
                <div class="pipeline-icon"><i class="fas fa-industry"></i></div>
                <h3>3. Generación Inteligente</h3>
                <div class="step-content" id="p-step-3">
                    <p style="text-align:center; color:#888;">Generar datos basados en conocimiento adquirido.</p>
                </div>
                <div class="pipeline-actions">
                    <button class="btn btn-primary" onclick="previewDataGenerationViz()">Vista Previa (50)</button>
                    <button class="btn" style="margin-top:5px;" onclick="confirmDataGeneration()">Confirmar e Insertar</button>
                </div>
            </div>
        </div>

        <!-- Knowledge Detail Modal -->
        <div id="knowledge-modal" style="display:none;" class="modal-overlay">
            <div class="modal-content">
                <h3>Gestionar Conocimiento Recopilado</h3>
                <div class="table-actions">
                     <button class="btn danger" onclick="deleteSelectedKnowledge()">Eliminar Seleccionados</button>
                     <button class="btn" onclick="closeKnowledgeModal()">Cerrar</button>
                </div>
                <div id="knowledge-table-container"></div>
            </div>
        </div>
    `;

    const content = document.getElementById('content');
    content.innerHTML = html;
}

async function openKnowledgeModal() {
    const modal = document.getElementById('knowledge-modal');
    modal.style.display = 'flex';
    // Re-use logic to fetch table
    const res = await fetch('/api/analytics/conocimiento_list/');
    const data = await res.json();

    document.getElementById('knowledge-table-container').innerHTML = `
        <table class="table-compact" style="margin-top:10px;">
            <thead><tr><th>Sel</th><th>Título</th><th>Fuente</th><th>Resumen</th></tr></thead>
            <tbody>
                ${data.map(k => `<tr>
                    <td><input type="checkbox" class="k-check" value="${k.id}"></td>
                    <td>${k.titulo}</td>
                    <td><a href="${k.fuente}" target="_blank">Link</a></td>
                    <td>${k.resumen.substring(0, 50)}...</td>
                </tr>`).join('')}
            </tbody>
        </table>
    `;
}

function closeKnowledgeModal() {
    document.getElementById('knowledge-modal').style.display = 'none';
    loadVisualizer(); // Refresh main view
}

// Visualizer Helper Functions
async function scrapearCustomViz() {
    const prompt = document.getElementById('viz-prompt').value;
    if (!prompt) return alert("Ingrese un tema");

    document.getElementById('p-step-1').innerHTML = '<div class="loading-mini">Rastreando: ' + prompt + '...</div>';

    // Call existing
    await fetch('/api/sistema/aprender_web/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt })
    });

    loadVisualizer(); // Reload to show new knowledge in Step 2
}

async function previewDataGenerationViz() {
    const p3 = document.getElementById('p-step-3');
    p3.innerHTML = '<div class="loading-mini">Consultando Base de Conocimiento y generando propuesta...</div>';

    // Simulate generation locally first for effect or call preview real
    pendingGenerationQty = 50;

    try {
        const res = await fetch('/api/sistema/generar_datos_prueba/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cantidad: 50, preview: true })
        });
        const data = await res.json();

        let html = '';
        data.equipos.slice(0, 5).forEach(e => {
            html += `<div class="data-chip temp">
                <strong>Propuesta: ${e.nombre}</strong>
                <small>Cat: ${e.categoria} | Basado en conocimiento previo</small>
            </div>`;
        });
        html += `<div style="text-align:center; font-style:italic; color:#888;">+ ${data.equipos.length - 5} items más...</div>`;
        p3.innerHTML = html;

        // Show modal as well for full details
        previewDataGeneration(50);

    } catch (e) {
        p3.innerHTML = 'Error: ' + e.message;
    }
}


async function generarDatos(cantidad) {
    if (confirm(`Generar ${cantidad} datos aleatorios?`)) {
        try {
            const response = await fetch('/api/sistema/generar_datos_prueba/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cantidad })
            });
            const result = await response.json();
            alert(result.mensaje || 'Datos generados');
            loadTabContent(currentTab);
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function entrenarIA() {
    if (confirm('Entrenar IA con datos actuales?')) {
        try {
            const response = await fetch('/api/sistema/entrenar/', { method: 'POST' });
            alert('IA entrenada exitosamente');
            loadTabContent(currentTab);
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function generarRecomendaciones() {
    try {
        const response = await fetch('/api/v2/recomendaciones/generar/', { method: 'POST' });
        const result = await response.json();
        alert(`${result.total} recomendaciones generadas`);
        loadTabContent(currentTab);
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function resetIA() {
    if (confirm('Resetear conocimiento de IA? (No afecta BD)')) {
        try {
            const response = await fetch('/api/sistema/reset_ia/', { method: 'POST' });
            const result = await response.json();
            alert(result.mensaje);
            loadTabContent(currentTab);
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function resetDatabase() {
    if (confirm('ELIMINAR TODA LA BASE DE DATOS? Esta acción NO se puede deshacer.')) {
        try {
            const response = await fetch('/api/sistema/reset_database/', { method: 'POST' });
            const result = await response.json();
            alert(result.mensaje);
            loadTabContent(currentTab);
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function scrapearCategoria(categoria) {
    if (confirm(`Iniciar aprendizaje web para categoría ${categoria}?`)) {
        try {
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = "Aprendiendo...";
            btn.disabled = true;

            const response = await fetch('/api/sistema/aprender_web/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ categoria })
            });
            const result = await response.json();

            alert(`Aprendizaje completado: ${result.mensaje}\nResultados: ${result.resultados.resultados_encontrados}`);
            loadTabContent(currentTab);

            btn.innerText = originalText;
            btn.disabled = false;
        } catch (error) {
            alert('Error aprendizaje web: ' + error.message);
        }
    }
}

async function scrapearCustom() {
    const prompt = document.getElementById('custom-topic').value;
    if (!prompt) return alert("Ingrese un tema");

    if (confirm(`¿Buscar e indexar información sobre: "${prompt}"?`)) {
        try {
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = "Investigando...";
            btn.disabled = true;

            const response = await fetch('/api/sistema/aprender_web/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt })
            });
            const result = await response.json();

            alert(`Investigación completa.\nEncontrados: ${result.resultados.resultados_encontrados}\nGuardados: ${result.resultados.conocimientos_guardados}`);

            btn.innerText = originalText;
            btn.disabled = false;
        } catch (error) {
            alert('Error: ' + error.message);
            event.target.innerText = "Buscar y Aprender";
            event.target.disabled = false;
        }
    }
}
// Initialize

async function loadSettings() {
    const html = `
        <h2 class="section-title"><i class="fas fa-cog"></i> Configuración del Sistema</h2>
        
        <div class="ia-controls" style="grid-template-columns: 1fr;">
            
            <div class="control-group">
                <h4><i class="fas fa-database"></i> Gestión de Base de Datos</h4>
                <p style="color:#888; font-size:0.9rem; margin-bottom:15px;">
                    Acciones administrativas destructivas. Úselas con precaución.
                </p>
                
                <div class="button-grid" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));">
                    <button class="control-btn danger" onclick="resetDatabase()">
                        <div style="font-size:1.5rem; margin-bottom:10px;"><i class="fas fa-trash-alt"></i></div>
                        <strong>Purgar Base de Datos</strong>
                        <div style="font-size:0.75rem; margin-top:5px;">Elimina Equipos, Mant., Eventos y Recursos</div>
                    </button>
                    
                    <button class="control-btn danger" onclick="resetIA()">
                        <div style="font-size:1.5rem; margin-bottom:10px;"><i class="fas fa-brain"></i></div>
                        <strong>Purgar Datos IA</strong>
                        <div style="font-size:0.75rem; margin-top:5px;">Elimina solo Conocimiento y Reglas Aprendidas</div>
                    </button>
                </div>
            </div>

            <div class="control-group">
                <h4><i class="fas fa-info-circle"></i> Información del Sistema</h4>
                <div class="stat-row">
                    <span>Versión API:</span> <strong>v2.0 (Django REST)</strong>
                </div>
                <div class="stat-row">
                    <span>Motor IA:</span> <strong>Hybrid Rule-Based / Web Learning</strong>
                </div>
                <div class="stat-row">
                    <span>Estado:</span> <span class="badge badge-success">Operativo</span>
                </div>
            </div>
            
        </div>
    `;

    document.getElementById('content').innerHTML = html;
}

// Initialize
loadDashboard();
