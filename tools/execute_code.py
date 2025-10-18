# tools/execute_code.py
from asteval import Interpreter

def execute_code(code: str) -> str:
    """
    Безопасно выполняет Python-код, содержащий математические вычисления.
    Поддерживает переменные, арифметику, print().
    Пример: "grams_CH4 = 25; moles_CH4 = grams_CH4 / 16.04; moles_H2O = moles_CH4 * 2; grams_H2O = moles_H2O * 18.02; print(grams_H2O)"
    """
    try:
        aeval = Interpreter()
        output = []
        def safe_print(*args):
            output.append(" ".join(str(arg) for arg in args))
        aeval.symtable["print"] = safe_print

        aeval(code)
        result = "\n".join(output) if output else str(aeval.symtable.get("result", ""))
        return result if result else "Код выполнен, но ничего не выведено."
    except Exception as e:
        return f"Ошибка выполнения кода: {str(e)}"