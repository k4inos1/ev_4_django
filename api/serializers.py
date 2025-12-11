from rest_framework import serializers
from .models import Equipo, Mantenimiento, Recurso, Evento, DatoEntrenamiento, ModeloIA


class EquipoSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(
        source="get_categoria_display", read_only=True
    )

    class Meta:
        model = Equipo
        fields = "__all__"


class MantenimientoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    prioridad_display = serializers.CharField(
        source="get_prioridad_display", read_only=True
    )
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)

    class Meta:
        model = Mantenimiento
        fields = "__all__"


class RecursoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    necesita_reposicion = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recurso
        fields = "__all__"


class EventoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    equipo_nombre = serializers.CharField(
        source="equipo.nombre", read_only=True, allow_null=True
    )

    class Meta:
        model = Evento
        fields = "__all__"


class DatoEntrenamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatoEntrenamiento
        fields = "__all__"


class ModeloIASerializer(serializers.ModelSerializer):
    precision_porcentaje = serializers.SerializerMethodField()

    def get_precision_porcentaje(self, obj):
        return f"{obj.precision_actual * 100:.2f}%"

    class Meta:
        model = ModeloIA
        fields = "__all__"
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

# Serializers para nuevos modelos
class RecomendacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recomendacion
        fields = '__all__'
