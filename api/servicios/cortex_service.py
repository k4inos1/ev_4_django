from api.models import Equipo, Mantenimiento
from api.cortex.neural_net import CortexNN
from django.utils import timezone
import random

# Singleton instance placeholder
_cortex_instance = None


class CortexService:
    @staticmethod
    def get_instance():
        global _cortex_instance
        if _cortex_instance is None:
            # Input: [antiguedad_norm, categoria_norm, mant_pendientes_norm]
            # Output: [probabilidad_falla]
            _cortex_instance = CortexNN(input_size=3, hidden_size=5, output_size=1)
        return _cortex_instance

    @staticmethod
    def vectorizar_equipo(equipo):
        """Convierte un objeto Equipo en un vector numérico [0-1]"""
        # 1. Antiguedad (0 a 10 años normalizado)
        dias_uso = (timezone.now().date() - equipo.fecha_instalacion).days
        antiguedad = min(dias_uso / 3650, 1.0)  # max 10 años

        # 2. Categoría (Hash simple normalizado o one-hot simplificado)
        # Asumimos categorias 1-5
        cat_norm = equipo.categoria / 5.0

        # 3. Mantenimientos Pendientes (0 si clean, 1 si saturado)
        pendientes = Mantenimiento.objects.filter(equipo=equipo, estado=1).count()
        pend_norm = min(pendientes / 5.0, 1.0)  # max 5 pendientes

        return [antiguedad, cat_norm, pend_norm]

    @staticmethod
    def entrenar_con_historia():
        """Entrena la red usando historial de mantenimientos pasados"""
        nn = CortexService.get_instance()
        mantenimientos = Mantenimiento.objects.filter(
            estado=4
        )  # Completados (historia)

        errores = []
        for m in mantenimientos:
            # Recrear estado "pasado" (simulado para este ejemplo)
            # Inputvector: el estado del equipo
            inputs = CortexService.vectorizar_equipo(m.equipo)

            # Target: 1.0 si fue correctivo (falló), 0.0 si fue preventivo (no falló)
            target = [1.0] if m.tipo == "Correctivo" else [0.0]

            loss = nn.train(inputs, target)
            errores.append(loss)

        return sum(errores) / len(errores) if errores else 0.0

    @staticmethod
    def predecir_riesgo_neuronal(equipo):
        nn = CortexService.get_instance()
        vec = CortexService.vectorizar_equipo(equipo)
        output = nn.forward(vec)
        return output[0]  # Probabilidad entre 0 y 1
