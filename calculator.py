def calculate_expression(expression):
    try:
        result = eval(expression)
        return result
    except ZeroDivisionError:
        raise ValueError("Błąd: Dzielenie przez zero.")
    except SyntaxError:
        raise ValueError("Błąd: Błędna składnia wyrażenia.")
    except Exception as e:
        raise ValueError("Błąd: " + str(e))