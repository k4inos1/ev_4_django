from .comun import ServicioGeneral, ServicioMantenimiento
from .scraping import ServicioScraping
from .ia_core import ia_sistema

# Mantener compatibilidad con código antiguo
from .ia_core import ia_sistema as ServicioIA

__all__ = [
    "ServicioIA",  # Alias para compatibilidad
    "ServicioMantenimiento",
    "ServicioGeneral",
    "ServicioScraping",
    "ia_sistema", 
]
