# tools/predict_reaction_products.py
import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct:free"  
def call_llm_for_prediction(prompt: str) -> str:
    """Вызывает ту же LLM, что и основной цикл, но только для предсказания продуктов."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:8502",
                "X-Title": "Chemistry Tutor - Reaction Predictor"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.0 
            },
            timeout=15
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        return text
    except Exception as e:
        return f"Ошибка предсказания: {str(e)}"

def clean_formula(formula: str) -> str:
    """Приводит формулу к стандартному виду: CH₄ → CH4"""
    return formula.translate(str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")).strip()

def predict_reaction_products(reactants: str, context: str = "") -> str:
    """
    Предсказывает продукты химической реакции с помощью few-shot prompting.
    
    Аргументы:
        reactants (str): Список реагентов через запятую, например: "CH4, O2"
        context (str): Дополнительный контекст, например: "сгорание", "в водном растворе"
    
    Возвращает:
        str: Продукты реакции в виде строки, например: "CO2 + H2O"
    """
    reactants_clean = ", ".join(clean_formula(r) for r in reactants.split(","))
    context_clean = context.strip() if context else "не указан"
    prompt = f"""Ты — эксперт-химик. Предскажи **только продукты** химической реакции на основе реагентов и контекста.
Следуй правилам школьной и вузовской химии. Не выдумывай несуществующие вещества.

### Примеры:
Реагенты: H2, O2 | Контекст: сгорание → Продукты: H2O
Реагенты: CH4, O2 | Контекст: сгорание → Продукты: CO2 + H2O
Реагенты: C2H5OH, O2 | Контекст: сгорание → Продукты: CO2 + H2O
Реагенты: HCl, NaOH | Контекст: нейтрализация → Продукты: NaCl + H2O
Реагенты: Zn, H2SO4 | Контекст: реакция металла с кислотой → Продукты: ZnSO4 + H2
Реагенты: CaCO3 | Контекст: термическое разложение → Продукты: CaO + CO2
Реагенты: Fe, O2 | Контекст: окисление → Продукты: Fe2O3
Реагенты: NH3, HCl | Контекст: газовая реакция → Продукты: NH4Cl

### Теперь твоя очередь:
Реагенты: {reactants_clean} | Контекст: {context_clean} → Продукты:"""

    raw_output = call_llm_for_prediction(prompt)
    if "→ Продукты:" in raw_output:
        raw_output = raw_output.split("→ Продукты:", 1)[1].strip()
    
    cleaned = re.sub(r"[^A-Za-z0-9+\s\-]", "", raw_output)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned or len(cleaned) < 2:
        return "Неизвестные продукты"
    
    return cleaned