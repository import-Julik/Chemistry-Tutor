# tools/__init__.py
from .balance_equation import balance_equation
from .calculate_molar_mass import calculate_molar_mass
from .get_element_info import get_element_info
from .execute_code import execute_code
from .predict_reaction_products import predict_reaction_products

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "balance_equation",
            "description": "Сбалансируй химическое уравнение. Пример ввода: 'H2 + O2 -> H2O'",
            "parameters": {
                "type": "object",
                "properties": {
                    "reaction": {
                        "type": "string",
                        "description": "Химическая реакция в виде строки, например: 'KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2'"
                    }
                },
                "required": ["reaction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_molar_mass",
            "description": "Рассчитай молярную массу вещества по его химической формуле.",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {
                        "type": "string",
                        "description": "Химическая формула, например: 'NaCl', 'C6H12O6'"
                    }
                },
                "required": ["formula"]
            }
        }
    }
]


TOOL_FUNCTIONS = {
    "balance_equation": balance_equation,
    "calculate_molar_mass": calculate_molar_mass,
    "get_element_info": get_element_info,
    "execute_code": execute_code,
    "predict_reaction_products": predict_reaction_products,
}