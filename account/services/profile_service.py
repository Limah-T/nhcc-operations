from django.http.request import HttpRequest

def getUserName(request:HttpRequest) -> str:
    return f"{request.user.first_name} {request.user.last_name}".strip()