from typing import Dict, Any, Optional

GROUNDING_EXERCISES: Dict[str, Dict[str, Any]] = {
    "box_breathing": {
        "title": "Box Breathing (4-4-4-4)",
        "category": "Breathing",
        "steps": [
            {"phase": "Inhale", "duration_seconds": 4, "instruction": "Breathe in deeply through your nose"},
            {"phase": "Hold", "duration_seconds": 4, "instruction": "Hold gently with full lungs"},
            {"phase": "Exhale", "duration_seconds": 4, "instruction": "Breathe out smoothly through your mouth"},
            {"phase": "Hold", "duration_seconds": 4, "instruction": "Pause and rest with empty lungs"}
        ],
        "rounds": 4,
        "purpose": "Calms the nervous system and lowers heart rate during acute stress."
    },
    "5_4_3_2_1": {
        "title": "5-4-3-2-1 Sensory Grounding",
        "category": "Mindfulness",
        "steps": [
            {"sense": "See", "count": 5, "instruction": "Notice 5 objects you can see around you"},
            {"sense": "Touch", "count": 4, "instruction": "Notice 4 physical textures or contact points"},
            {"sense": "Hear", "count": 3, "instruction": "Listen for 3 distinct ambient sounds"},
            {"sense": "Smell", "count": 2, "instruction": "Identify 2 scents or take two deep breaths"},
            {"sense": "Taste", "count": 1, "instruction": "Focus on 1 lingering taste or sip cold water"}
        ],
        "purpose": "Anchors overwhelming thoughts back into the physical present moment."
    },
    "4_7_8_breathing": {
        "title": "4-7-8 Relaxing Breath",
        "category": "Breathing",
        "steps": [
            {"phase": "Inhale", "duration_seconds": 4, "instruction": "Inhale quietly through your nose"},
            {"phase": "Hold", "duration_seconds": 7, "instruction": "Hold your breath calmly"},
            {"phase": "Exhale", "duration_seconds": 8, "instruction": "Exhale completely making a whooshing sound"}
        ],
        "rounds": 4,
        "purpose": "Promotes deep parasympathetic relaxation and sleep readiness."
    }
}

class GroundingService:
    """Provides structured grounding templates for interactive UI cards."""

    @staticmethod
    def detect_grounding_opportunity(text: str) -> Optional[str]:
        """Checks if user is specifically requesting or would benefit from a grounding exercise."""
        lower = text.lower()
        if "box breath" in lower or "square breath" in lower:
            return "box_breathing"
        if "5-4-3-2-1" in lower or "54321" in lower or "sensory ground" in lower:
            return "5_4_3_2_1"
        if "4-7-8" in lower or "478" in lower:
            return "4_7_8_breathing"
        if "grounding exercise" in lower or "help me calm down" in lower or "breathing exercise" in lower:
            return "box_breathing"
        return None

    @staticmethod
    def get_exercise_details(card_type: str) -> Optional[Dict[str, Any]]:
        return GROUNDING_EXERCISES.get(card_type)
