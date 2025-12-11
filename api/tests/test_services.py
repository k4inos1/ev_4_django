from datetime import date

import pytest
from django.contrib.auth.models import User

from api.constants import CE, CE_EL, EO, ET, PO
from api.models import OT, PM, Emp, Eq, Tec
from api.servicios import ServGral, ServIA, ServOT


@pytest.fixture
def data(db):
    u = User.objects.create(username="u")
    c = Emp.objects.create(nom="c", rut="1", dir="d")
    e = Eq.objects.create(emp=c, nom="e", ser="s", cat=CE.EL, t_i=date.today())
    t = Tec.objects.create(usr=u, nom="t", esp=ET.EL)
    p = PM.objects.create(eq=e, nom="p", frq=30)
    return {"u": u, "c": c, "e": e, "t": t, "p": p}


@pytest.mark.django_db
class TestServIA:
    def test_p_al(self):
        assert ServIA.calc_p("fuego critico") == PO.ALTA

    def test_t_busc(self, data):
        data = data
        OT.objects.create(
            pln=data["p"],
            eq=data["e"],
            tec=data["t"],
            pr=PO.ALTA,
            t_p=date.today(),
            st=EO.PEND,
        )
        # buscar por cat int
        r = ServIA.busc_t(CE_EL)
        assert r["n"] == "t"


@pytest.mark.django_db
class TestServOT:
    def test_sinc(self, data):
        d = data
        ot = OT(
            pln=d["p"], eq=d["e"], tec=d["t"], t_p=date.today(), pr=PO.BAJA, n="fuego"
        )
        ot = ServOT.sinc(ot)
        assert ot.pr == PO.ALTA


@pytest.mark.django_db
class TestServGral:
    def test_pulso(self):
        res = ServGral.pulso()
        assert res["sys"] == "OK_0x1"
