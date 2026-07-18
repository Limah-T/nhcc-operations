from django.http.request import HttpRequest

def getFullName(request:HttpRequest) -> str:
    return f"{request.user.first_name} {request.user.last_name}".strip()

def getNameAvatar(request:HttpRequest) -> str:
    return request.user.first_name[0]+request.user.last_name[0]