from django.db import models

# estados bitwise / int (hiper-densa)
# 0x0...
CE_EL, CE_HI, CE_ME, CE_GR = 1, 2, 4, 8
ET_EL, ET_HI, ET_ME, ET_GR = 1, 2, 4, 8
EO_PE, EO_PR, EO_OK, EO_XX = 1, 2, 4, 8
PO_AL, PO_ME, PO_BA, PO_CR = 100, 50, 10, 999


class CE(models.IntegerChoices):
    EL = CE_EL, "E"
    HI = CE_HI, "H"
    ME = CE_ME, "M"
    GR = CE_GR, "G"


class ET(models.IntegerChoices):
    EL = ET_EL, "E"
    HI = ET_HI, "H"
    ME = ET_ME, "M"
    GR = ET_GR, "G"


class EO(models.IntegerChoices):
    PEND = EO_PE, "P"
    PROG = EO_PR, "R"
    COMP = EO_OK, "C"
    CANC = EO_XX, "X"


class PO(models.IntegerChoices):
    ALTA = PO_AL, "AL"
    MEDI = PO_ME, "ME"
    BAJA = PO_BA, "BA"
    CRIT = PO_CR, "CX"


# config ia (pesos)
KW = {
    PO_AL: [("fuego", 50), ("critico", 40)],
    PO_ME: [("ruido", 20), ("ajuste", 10)],
}
UM_AL, UM_ME = 30, 20
