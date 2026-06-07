from typing import Dict, Any, List

class ScenarioManager:
    """Manages predefined simulation scenarios and configurations."""
    
    SCENARIOS = {
        "baseline": {
            "name": "Baseline Operations",
            "global_multiplier": 1.0,
            "is_holiday": False,
            "is_emergency": False,
            "p_failure_multiplier": 1.0
        },
        "black_friday": {
            "name": "Black Friday Demand Surge",
            "global_multiplier": 3.5,
            "is_holiday": True,
            "is_emergency": False,
            "p_failure_multiplier": 1.2
        },
        "severe_storm": {
            "name": "Severe Weather Impact",
            "global_multiplier": 0.8,
            "is_holiday": False,
            "is_emergency": False,
            "forced_weather_condition": "STORM",
            "p_failure_multiplier": 2.5
        },
        "emergency_medical": {
            "name": "Emergency Medical Response",
            "global_multiplier": 1.5,
            "is_holiday": False,
            "is_emergency": True,
            "p_failure_multiplier": 1.0
        },
        "population_growth_2030": {
            "name": "Tirana 2030 (Population +20%)",
            "global_multiplier": 1.2,
            "population_growth_years": 5,
            "p_failure_multiplier": 1.1
        }
    }

    @classmethod
    def get_scenario(cls, key: str) -> Dict[str, Any]:
        return cls.SCENARIOS.get(key, cls.SCENARIOS["baseline"])

    @classmethod
    def list_scenarios(cls) -> List[str]:
        return list(cls.SCENARIOS.keys())
