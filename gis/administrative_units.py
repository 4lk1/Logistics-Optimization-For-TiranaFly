from typing import List, Dict

class AdministrativeUnits:
    """
    Registry and metadata for the 14 real administrative units of Tirana.
    Includes the 11 urban units and 3 major suburban units (Kashar, Farkë, Dajt).
    """
    
    UNITS = [
        "Njësia 1", "Njësia 2", "Njësia 3", "Njësia 4", "Njësia 5",
        "Njësia 6", "Njësia 7", "Njësia 8", "Njësia 9", "Njësia 10",
        "Njësia 11", "Kashar", "Farkë", "Dajt"
    ]

    # Estimated population distribution based on 2023 census total (807,029)
    # This is used as a fallback or for initializing the mapping logic.
    POPULATION_ESTIMATES = {
        "Njësia 1": 50000,
        "Njësia 2": 70000,
        "Njësia 3": 40000,
        "Njësia 4": 60000,
        "Njësia 5": 80000,
        "Njësia 6": 60000,
        "Njësia 7": 65000,
        "Njësia 8": 35000,
        "Njësia 9": 50000,
        "Njësia 10": 25000,
        "Njësia 11": 65000,
        "Kashar": 80000,
        "Farkë": 35000,
        "Dajt": 92029  # Adjusted to match total exactly: 807,029
    }

    @classmethod
    def get_all_units(cls) -> List[str]:
        return cls.UNITS

    @classmethod
    def get_population(cls, unit_name: str) -> int:
        return cls.POPULATION_ESTIMATES.get(unit_name, 0)

    @classmethod
    def get_total_population(cls) -> int:
        return sum(cls.POPULATION_ESTIMATES.values())
