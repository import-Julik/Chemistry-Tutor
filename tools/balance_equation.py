# tools/balance_equation.py
from chempy import balance_stoichiometry
from chempy.util.parsing import formula_to_composition
import re

def normalize_formula(formula: str) -> str:
    """Преобразует CH₄ → CH4, Fe₂O₃ → Fe2O3 и т.д."""
    subscript_map = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    return formula.translate(subscript_map)

def parse_reaction(reaction_str: str) -> tuple[list[str], list[str]]:
    reaction_str = normalize_formula(reaction_str)
    reaction_str = re.sub(r'\s+', '', reaction_str)  
    if "->" not in reaction_str:
        raise ValueError("Реакция должна содержать '->'")
    left, right = reaction_str.split("->", 1)
    reactants = [r for r in left.split("+") if r]
    products = [p for p in right.split("+") if p]
    return reactants, products

def format_balanced_equation(reactants, products, coeffs_react, coeffs_prod):
    """Форматирует сбалансированное уравнение в строку."""
    left = " + ".join(f"{coeffs_react[r]}{r}" if coeffs_react[r] > 1 else r for r in reactants)
    right = " + ".join(f"{coeffs_prod[p]}{p}" if coeffs_prod[p] > 1 else p for p in products)
    return f"{left} -> {right}"

def balance_equation(reaction: str) -> str:
    """
    Балансирует химическое уравнение.
    Пример: balance_equation("KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2")
    """
    try:
        reactants, products = parse_reaction(reaction)
        coeffs_react, coeffs_prod = balance_stoichiometry(reactants, products)
        return format_balanced_equation(reactants, products, coeffs_react, coeffs_prod)
    except Exception as e:
        return f"Ошибка при балансировке: {str(e)}"