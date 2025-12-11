from django.db import models

# Constantes con nombres descriptivos y claros

# Categorías de Equipo
CATEGORIA_ELECTRICO = 1
CATEGORIA_HIDRAULICO = 2
CATEGORIA_MECANICO = 4
CATEGORIA_GENERAL = 8

# Especialidades de Técnico (mismo esquema que categorías)
ESPECIALIDAD_ELECTRICO = 1
ESPECIALIDAD_HIDRAULICO = 2
ESPECIALIDAD_MECANICO = 4
ESPECIALIDAD_GENERAL = 8

# Estados de Orden de Trabajo
ESTADO_PENDIENTE = 1
ESTADO_EN_PROGRESO = 2
ESTADO_COMPLETADO = 4
ESTADO_CANCELADO = 8

# Prioridades
PRIORIDAD_ALTA = 100
PRIORIDAD_MEDIA = 50
PRIORIDAD_BAJA = 10
PRIORIDAD_CRITICA = 999


class CategoriaEquipo(models.IntegerChoices):
    """Categorías de equipos industriales"""

    ELECTRICO = CATEGORIA_ELECTRICO, "Eléctrico"
    HIDRAULICO = CATEGORIA_HIDRAULICO, "Hidráulico"
    MECANICO = CATEGORIA_MECANICO, "Mecánico"
    GENERAL = CATEGORIA_GENERAL, "General"


class EspecialidadTecnico(models.IntegerChoices):
    """Especialidades de técnicos de mantenimiento"""

    ELECTRICO = ESPECIALIDAD_ELECTRICO, "Eléctrico"
    HIDRAULICO = ESPECIALIDAD_HIDRAULICO, "Hidráulico"
    MECANICO = ESPECIALIDAD_MECANICO, "Mecánico"
    GENERAL = ESPECIALIDAD_GENERAL, "General"


class EstadoOrden(models.IntegerChoices):
    """Estados de órdenes de trabajo"""

    PENDIENTE = ESTADO_PENDIENTE, "Pendiente"
    EN_PROGRESO = ESTADO_EN_PROGRESO, "En Progreso"
    COMPLETADO = ESTADO_COMPLETADO, "Completado"
    CANCELADO = ESTADO_CANCELADO, "Cancelado"


class Prioridad(models.IntegerChoices):
    """Niveles de prioridad"""

    ALTA = PRIORIDAD_ALTA, "Alta"
    MEDIA = PRIORIDAD_MEDIA, "Media"
    BAJA = PRIORIDAD_BAJA, "Baja"
    CRITICA = PRIORIDAD_CRITICA, "Crítica"


# Configuración de IA: palabras clave y pesos para cálculo de prioridad
PALABRAS_CLAVE_PRIORIDAD = {
    PRIORIDAD_ALTA: [
        ("fuego", 50),
        ("critico", 40),
        ("urgente", 45),
        ("falla", 35),
    ],
    PRIORIDAD_MEDIA: [
        ("ruido", 20),
        ("ajuste", 10),
        ("revision", 15),
    ],
}

# Umbrales para clasificación de prioridad
UMBRAL_PRIORIDAD_ALTA = 30
UMBRAL_PRIORIDAD_MEDIA = 20
