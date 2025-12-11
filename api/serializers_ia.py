from rest_framework import serializers
from .models import DatoEntrenamiento, ModeloIA


class DatoEntrenamientoSerializer(serializers.ModelSerializer):
    """Serializer para datos de entrenamiento"""

    class Meta:
        model = DatoEntrenamiento
        fields = "__all__"


class ModeloIASerializer(serializers.ModelSerializer):
    """Serializer para modelo de IA"""

    precision_porcentaje = serializers.SerializerMethodField()

    def get_precision_porcentaje(self, obj):
        return f"{obj.precision_actual * 100:.2f}%"

    class Meta:
        model = ModeloIA
        fields = "__all__"
