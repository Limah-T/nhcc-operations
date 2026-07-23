

def intId(pk) -> bool:
    return True if isinstance(pk, int) else False

def emptyFields(fields:dict) -> bool:
    if all(value is None or value == [] for key,value in fields.values()):
        return True
    return False

def getSingleData(request, value):
    return request.POST.get(value, None)

def getBulkData(request, value):
    return request.POST.getlist(value, [])

server_error = "An error occurred, please try again later"
queue_error = "Another device is processing this request."
ekedc_404 = "Electricity record not found."
diesel_404 = "Diesel record not found."
expense_404 = "Expense record not found."
category_404 = "Category record not found."
role_404 = "Role(s) record not found."
staff_404 = "Staff record not found."
no_changes = "Nothing to update"

empty_fields_error = "All fields are empty"
invalid_name_error = "Only letters, numbers, '.', and ',' are allowed."