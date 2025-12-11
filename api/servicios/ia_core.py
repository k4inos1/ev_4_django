"""
Sistema de IA Principal
Integra: ML Training + Reinforcement Learning + Web Scraping + Decisiones Inteligentes
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

# Importar RL de Rust si está disponible
try:
    from k_ia import calc_p_rust, update_q_value as rust_update_q

    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False


class SistemaIA:
    """
    Sistema de IA completo y unificado

    Combina:
    - Cálculo de prioridades (IA heurística)
    - Reinforcement Learning (aprendizaje continuo)
    - Web Scraping (datos reales)
    - Decisiones optimizadas
    """

    def __init__(self):
        self.estado = "idle"

        # RL Configuration
        self.q_table = self._cargar_conocimiento()
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploración

        # Métricas globales
        self.metricas = {
            "decisiones_totales": 0,
            "decisiones_correctas": 0,
            "recompensa_acumulada": 0.0,
            "precision_actual": 0.0,
            "aprendizajes_web": 0,
        }

    # ═══════════════════════════════════════════════════════
    # DECISIONES INTELIGENTES
    # ═══════════════════════════════════════════════════════

    def decidir_prioridad(self, descripcion: str, contexto: Dict = None) -> int:
        """
        Decide prioridad combinando IA + RL

        1. IA calcula prioridad base (heurística/Rust)
        2. RL ajusta basándose en experiencia pasada
        3. Retorna prioridad optimizada
        """
        from api.constants import PRIORIDAD_ALTA, PRIORIDAD_MEDIA, PRIORIDAD_BAJA

        # Paso 1: Cálculo base
        if RUST_AVAILABLE:
            prioridad_base = calc_p_rust(descripcion)
        else:
            prioridad_base = self._calcular_prioridad_python(descripcion)

        # Paso 2: Ajuste con RL
        if contexto and self.q_table:
            estado = self._crear_estado(contexto)
            acciones_posibles = [PRIORIDAD_BAJA, PRIORIDAD_MEDIA, PRIORIDAD_ALTA]
            prioridad_ajustada = self._elegir_mejor_accion(estado, acciones_posibles)
            if prioridad_ajustada:
                return int(prioridad_ajustada)

        return prioridad_base

    def decidir_tecnico(
        self, mantenimiento, tecnicos_disponibles: List
    ) -> Optional[Dict]:
        """
        Decide qué técnico asignar usando RL

        Aprende de asignaciones pasadas para optimizar:
        - Tiempo de resolución
        - Costo
        - Éxito de la tarea
        """
        if not tecnicos_disponibles:
            return None

        # Crear estado
        estado = f"cat_{mantenimiento.equipo.categoria}_tipo_{mantenimiento.tipo}_pri_{mantenimiento.prioridad}"

        # Acciones = técnicos disponibles
        acciones = [f"tecnico_{t.id}" for t in tecnicos_disponibles]

        # Elegir mejor
        mejor_accion = self._elegir_mejor_accion(estado, acciones)

        if mejor_accion:
            tecnico_id = int(mejor_accion.split("_")[1])
            tecnico = next(
                (t for t in tecnicos_disponibles if t.id == tecnico_id), None
            )
            return {
                "tecnico": tecnico,
                "confianza": self._obtener_confianza(estado, mejor_accion),
            }

        # Fallback: técnico con mejor calificación
        return {
            "tecnico": max(tecnicos_disponibles, key=lambda t: t.calificacion),
            "confianza": 0.5,
        }

    # ═══════════════════════════════════════════════════════
    # APRENDIZAJE CONTINUO
    # ═══════════════════════════════════════════════════════

    def aprender_de_resultado(self, mantenimiento, resultado: Dict) -> Dict:
        """
        Aprende de un resultado y actualiza conocimiento

        Args:
            mantenimiento: Objeto Mantenimiento
            resultado: {
                'fue_exitoso': bool,
                'dias_resolucion': int,
                'costo_real': float,
                'costo_esperado': float
            }

        Returns:
            Dict con info del aprendizaje
        """
        # Crear estado y acción
        estado = f"cat_{mantenimiento.equipo.categoria}_tipo_{mantenimiento.tipo}_pri_{mantenimiento.prioridad}"
        accion = f"tecnico_{mantenimiento.tecnico_asignado}"

        # Calcular recompensa
        recompensa = self._calcular_recompensa(resultado)

        # Actualizar Q-value
        next_estado = f"{estado}_completado"
        q_anterior = self.q_table.get(estado, {}).get(accion, 0.0)
        q_nuevo = self._actualizar_q_value(estado, accion, recompensa, next_estado)

        # Actualizar métricas
        self.metricas["decisiones_totales"] += 1
        if resultado.get("fue_exitoso"):
            self.metricas["decisiones_correctas"] += 1
        self.metricas["recompensa_acumulada"] += recompensa
        self.metricas["precision_actual"] = self.metricas["decisiones_correctas"] / max(
            self.metricas["decisiones_totales"], 1
        )

        # Guardar
        self._guardar_conocimiento()

        return {
            "recompensa": recompensa,
            "q_anterior": q_anterior,
            "q_nuevo": q_nuevo,
            "mejora": q_nuevo - q_anterior,
            "precision_sistema": self.metricas["precision_actual"],
        }

    def aprender_de_web(self, tema: str, max_resultados: int = 5) -> Dict:
        """
        Busca en web y aprende automáticamente

        Integra: scraping + extracción + aprendizaje
        """
        from .scraping import ServicioScraping

        resultados = ServicioScraping.buscar_web(tema, max_resultados)

        aprendizajes = 0
        for resultado in resultados:
            if "error" not in resultado:
                # Estado basado en tema
                estado_web = f"web_{tema.replace(' ', '_')[:30]}"
                accion_web = "extraer_conocimiento"

                # Recompensa basada en calidad
                contenido = resultado.get("contenido", "")
                recompensa_web = min(len(contenido) / 1000.0, 5.0)  # Max 5.0

                # Aprender
                self._actualizar_q_value(
                    estado_web, accion_web, recompensa_web, estado_web
                )
                aprendizajes += 1

        self.metricas["aprendizajes_web"] += aprendizajes
        self._guardar_conocimiento()

        return {
            "tema": tema,
            "resultados_encontrados": len(resultados),
            "aprendizajes": aprendizajes,
            "total_aprendizajes_web": self.metricas["aprendizajes_web"],
        }

    # ═══════════════════════════════════════════════════════
    # MÉTODOS INTERNOS
    # ═══════════════════════════════════════════════════════

    def _calcular_prioridad_python(self, texto: str) -> int:
        """Cálculo de prioridad en Python (fallback)"""
        from api.constants import (
            PALABRAS_CLAVE_PRIORIDAD,
            PRIORIDAD_ALTA,
            PRIORIDAD_MEDIA,
            PRIORIDAD_BAJA,
            UMBRAL_PRIORIDAD_ALTA,
            UMBRAL_PRIORIDAD_MEDIA,
        )

        texto_lower = texto.lower()
        score = sum(
            10 for palabra in PALABRAS_CLAVE_PRIORIDAD if palabra in texto_lower
        )

        if score >= UMBRAL_PRIORIDAD_ALTA:
            return PRIORIDAD_ALTA
        elif score >= UMBRAL_PRIORIDAD_MEDIA:
            return PRIORIDAD_MEDIA
        else:
            return PRIORIDAD_BAJA

    def _crear_estado(self, contexto: Dict) -> str:
        """Crea representación de estado"""
        return f"cat_{contexto.get('categoria', 0)}_tipo_{contexto.get('tipo', 'unknown')}_pri_{contexto.get('prioridad', 0)}"

    def _elegir_mejor_accion(self, estado: str, acciones: List) -> any:
        """Elige mejor acción usando epsilon-greedy"""
        if not acciones:
            return None

        # Epsilon-greedy: exploración vs explotación
        if np.random.random() < self.epsilon:
            # Exploración: acción aleatoria
            return np.random.choice(acciones)

        # Explotación: mejor acción conocida
        q_values = [self.q_table.get(estado, {}).get(str(a), 0.0) for a in acciones]

        if max(q_values) == 0:
            # Si no hay experiencia, elegir aleatoriamente
            return np.random.choice(acciones)

        max_idx = np.argmax(q_values)
        return acciones[max_idx]

    def _calcular_recompensa(self, resultado: Dict) -> float:
        """Calcula recompensa total basada en resultado"""
        reward = 0.0

        # Éxito/Falla
        if resultado.get("fue_exitoso"):
            reward += 10.0
        else:
            reward -= 15.0

        # Tiempo de resolución
        dias = resultado.get("dias_resolucion", 999)
        if dias < 7:
            reward += 5.0
        elif dias > 30:
            reward -= 5.0

        # Eficiencia de costo
        costo_esperado = resultado.get("costo_esperado", 1000)
        costo_real = resultado.get("costo_real", 1000)

        if costo_real < costo_esperado * 0.8:
            reward += 3.0
        elif costo_real > costo_esperado * 1.5:
            reward -= 3.0

        return reward

    def _actualizar_q_value(
        self, estado: str, accion: str, reward: float, next_estado: str
    ) -> float:
        """Actualiza Q-value usando Q-Learning"""
        # Inicializar si no existe
        if estado not in self.q_table:
            self.q_table[estado] = {}
        if accion not in self.q_table[estado]:
            self.q_table[estado][accion] = 0.0

        current_q = self.q_table[estado][accion]
        next_max_q = max(self.q_table.get(next_estado, {}).values(), default=0.0)

        # Q-Learning update
        if RUST_AVAILABLE:
            new_q = rust_update_q(
                current_q, reward, next_max_q, self.learning_rate, self.discount_factor
            )
        else:
            new_q = current_q + self.learning_rate * (
                reward + self.discount_factor * next_max_q - current_q
            )

        self.q_table[estado][accion] = new_q
        return new_q

    def _obtener_confianza(self, estado: str, accion: str) -> float:
        """Obtiene confianza en una decisión (0-1)"""
        q_value = self.q_table.get(estado, {}).get(accion, 0.0)
        # Normalizar a 0-1
        return min(max(q_value / 100.0, 0.0), 1.0)

    def _cargar_conocimiento(self) -> Dict:
        """Carga conocimiento desde cache"""
        cached = cache.get("ia_sistema_q_table")
        return json.loads(cached) if cached else {}

    def _guardar_conocimiento(self):
        """Guarda conocimiento en cache"""
        cache.set("ia_sistema_q_table", json.dumps(self.q_table), timeout=None)

    def obtener_estadisticas(self) -> Dict:
        """Estadísticas completas del sistema"""
        return {
            "estado": self.estado,
            "rust_habilitado": RUST_AVAILABLE,
            "total_estados": len(self.q_table),
            "total_acciones": sum(len(actions) for actions in self.q_table.values()),
            "metricas": self.metricas,
            "configuracion": {
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "epsilon": self.epsilon,
            },
        }

    def reiniciar_conocimiento(self) -> Dict:
        """Reinicia el conocimiento (usar con precaución)"""
        old_size = len(self.q_table)
        self.q_table = {}
        self.metricas = {
            "decisiones_totales": 0,
            "decisiones_correctas": 0,
            "recompensa_acumulada": 0.0,
            "precision_actual": 0.0,
            "aprendizajes_web": 0,
        }
        self._guardar_conocimiento()

        return {"mensaje": "Conocimiento reiniciado", "estados_eliminados": old_size}


# Instancia global única
ia_sistema = SistemaIA()
