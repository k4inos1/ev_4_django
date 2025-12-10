from django.db import models


class CE(models.TextChoices):
    ELEC = "ELEC", "Eléctrico"
    HIDR = "HIDR", "Hidráulico"
    MECA = "MECA", "Mecánico"
    GRAL = "GRAL", "General"


class ET(models.TextChoices):
    ELEC = "ELEC", "Eléctrico"
    HIDR = "HIDR", "Hidráulico"
    MECA = "MECA", "Mecánico"
    GRAL = "GRAL", "General"


class EO(models.TextChoices):
    PEND = "PEND", "Pendiente"
    PROG = "PROG", "En Progreso"
    COMP = "COMP", "Completado"
    CANC = "CANC", "Cancelado"


class PO(models.TextChoices):
    ALTA = "ALTA", "Alta"
    MEDI = "MEDI", "Media"
    BAJA = "BAJA", "Baja"


# Config IA
KW_PRIORIDAD = {
    PO.ALTA: [
        ("urgente", 50),
        ("critico", 40),
        ("fuego", 50),
        ("falla", 30),
        ("inmediato", 40),
        ("peligro", 40),
        ("roto", 30),
        ("detenido", 40),
    ],
    PO.MEDI: [
        ("revisar", 10),
        ("mantenimiento", 10),
        ("ruido", 20),
        ("ajuste", 10),
        ("fuga", 20),
        ("desgaste", 10),
    ],
}

UMBRAL_ALTO = 30
UMBRAL_MEDIO = 20
