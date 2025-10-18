# tools/get_element_info.py

from mendeleev import element
import pubchempy as pcp
import re
import time

def normalize_query(query: str) -> str:
    """Очищает запрос: убирает 'ион', 'элемент', нижние индексы и т.д."""
    query = query.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789"))
    query = re.sub(r'\s*(ион|иона|ионы|элемент|вещество)\s*', '', query, flags=re.IGNORECASE)
    return query.strip()

def get_element_info(query: str) -> str:
    """
    Получает информацию о веществе из Mendeleev (элементы) и PubChem (всё остальное).
    Поддерживает: элементы, ионы, молекулы, соли.
    Примеры: 'золото', 'Au', 'перманганат', 'MnO4', 'H2SO4'
    """
    original_query = query
    query = normalize_query(query)
    
    if not query:
        return "Пустой запрос."
    try:
        elem = element(query)
        return (
            f"🔹 **Элемент**: {elem.name} ({elem.symbol})\n"
            f"• Атомный номер: {elem.atomic_number}\n"
            f"• Атомная масса: {elem.atomic_weight:.2f} г/моль\n"
            f"• Плотность: {elem.density:.2f} г/см³\n"
            f"• Температура плавления: {elem.melting_point:.0f} K ({elem.melting_point - 273.15:.0f} °C)\n"
            f"• Температура кипения: {elem.boiling_point:.0f} K ({elem.boiling_point - 273.15:.0f} °C)"
        )
    except Exception:
        pass  
    try:
        time.sleep(0.5)
        compounds = pcp.get_compounds(query, 'name')
        if not compounds:
            compounds = pcp.get_compounds(query, 'formula')
        
        if not compounds:
            return f"Вещество '{original_query}' не найдено в базах данных."

        comp = compounds[0] 
        lines = [f"🔹 **{comp.iupac_name or comp.synonyms[0] if comp.synonyms else query}**"]
        
        if comp.molecular_formula:
            lines.append(f"• Формула: {comp.molecular_formula}")
        if comp.molecular_weight:
            lines.append(f"• Молярная масса: {comp.molecular_weight:.2f} г/моль")
        if hasattr(comp, 'charge') and comp.charge is not None:
            charge = comp.charge
            if charge == 0:
                lines.append("• Заряд: нейтральное вещество")
            else:
                lines.append(f"• Заряд: {charge:+d}")

        if comp.charge != 0:
            lines.insert(1, "• Тип: ион")
        
        return "\n".join(lines)

    except pcp.PubChemHTTPError as e:
        if "PUGREST.NotFound" in str(e):
            return f"Вещество '{original_query}' не найдено в PubChem."
        else:
            return f"Ошибка PubChem: {str(e)}"
    except Exception as e:
        return f"Ошибка при запросе к базе данных: {str(e)}"