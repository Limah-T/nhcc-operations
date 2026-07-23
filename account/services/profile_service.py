from account.models import CustomUser

def getFullName(user:CustomUser) -> str:
    return f"{user.first_name} {user.last_name}".strip()

def getNameAvatar(user:CustomUser) -> str:
    return user.first_name[0]+user.last_name[0]