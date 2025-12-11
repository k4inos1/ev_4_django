// EV4 Sistema IA - JavaScript

let currentTab = 'dashboard';

function showTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    loadTabContent(tab);
}

async function loadTabContent(tab) {
    const content = document.getElementById('content');
    content.innerHTML = '<div class="loading">Cargando...</div>';

    try {
        if (tab === 'dashboard') await loadDashboard();
        else if (tab === 'db') await loadDatabase();
        else if (tab === 'ia') await loadIAControl();
        else if (tab === 'analytics') await loadAnalytics();
        else if (tab === 'scraping') await loadScraping();
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
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Equipos Totales</div>
                <div class="card-value">${analytics.equipos?.total || 0}</div>
                <div class="card-subtitle">${analytics.equipos?.criticos || 0} críticos</div>
            </div>
            <div class="card">
                <div class="card-title">Mantenimientos</div>
                <div class="card-value">${analytics.mantenimientos?.total || 0}</div>
                <div class="card-subtitle">${analytics.mantenimientos?.pendientes || 0} pendientes</div>
            </div>
            <div class="card">
                <div class="card-title">Precisión IA</div>
                <div class="card-value">${((analytics.ia?.precision_promedio || 0) * 100).toFixed(1)}%</div>
                <div class="card-subtitle">${analytics.ia?.aprendizajes || 0} aprendizajes</div>
            </div>
            <div class="card">
                <div class="card-title">Conocimiento Web</div>
                <div class="card-value">${analytics.ia?.conocimiento_web || 0}</div>
                <div class="card-subtitle">${analytics.ia?.recomendaciones || 0} recomendaciones</div>
            </div>
        </div>
    `;

    document.getElementById('content').innerHTML = html;
}

async function loadDatabase() {
    const [equipos, mantenimientos, recursos, eventos] = await Promise.all([
        fetch('/api/equipos/').then(r => r.json()),
        fetch('/api/mantenimientos/').then(r => r.json()),
        fetch('/api/recursos/').then(r => r.json()),
        fetch('/api/eventos/').then(r => r.json())
    ]);

    const html = `
        <h2 class="section-title">Visor Completo de Base de Datos</h2>
        
        <div class="table-container">
            <div class="table-header">
                <h3>Equipos (${equipos.length})</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Empresa</th>
                        <th>Categoría</th>
                        <th>Estado</th>
                        <th>Crítico</th>
                    </tr>
                </thead>
                <tbody>
                    ${equipos.slice(0, 10).map(eq => `
                        <tr>
                            <td>${eq.id}</td>
                            <td>${eq.nombre}</td>
                            <td>${eq.empresa_nombre}</td>
                            <td>${eq.categoria_display || eq.categoria}</td>
                            <td><span class="badge badge-success">${eq.estado}</span></td>
                            <td>${eq.es_critico ? 'Si' : 'No'}</td>
                        </tr>
                    `).join('') || '<tr><td colspan="6" style="text-align: center; padding: 40px;">Sin datos</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="table-container">
            <div class="table-header">
                <h3>Mantenimientos (${mantenimientos.length})</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Equipo</th>
                        <th>Tipo</th>
                        <th>Prioridad</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    ${mantenimientos.slice(0, 10).map(m => {
        const badgeClass = m.prioridad > 70 ? 'badge-error' : m.prioridad > 40 ? 'badge-warning' : 'badge-success';
        return `
                            <tr>
                                <td>${m.id}</td>
                                <td>${m.equipo}</td>
                                <td>${m.tipo}</td>
                                <td><span class="badge ${badgeClass}">${m.prioridad}</span></td>
                                <td>${m.estado}</td>
                            </tr>
                        `;
    }).join('') || '<tr><td colspan="5" style="text-align: center; padding: 40px;">Sin datos</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="table-container">
            <div class="table-header">
                <h3>Recursos (${recursos.length})</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Nombre</th>
                        <th>Stock</th>
                        <th>Disponible</th>
                    </tr>
                </thead>
                <tbody>
                    ${recursos.slice(0, 10).map(r => `
                        <tr>
                            <td>${r.id}</td>
                            <td>${r.tipo}</td>
                            <td>${r.nombre}</td>
                            <td>${r.stock || '-'}</td>
                            <td>${r.disponible ? 'Si' : 'No'}</td>
                        </tr>
                    `).join('') || '<tr><td colspan="5" style="text-align: center; padding: 40px;">Sin datos</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="table-container">
            <div class="table-header">
                <h3>Eventos (${eventos.length})</h3>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Descripción</th>
                        <th>Severidad</th>
                    </tr>
                </thead>
                <tbody>
                    ${eventos.slice(0, 10).map(e => `
                        <tr>
                            <td>${e.id}</td>
                            <td>${e.tipo}</td>
                            <td>${e.descripcion?.substring(0, 50)}...</td>
                            <td>${e.severidad}</td>
                        </tr>
                    `).join('') || '<tr><td colspan="4" style="text-align: center; padding: 40px;">Sin datos</td></tr>'}
                </tbody>
            </table>
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
                <div class="card-title">Rust Engine</div>
                <div class="card-value">
                    <span class="status-indicator ${rustStatus ? 'status-on' : 'status-off'}"></span>
                    ${rustStatus ? 'ON' : 'OFF'}
                </div>
                <div class="card-subtitle">Aceleración de cálculos</div>
            </div>
            <div class="card">
                <div class="card-title">Learning Rate</div>
                <div class="card-value">${(metricas.sistema?.learning_rate || 0.1).toFixed(3)}</div>
                <div class="card-subtitle">Velocidad de aprendizaje</div>
            </div>
            <div class="card">
                <div class="card-title">Epsilon</div>
                <div class="card-value">${(metricas.sistema?.epsilon || 0.1).toFixed(3)}</div>
                <div class="card-subtitle">Exploración vs Explotación</div>
            </div>
            <div class="card">
                <div class="card-title">Estados IA</div>
                <div class="card-value">${stats.estadisticas?.total_estados || 0}</div>
                <div class="card-subtitle">${stats.estadisticas?.total_acciones || 0} acciones</div>
            </div>
        </div>

        <h3 class="section-title">Acciones Rápidas</h3>
        <div class="ia-controls">
            <button class="control-btn" onclick="generarDatos(10)">Generar 10 Datos</button>
            <button class="control-btn" onclick="generarDatos(50)">Generar 50 Datos</button>
            <button class="control-btn" onclick="generarDatos(100)">Generar 100 Datos</button>
            <button class="control-btn" onclick="entrenarIA()">Entrenar IA</button>
            <button class="control-btn" onclick="generarRecomendaciones()">Generar Recomendaciones</button>
            <button class="control-btn danger" onclick="resetIA()">Reset Conocimiento IA</button>
            <button class="control-btn danger" onclick="resetDatabase()">Reset BD Completa</button>
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

async function loadScraping() {
    const html = `
        <h2 class="section-title">Web Learning - Scraping Inteligente</h2>
        
        <div class="cards-grid">
            <div class="card">
                <div class="card-title">Estado</div>
                <div class="card-value">
                    <span class="status-indicator status-on"></span>
                    Activo
                </div>
                <div class="card-subtitle">Sistema de aprendizaje web</div>
            </div>
        </div>

        <h3 class="section-title">Acciones de Web Learning</h3>
        <div class="ia-controls">
            <button class="control-btn" onclick="scrapearCategoria(1)">Aprender sobre Bombas</button>
            <button class="control-btn" onclick="scrapearCategoria(2)">Aprender sobre Motores</button>
            <button class="control-btn" onclick="scrapearCategoria(3)">Aprender sobre Compresores</button>
            <button class="control-btn" onclick="scrapearCategoria(4)">Aprender sobre Generadores</button>
            <button class="control-btn" onclick="scrapearTodasCategorias()">Aprender Todas las Categorías</button>
        </div>
    `;

    document.getElementById('content').innerHTML = html;
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
    alert(`Scraping para categoría ${categoria} iniciado`);
}

async function scrapearTodasCategorias() {
    if (confirm('Iniciar scraping de todas las categorías?')) {
        alert('Scraping iniciado');
    }
}

// Initialize
loadDashboard();
