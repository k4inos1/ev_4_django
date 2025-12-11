import time
import threading
import numpy as np
from datetime import datetime
from django.db.models import Count, Q
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

from api.constants import (
    CATEGORIA_GENERAL,
    ESTADO_PENDIENTE,
    ESTADO_EN_PROGRESO,
    PALABRAS_CLAVE_PRIORIDAD,
    PRIORIDAD_ALTA,
    PRIORIDAD_BAJA,
    PRIORIDAD_MEDIA,
    UMBRAL_PRIORIDAD_ALTA,
    UMBRAL_PRIORIDAD_MEDIA,
)


class ServicioIA:
    """Servicio de Inteligencia Artificial para el sistema"""

    # Estado del entrenamiento
    _training_state = {
        "status": "idle",
        "epoch": 0,
        "total_epochs": 0,
        "current_step": "ninguno",
        "metrics": {
            "train_acc": [],
            "val_acc": [],
            "test_acc": 0.0,
        },
        "logs": [],
        "model": None,
        "pipeline_steps": [
            {"id": 1, "name": "Conjunto de Datos Crudos", "status": "pending"},
            {"id": 2, "name": "Limpieza de Datos", "status": "pending"},
            {"id": 3, "name": "Ingeniería de Características", "status": "pending"},
            {"id": 4, "name": "División Estratificada", "status": "pending"},
            {"id": 5, "name": "Análisis de Entrenamiento", "status": "pending"},
            {"id": 6, "name": "Análisis de Validación", "status": "pending"},
            {"id": 7, "name": "Análisis de Prueba", "status": "pending"},
        ],
    }
    _stop_training = False
    _training_thread = None

    @staticmethod
    def calcular_prioridad(texto: str) -> int:
        """Calcula la prioridad basándose en palabras clave"""
        texto_lower = texto.lower()
        score = 0

        for palabra in PALABRAS_CLAVE_PRIORIDAD:
            if palabra in texto_lower:
                score += 10

        if score >= UMBRAL_PRIORIDAD_ALTA:
            return PRIORIDAD_ALTA
        elif score >= UMBRAL_PRIORIDAD_MEDIA:
            return PRIORIDAD_MEDIA
        else:
            return PRIORIDAD_BAJA

    @staticmethod
    def buscar_tecnico(especialidad: str = None) -> dict:
        """Busca un técnico disponible (simulado con recursos)"""
        from api.models import Recurso

        recursos_tecnicos = Recurso.objects.filter(
            tipo=Recurso.TIPO_TECNICO, disponible=True
        )

        if especialidad:
            recursos_tecnicos = recursos_tecnicos.filter(especialidad=especialidad)

        if recursos_tecnicos.exists():
            tecnico = recursos_tecnicos.order_by("-calificacion").first()
            return {
                "nombre": tecnico.nombre,
                "especialidad": tecnico.especialidad,
                "calificacion": tecnico.calificacion,
            }

        return {"nombre": "No disponible", "especialidad": "N/A", "calificacion": 0}

    @staticmethod
    def _log(mensaje: str):
        """Agrega un log con timestamp"""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        log_msg = f"{timestamp} {mensaje}"
        ServicioIA._training_state["logs"].append(log_msg)
        # print removed

    @staticmethod
    def _update_step(step_id: int, status: str):
        """Actualiza el estado de un paso del pipeline"""
        for step in ServicioIA._training_state["pipeline_steps"]:
            if step["id"] == step_id:
                step["status"] = status
                break

    @staticmethod
    def _generar_datos_sinteticos(n_samples: int = 1000):
        """Genera datos sintéticos para entrenamiento"""
        np.random.seed(42)

        X = np.random.randn(n_samples, 10)
        y = np.random.choice(
            [PRIORIDAD_BAJA, PRIORIDAD_MEDIA, PRIORIDAD_ALTA], n_samples
        )

        return X, y

    @staticmethod
    def _limpiar_datos(X, y):
        """Limpia los datos eliminando valores nulos"""
        mask = ~np.isnan(X).any(axis=1)
        return X[mask], y[mask]

    @staticmethod
    def _ingenieria_caracteristicas(X):
        """Aplica ingeniería de características"""
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return X_scaled, scaler

    @staticmethod
    def _dividir_datos(X, y):
        """Divide los datos en train/val/test"""
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
        )

        return X_train, X_val, X_test, y_train, y_val, y_test

    @staticmethod
    def _evaluar_modelo(model, X_test, y_test):
        """Evalúa el modelo en el conjunto de prueba"""
        y_pred = model.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred)

        ServicioIA._training_state["metrics"]["test_acc"] = float(test_acc)
        ServicioIA._log(f"Precisión en conjunto de prueba: {test_acc:.4f}")

        return test_acc

    @staticmethod
    def _entrenar_modelo_thread(epochs: int, n_samples: int):
        """Hilo de entrenamiento del modelo"""
        try:
            ServicioIA._training_state["status"] = "training"
            ServicioIA._training_state["total_epochs"] = epochs
            ServicioIA._log("Iniciando entrenamiento del modelo...")

            # Fase A: Preparación de datos
            ServicioIA._update_step(1, "in_progress")
            X, y = ServicioIA._generar_datos_sinteticos(n_samples)
            ServicioIA._update_step(1, "completed")

            ServicioIA._update_step(2, "in_progress")
            X, y = ServicioIA._limpiar_datos(X, y)
            ServicioIA._update_step(2, "completed")

            ServicioIA._update_step(3, "in_progress")
            X_scaled, scaler = ServicioIA._ingenieria_caracteristicas(X)
            ServicioIA._update_step(3, "completed")

            ServicioIA._update_step(4, "in_progress")
            X_train, X_val, X_test, y_train, y_val, y_test = ServicioIA._dividir_datos(
                X_scaled, y
            )
            ServicioIA._update_step(4, "completed")

            # Fase B/C: Entrenamiento
            model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42
            )

            for epoch in range(epochs):
                if ServicioIA._stop_training:
                    break

                ServicioIA._training_state["epoch"] = epoch + 1
                ServicioIA._update_step(5, "in_progress")

                model.fit(X_train, y_train)

                train_pred = model.predict(X_train)
                train_acc = accuracy_score(y_train, train_pred)

                ServicioIA._update_step(6, "in_progress")
                val_pred = model.predict(X_val)
                val_acc = accuracy_score(y_val, val_pred)

                ServicioIA._training_state["metrics"]["train_acc"].append(
                    float(train_acc)
                )
                ServicioIA._training_state["metrics"]["val_acc"].append(float(val_acc))

                ServicioIA._log(
                    f"Época {epoch+1}/{epochs} - Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}"
                )

                time.sleep(0.5)

            ServicioIA._update_step(5, "completed")
            ServicioIA._update_step(6, "completed")

            # Fase D: Evaluación
            ServicioIA._update_step(7, "in_progress")
            ServicioIA._evaluar_modelo(model, X_test, y_test)
            ServicioIA._update_step(7, "completed")

            ServicioIA._training_state["model"] = model
            ServicioIA._training_state["status"] = "completed"
            ServicioIA._log("Entrenamiento completado exitosamente")

            # Actualizar modelo en BD
            from api.models import ModeloIA

            modelo_ia = ModeloIA.objects.filter(activo=True).first()
            if modelo_ia:
                modelo_ia.precision_actual = ServicioIA._training_state["metrics"][
                    "test_acc"
                ]
                modelo_ia.epocas_completadas = epochs
                modelo_ia.historial_metricas = ServicioIA._training_state["metrics"][
                    "val_acc"
                ]
                modelo_ia.estado = "completed"
                modelo_ia.save()

        except Exception as e:
            ServicioIA._training_state["status"] = "error"
            ServicioIA._log(f"Error en entrenamiento: {str(e)}")

    @staticmethod
    def iniciar_entrenamiento(epochs: int = 10, n_samples: int = 1000):
        """Inicia el entrenamiento del modelo en un hilo separado"""
        if ServicioIA._training_state["status"] == "training":
            return {
                "status": "ya_entrenando",
                "mensaje": "Ya hay un entrenamiento en progreso",
            }

        ServicioIA._stop_training = False
        ServicioIA._training_state["metrics"] = {
            "train_acc": [],
            "val_acc": [],
            "test_acc": 0.0,
        }
        ServicioIA._training_state["logs"] = []

        for step in ServicioIA._training_state["pipeline_steps"]:
            step["status"] = "pending"

        ServicioIA._training_thread = threading.Thread(
            target=ServicioIA._entrenar_modelo_thread, args=(epochs, n_samples)
        )
        ServicioIA._training_thread.start()

        return {"status": "iniciado", "epochs": epochs}

    @staticmethod
    def detener_entrenamiento():
        """Detiene el entrenamiento en progreso"""
        ServicioIA._stop_training = True
        return {"status": "deteniendo"}

    @staticmethod
    def obtener_metricas():
        """Obtiene las métricas actuales del entrenamiento"""
        return {
            "status": ServicioIA._training_state["status"],
            "epoch": ServicioIA._training_state["epoch"],
            "total_epochs": ServicioIA._training_state["total_epochs"],
            "current_step": ServicioIA._training_state["current_step"],
            "metrics": ServicioIA._training_state["metrics"],
            "logs": ServicioIA._training_state["logs"],
            "pipeline_steps": ServicioIA._training_state["pipeline_steps"],
        }

