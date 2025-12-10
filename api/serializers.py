from rest_framework import serializers
from .models import Emp, Eq, Tec, PM, OT


class SerBase(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


# Evitamos sobre-ingenieria.
# Usamos el patron de Vistas: variables cortas.
# En Serializers, 'model' en Meta es requerido.


class SerEmp(SerBase):
    class Meta:
        model = Emp
        fields = "__all__"


class SerEq(SerBase):
    class Meta:
        model = Eq
        fields = "__all__"


class SerTec(SerBase):
    class Meta:
        model = Tec
        fields = "__all__"


class SerPM(SerBase):
    class Meta:
        model = PM
        fields = "__all__"


class SerOT(SerBase):
    class Meta:
        model = OT
        fields = "__all__"
