# EV4 Django - API Inteligente de Mantenimiento

> Sistema de gestión de mantenimiento industrial con IA, Reinforcement Learning y Web Scraping

## Características

- **IA Integrada**: Cálculo automático de prioridades
- **Reinforcement Learning**: Mejora continua con cada operación
- **Web Scraping**: Recolección automática de datos reales
- **Dashboard Interactivo**: Visualización en tiempo real
- **API RESTful**: Documentación OpenAPI completa

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/usuario/ev_4_django.git
cd ev_4_django

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Migrar base de datos
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

## Uso Rápido

### Iniciar Sistema

```bash
python manage.py runserver
```

El sistema se auto-inicializa y estará disponible en:
- **Dashboard**: http://127.0.0.1:8000/
- **API**: http://127.0.0.1:8000/api/
- **Documentación**: http://127.0.0.1:8000/api/docs/

### Generar Datos

```bash
# Generar datos sintéticos
python manage.py generar_datos --cantidad 50

# Aprender de la web y generar datos reales
python manage.py aprender_web --busquedas 10
```

## API Principal

### Recursos CRUD

```bash
GET/POST   /api/equipos/          # Equipos
GET/POST   /api/mantenimientos/   # Mantenimientos
GET/POST   /api/recursos/         # Recursos (técnicos, repuestos)
GET/POST   /api/eventos/          # Eventos del sistema
```

### Sistema Inteligente

```bash
POST /api/sistema/decidir/        # Tomar decisión IA
POST /api/sistema/aprender/       # Aprender de resultado
POST /api/sistema/aprender_web/   # Aprender de web
GET  /api/sistema/estadisticas/   # Estadísticas del sistema
```

### Ejemplo de Uso

```bash
# Decidir prioridad con IA
curl -X POST http://127.0.0.1:8000/api/sistema/decidir/ \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "prioridad",
    "descripcion": "Falla crítica en bomba principal"
  }'

# Respuesta
{
  "tipo": "prioridad",
  "decision": 100,
  "metodo": "IA + RL",
  "rust_usado": false
}
```

## Arquitectura

### Modelos

- **Equipo**: Equipos industriales
- **Mantenimiento**: Órdenes de trabajo
- **Recurso**: Técnicos, repuestos, proveedores
- **Evento**: Registro de eventos
- **ModeloIA**: Modelos de IA entrenados

### Sistema IA

```
api/servicios/ia_core.py
├── decidir_prioridad()      # IA + RL
├── decidir_tecnico()        # Asignación RL
├── aprender_de_resultado()  # Q-Learning
└── aprender_de_web()        # Web scraping
```

## Tecnologías

- **Backend**: Django 5.1, Django REST Framework
- **IA/ML**: scikit-learn, NumPy
- **RL**: Q-Learning personalizado
- **Scraping**: BeautifulSoup4
- **Aceleración**: Rust
- **Docs**: OpenAPI 3.0 (ReDoc)


## Configuración

### Variables de Entorno

Crear archivo `.env`:

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Producción

- Configurar `DEBUG=False`
- Usar PostgreSQL/MySQL
- Configurar `ALLOWED_HOSTS`
- Ejecutar `collectstatic`
- Configurar HTTPS

## Comandos Útiles

```bash
# Verificar sistema
python manage.py check

# Crear superusuario
python manage.py createsuperuser

# Generar datos de prueba
python manage.py generar_datos --cantidad 100

# Aprender de la web
python manage.py aprender_web --busquedas 5
```


## Licencia

MIT License

---

