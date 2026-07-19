

def intId(pk) -> bool:
    return True if isinstance(pk, int) else False

def emptyFields(fields:list) -> bool:
    if all(value is None or value == [] for value in fields):
        return True
    return False

   

server_error = {"error":["An error occurred, please try again later"], "status":500}
queue_error = {"error": ["Another device is processing this request."], "status":400}
ekedc_404 = {"error": ["Electricity record not found."], "status":404}
diesel_404 = {"error": ["Diesel record not found."], "status":404}
expense_404 = {"error": ["Expense record not found."], "status":404}