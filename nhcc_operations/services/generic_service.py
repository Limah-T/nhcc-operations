

def intId(pk) -> bool:
    return True if isinstance(pk, int) else False

def emptyFields(fields:list) -> bool:
    if all(value is None for value in fields):
        return True
    return False

def custom_form_errors(queryset, form, value, message:list) -> dict:
    return {
        "records": queryset, 
        "count": queryset.count(),
        "form": form,
        "errors":[
        {"value": value, 
            "errors": {"name": message}
        }]
    }

server_error = {"error":["An error occurred, please try again later"]}