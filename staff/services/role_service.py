from ..models import Role
from django.db import transaction, IntegrityError, DatabaseError
from django.db.models import ProtectedError
from nhcc_operations.services.generic_service import server_error, queue_error, role_404
from ..forms import RoleForm

def roleRetrieval(pk) -> Role | None:
    return Role.objects.filter(id=pk).first()

def roleQueryset() -> Role:
    return Role.objects.all().order_by("name")

def roleFormValidator(roles:list) -> RoleForm | list:
    role_list = []
    for role in roles:
        form = RoleForm(data={"name":role})
        if not form.is_valid():
            return form
        role_list.append(form.cleaned_data["name"])
    return role_list

def newRoles(roles:list) -> set | None:
    existing_roles = set(Role.objects.filter(
        name__in=roles).values_list("name", flat=True))
    if len(existing_roles) == len(roles):
        return None
    new_roles = set(roles) - existing_roles
    return new_roles
    
def prepareCreate(roles:list, data) -> list:
    new_data = []
    for role in roles:
        new_data.append(
            Role(
                name=role, 
                created_by_user=data["user"],
                created_by=data["user_name"]
            )
        )
    return new_data

def roleCreator(roles:list) -> None:
    Role.objects.bulk_create(roles)

def roleUpdate(role:Role, data) -> None:
    role.name = data["name"]
    role.save(update_fields=["name"])

def create(data:dict, roles:list) -> dict | None:
    try:
        new_roles = newRoles(roles)
        if not new_roles:
            return {"error": "Role(s) already exists", "status":400}
        role_list = prepareCreate(list(new_roles), data)
        with transaction.atomic():
            roleCreator(role_list)
    except IntegrityError:
        return queue_error
    except Exception:
        return server_error
    return None

def update(role:Role, data:dict) -> dict | None:
    try:
        if role.name == data["name"].title():
            return {"error": "Nothing to update.", "status": 400}
        with transaction.atomic():
            roleUpdate(role, data)
    except IntegrityError:
        return {"error": "Role record already exists.", "status": 400}
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None

def delete_one(role:Role) -> dict | None:
    try:
        with transaction.atomic():
            role.delete()
    except ProtectedError:
            return {
                "error": "Role(s) cannot be deleted because of existing staff attached.", 
                "status": 400
            }
    except Role.DoesNotExist:
        return role_404
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None

def delete_many(role_ids:list) -> dict | None:
    try:
        with transaction.atomic():
            roles = Role.objects.select_for_update(
                nowait=True
            ).filter(id__in=role_ids)
            if not roles.exists():
                raise Role.DoesNotExist
            roles.delete()
    except ProtectedError:
        return {
            "error": "Role(s) cannot be deleted because of existing staff attached.", 
            "status": 400
        }
    except Role.DoesNotExist:
        return role_404
    except DatabaseError:
        return queue_error
    except Exception:
        return server_error
    return None