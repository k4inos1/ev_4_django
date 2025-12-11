import datetime
import os
import sys
import time

import django
import psutil

# config entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from api.constants import CE_GR  # noqa: E402
from api.models import Emp, Eq, Nodo  # noqa: E402
from api.servicios import ServFlux  # noqa: E402

# ==========================================
# benchmark neuro-digital (alta velocidad)
# ==========================================
print("\n--- iniciando protocolo de prueba: velocidad tactica ---\n")

mem_ini = psutil.Process().memory_info().rss / 1024 / 1024
print(f"[recursos] memoria base: {mem_ini:.2f} mb")

# 1. generacion de escenario (creacion masiva)
t0 = time.time()
emp = Emp.objects.create(nom="ind. test", rut="x", dir="lab")
eq = Eq.objects.create(
    emp=emp, nom="reactor 1", ser="r1", cat=CE_GR, t_i=datetime.date.today()
)

cant_nodos = 5000
print(f"[accion] desplegando {cant_nodos} nodos sensores virtuales...")

nodos = []
for i in range(cant_nodos):
    # simulamos valores altos (criticos) para forzar al sistema a reaccionar
    val_sim = 99.9 if i % 2 == 0 else 20.0
    import uuid

    nodos.append(Nodo(uid=uuid.uuid4(), eq=eq, lec=val_sim))

Nodo.objects.bulk_create(nodos)
dt_creacion = time.time() - t0
ops = int(cant_nodos / dt_creacion)
print(f" -> despliegue completado en {dt_creacion:.4f}s ({ops} ops/s)")

# 2. neuro-scan (reaccion autonoma)
print("\n[accion] ejecutando servflux.neuro_escan() (deteccion de anomalias)...")
t1 = time.time()
alertas_gen = ServFlux.neuro_escan(umbral=90.0)
dt_neuro = time.time() - t1

print(f" -> escaneo finalizado en {dt_neuro:.4f}s")
print(f" -> alertas criticas generadas (ots): {alertas_gen}")
if alertas_gen > 0:
    vel_reac = alertas_gen / dt_neuro
    print(f" -> velocidad de reaccion: {int(vel_reac)} decisiones/s")

# metrica final
mem_fin = psutil.Process().memory_info().rss / 1024 / 1024
print(f"\n[recursos] memoria final: {mem_fin:.2f} mb (delta: {mem_fin-mem_ini:.2f} mb)")
print("--- protocolo finalizado: exitoso ---")

# limpieza (opcional, para no ensuciar db de dev)
# emp.objects.all().delete()
