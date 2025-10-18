# main.py
import os
import re
import json
import time
import requests
from dotenv import load_dotenv
from tools import TOOL_FUNCTIONS

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY не найден в .env")

MODEL = "mistralai/mistral-7b-instruct:free"
#MODEL = "qwen/qwen3-235b-a22b:free"

def call_llm(messages):
    """Вызывает LLM через OpenRouter."""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",  
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:8502",
                "X-Title": "Chemistry Tutor"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.1
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            return f"Ошибка OpenRouter (HTTP {e.response.status_code}): {e.response.text}"
        return f"Ошибка сети: {str(e)}"
    except Exception as e:
        return f"Неизвестная ошибка: {str(e)}"


def parse_action(text: str):
    """
    Извлекает JSON из строки вида:
    Action: {"name": "...", "args": {...}}
    """
    action_match = re.search(r"Action:\s*(.*)", text, re.DOTALL)
    if not action_match:
        return None

    json_candidate = action_match.group(1).strip()
    brace_count = 0
    cut_pos = 0
    in_string = False
    escaped = False
    for i, char in enumerate(json_candidate):
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == '"' and not escaped:
            in_string = not in_string
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    cut_pos = i + 1
                    break

    json_str = json_candidate[:cut_pos] if cut_pos > 0 else json_candidate
    json_str = json_str.strip().rstrip('.,')
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def run_chemistry_tutor(query: str, max_steps=8) -> str:
    tools_desc_lines = []
    for name, func in TOOL_FUNCTIONS.items():
        doc = func.__doc__.strip() if func.__doc__ else "Инструмент для химических расчётов"
        tools_desc_lines.append(f"- {name}: {doc}")
    tools_desc = "\n".join(tools_desc_lines)

    system_prompt = f"""Ты — компетентный AI-тьютор по химии для старшеклассников и студентов.
Ты ОБЯЗАН использовать ТОЛЬКО доступные инструменты для получения точных данных.
НИКОГДА не выдумывай молярные массы, коэффициенты, продукты реакции или свойства веществ.

Доступные инструменты:
{tools_desc}

### Как решать задачи:
- **Балансировка**: если дано уравнение с "->", вызови `balance_equation`.
- **Молярная масса**: если спрашивают массу вещества по формуле — `calculate_molar_mass`.
- **Свойства элемента/иона/соединения**: 
  - Для элементов (Au, железо, O) → `get_element_properties`
  - Для ионов (MnO4-, SO4^2-) → `get_ion_info`
  - Для молекул (H2SO4, глюкоза) → `get_compound_info`
- **Стехиометрия (расчёт по уравнению)**: если вопрос вида "сколько ... получится из ...", следуй алгоритму:

#### 🔄 Универсальный алгоритм стехиометрии:
1. **Определи реагенты** из вопроса.
2. **Если продукты неизвестны**, вызови `predict_reaction_products` с:
   - `reactants`: список реагентов через запятую (например, "CH4, O2")
   - `context`: тип реакции (например, "сгорание", "нейтрализация", "в кислоте")
3. **Собери полное уравнение**: реагенты + "->" + продукты из шага 2.
4. **Сбалансируй уравнение** → вызови `balance_equation`.
5. **Найди молярные массы** всех участвующих веществ → вызови `calculate_molar_mass` для каждого.
6. **Выполни расчёт** через `execute_code`, используя:
   - граммы → моли (масса / молярная масса)
   - моли → моли (по коэффициентам из сбалансированного уравнения)
   - моли → граммы (моль × молярная масса)

### ❗ Правила формата ОТВЕТА:
1. Начни с **"Thought:"** — опиши ТОЛЬКО ОДИН следующий шаг.
2. Если нужен инструмент, напиши **ТОЛЬКО ОДНУ строку**:
   Action: {{"name": "имя_инструмента", "args": {{"параметр": "значение"}}}}
3. **Сразу после Action — НИЧЕГО НЕ ПИШИ**. Не добавляй пояснений, точек, новых строк.
4. После получения результата (Observation) повтори цикл.
5. Финальный ответ начни с **"Answer:"**.

⚠️ ЗАПРЕЩЕНО:
- Вызывать несколько инструментов в одном Action.
- Делать вычисления без `execute_code`.
- Предполагать продукты без `predict_reaction_products`.
- Пропускать шаги (например, балансировку или молярные массы).

Теперь ответь на вопрос:
Вопрос: {query}
"""

    messages = [{"role": "user", "content": system_prompt}]
    
    for step in range(max_steps):
        response = call_llm(messages)
        messages.append({"role": "assistant", "content": response})

        action = parse_action(response)
        if action:
            name = action.get("name")
            args = action.get("args", {})
            if name in TOOL_FUNCTIONS:
                try:
                    result = TOOL_FUNCTIONS[name](**args)
                except Exception as e:
                    result = f"Ошибка выполнения инструмента: {str(e)}"
                messages.append({
                    "role": "user",
                    "content": f"\nObservation: {result}\n"
                })
                continue
            else:
                messages.append({
                    "role": "user",
                    "content": f"\nObservation: Ошибка: неизвестный инструмент '{name}'\n"
                })
                continue
        else:
            text = response.strip()
            if "Answer:" in text:
                return text.split("Answer:", 1)[1].strip()
            return text.replace("<s>", "").strip()

    return "Не удалось получить ответ за отведённое число шагов."

if __name__ == "__main__":
    print("ТЕСТ 1: Балансировка")
    print(run_chemistry_tutor("Сбалансируй уравнение: Fe + O2 -> Fe2O3"))
    print("\n" + "="*50 + "\n")

    print("ТЕСТ 2: Молярная масса")
    print(run_chemistry_tutor("Какая молярная масса у серной кислоты (H2SO4)?"))
    print("\n" + "="*50 + "\n")

    print("ТЕСТ 3: Свойства элемента")
    print(run_chemistry_tutor("Расскажи о золоте"))
    print("\n" + "="*50 + "\n")

    print("ТЕСТ 4: Стехиометрия")
    print(run_chemistry_tutor("Сколько граммов воды получится при сжигании 2 граммов водорода (H2) в избытке кислорода?"))