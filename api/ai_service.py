import re
from django.db.models import Count, Q
from .models import Technician, WorkOrder
from .constants import (
    PRIORITY_KEYWORDS,
    THRESHOLD_HIGH,
    THRESHOLD_MEDIUM,
    WorkOrderPriority,
    TechnicianSpecialty,
    WorkOrderStatus,
)


class AIService:
    """
    Intelligent Service for analyzing Work Orders and recommending resources.
    Uses heuristic algorithms and keyword analysis to simulate AI behavior.
    """

    @classmethod
    def analyze_priority(cls, notes: str) -> str:
        """
        Analyzes the text notes to determine the recommended priority.
        Algorithm:
        1. Tokenize and normalize text.
        2. Calculate scores for High and Medium categories based on keyword weighting.
        3. Return the highest scoring category, defaulting to MEDIA.
        """
        if not notes:
            return WorkOrderPriority.MEDIA

        normalized_text = notes.lower()
        score_high = 0
        score_medium = 0

        # Calculate High Priority Score
        for word, weight in PRIORITY_KEYWORDS[WorkOrderPriority.ALTA]:
            if word in normalized_text:
                score_high += weight

        # Calculate Medium Priority Score
        for word, weight in PRIORITY_KEYWORDS[WorkOrderPriority.MEDIA]:
            if word in normalized_text:
                score_medium += weight

        # Decision Logic
        if score_high >= THRESHOLD_HIGH:
            return WorkOrderPriority.ALTA
        elif score_high > 0 or score_medium >= THRESHOLD_MEDIUM:
            return WorkOrderPriority.MEDIA

        return WorkOrderPriority.BAJA

    @classmethod
    def recommend_technician(cls, equipment_category: str) -> dict:
        """
        Recommends the best available technician for a specific equipment category.
        """
        # 1. Filter by Specialty
        candidates = Technician.objects.filter(
            Q(especialidad=equipment_category)
            | Q(especialidad=TechnicianSpecialty.GENERAL)
        )

        if not candidates.exists():
            return None

        # 2. Load Balancing (Complex Query)
        # Count active work orders for each candidate
        candidates = candidates.annotate(
            active_load=Count(
                "workorder",
                filter=Q(
                    workorder__estado__in=[
                        WorkOrderStatus.PENDING,
                        WorkOrderStatus.IN_PROGRESS,
                    ]
                ),
            )
        ).order_by("active_load", "nombre")

        # 3. Select best candidate
        best_match = candidates.first()

        return {
            "technician_id": best_match.id,
            "name": best_match.nombre,
            "specialty": best_match.especialidad,
            "current_load": best_match.active_load,
            "reason": f"Best match for {equipment_category} with lowest active load ({best_match.active_load} orders).",
        }
