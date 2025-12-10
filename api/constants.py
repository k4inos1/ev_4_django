from django.db import models


class EquipmentCategory(models.TextChoices):
    ELECTRICO = "ELECTRICO", "Eléctrico"
    HIDRAULICO = "HIDRAULICO", "Hidráulico"
    MECANICO = "MECANICO", "Mecánico"
    GENERAL = "GENERAL", "General"


class TechnicianSpecialty(models.TextChoices):
    ELECTRICO = "ELECTRICO", "Eléctrico"
    HIDRAULICO = "HIDRAULICO", "Hidráulico"
    MECANICO = "MECANICO", "Mecánico"
    GENERAL = "GENERAL", "General"


class WorkOrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    IN_PROGRESS = "IN_PROGRESS", "En Progreso"
    COMPLETED = "COMPLETED", "Completado"
    CANCELLED = "CANCELLED", "Cancelado"


class WorkOrderPriority(models.TextChoices):
    ALTA = "ALTA", "Alta"
    MEDIA = "MEDIA", "Media"
    BAJA = "BAJA", "Baja"


# AI Configuration
PRIORITY_KEYWORDS = {
    WorkOrderPriority.ALTA: [
        ("urgente", 50),
        ("critico", 40),
        ("fuego", 50),
        ("falla", 30),
        ("inmediato", 40),
        ("peligro", 40),
        ("roto", 30),
        ("detenido", 40),
    ],
    WorkOrderPriority.MEDIA: [
        ("revisar", 10),
        ("mantenimiento", 10),
        ("ruido", 20),
        ("ajuste", 10),
        ("fuga", 20),
        ("desgaste", 10),
    ],
}

THRESHOLD_HIGH = 30
THRESHOLD_MEDIUM = 20
