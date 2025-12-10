from rest_framework import serializers
from .models import Company, Equipment, Technician, MaintenancePlan, WorkOrder


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company

        fields = "__all__"


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment

        fields = "__all__"


class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician

        fields = "__all__"
    

class MaintenancePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenancePlan

        fields = "__all__"


class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder

        fields = "__all__"
