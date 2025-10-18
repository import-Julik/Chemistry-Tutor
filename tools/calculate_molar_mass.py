# tools/calculate_molar_mass.py
from chempy import Substance

def calculate_molar_mass(formula: str) -> str:
    """
    Рассчитывает молярную массу по химической формуле.
    Пример: calculate_molar_mass("C6H12O6") → "180.16 г/моль"
    """
    try:
        substance = Substance.from_formula(formula)
        mass = substance.molar_mass() 
        return f"{mass * 1000:.2f} г/моль"
    except Exception as e:
        return f"Ошибка при расчёте молярной массы: {str(e)}"