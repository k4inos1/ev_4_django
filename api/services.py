from django.db.models import Count, Q
from .models import Tec, OT, Emp, Eq, PM
from .constants import KW_PRIORIDAD, UMBRAL_ALTO, UMBRAL_MEDIO, PO, ET, EO, CE


class ServIA:
    """
    Servicio de Inteligencia Artificial (Lógica Pura).
    """

    @staticmethod
    def calc_p(txt: str) -> str:
        """
        Calcula Prioridad basada en texto (Heurística).
        """
        if not txt:
            return PO.MEDI

        t = txt.lower()
        p_a = 0
        p_m = 0

        # Puntaje Alta
        for w, v in KW_PRIORIDAD.get(PO.ALTA, []):
            if w in t:
                p_a += v

        # Puntaje Media
        for w, v in KW_PRIORIDAD.get(PO.MEDI, []):
            if w in t:
                p_m += v

        # Logica
        if p_a >= UMBRAL_ALTO:
            return PO.ALTA
        elif p_a > 0 or p_m >= UMBRAL_MEDIO:
            return PO.MEDI

        return PO.BAJA

    @staticmethod
    def busc_t(cat: str) -> dict:
        """
        Busca Técnico ideal por especialidad y carga.
        """
        # 1. Filtro
        cands = Tec.objects.filter(Q(especialidad=cat) | Q(especialidad=ET.GRAL))

        if not cands.exists():
            return None

        # 2. Balanceo
        cands = cands.annotate(
            carga=Count("workorder", filter=Q(workorder__estado__in=[EO.PEND, EO.PROG]))
        ).order_by("carga", "nombre")

        # 3. Mejor
        best = cands.first()

        if not best:
            return None

        return {
            "id": best.id,
            "nom": best.nombre,
            "esp": best.especialidad,
            "carga": best.carga,
            "msg": f"Match: {cat}, carga: {best.carga}.",
        }


class ServOT:
    """
    Servicio para Ordenes de Trabajo.
    """

    @staticmethod
    def crear_o_actualizar(ot: OT) -> OT:
        """
        Aplica logica de negocio al guardar OT.
        """
        if ot.notas:
            p_a = ServIA.calc_p(ot.notas)
            if p_a != ot.prioridad:
                ot.prioridad = p_a
                # No guardamos aqui para evitar recursividad si se llama desde signal,
                # pero retornamos el objeto modificado.
        return ot


class ServGral:
    """
    Servicio General (Datos Totales / Dashboard).
    """

    @staticmethod
    def resumen_api() -> dict:
        """
        Retorna estadísticas globales del sistema.
        """
        # Contadores
        c_emp = Emp.objects.count()
        c_eq = Eq.objects.count()
        c_ot = OT.objects.count()
        c_tec = Tec.objects.count()

        # Desglose OT
        ot_pen = OT.objects.filter(estado=EO.PEND).count()
        ot_pro = OT.objects.filter(estado=EO.PROG).count()
        ot_alt = OT.objects.filter(prioridad=PO.ALTA).count()

        # Equipos Criticos
        eq_crit = Eq.objects.filter(critico=True).count()

        return {
            "global": {
                "empresas": c_emp,
                "equipos": c_eq,
                "ordenes": c_ot,
                "tecnicos": c_tec,
            },
            "estado_ot": {
                "pendientes": ot_pen,
                "en_progreso": ot_pro,
                "criticas_altas": ot_alt,
            },
            "equipos": {
                "criticos": eq_crit,
                "ratio_critico": round(eq_crit / c_eq, 2) if c_eq > 0 else 0,
            },
            "status": "OK_SISTEMA",
        }
