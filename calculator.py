def calculate_expression(expression):
    try:
        result = eval(expression)
        return result
    except Exception as e:
        return "Błąd: " + str(e)
