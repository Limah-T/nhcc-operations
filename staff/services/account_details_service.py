from ..models import AccountDetail
from django.db import transaction, IntegrityError, DatabaseError
from nhcc_operations.services.generic_service import server_error, queue_error, role_404

def bankAcctRetrieval(pk) -> AccountDetail | None:
    return AccountDetail.objects.filter(id=pk).first()

def bankAccountQueryset() -> AccountDetail:
    return AccountDetail.objects.select_related(
        "staff").all().order_by("bank_full_name")

# def bankAccountFormValidator(data:dict) -> AccountDetailForm | list:
#     full_names = data["bank_full_names"]
#     bank_names = data["bank_names"]
#     account_numbers = data["account_numbers"]
#     account_list = []
#     for number, name, bank in zip(account_numbers, full_names, bank_names):
#         form = AccountDetailForm(data={
#             "account_number":number,
#             "bank_full_name":name,
#             "bank_name":bank
#         })
#         if not form.is_valid():
#             return form
#         account_list.append(form.cleaned_data)
#     return account_list

def newAccounts(accounts:list) -> set | None:
    numbers = {data["account_number"] for data in accounts}
    existing_roles = set(AccountDetail.objects.filter(
        account_number__in=numbers
        ).values_list("account_number", flat=True))
    if len(existing_roles) == len(numbers):
        return None
    new_accts = numbers - existing_roles
    return new_accts
    
def accountDetailCreator(accounts:list, data) -> None:
    new_data = []
    for account in accounts:
        new_data.append(
            AccountDetail(
                staff=account["staff"],
                bank_name=account["bank_name"],
                bank_full_name=account["bank_full_name"],
                account_number=account["account_number"],
                created_by_user=data["user"],
                created_by=data["user_name"]
            )
        )
    AccountDetail.objects.bulk_create(new_data)


# def create(data:dict, accounts:list) -> dict | None:
#     try:
#         new_accts = newAccounts(accounts)
#         if not new_accts:
#             return {"error": "Account number(s) already exists", "status":400}
#         role_list = prepareCreate(list(accounts), data)
#         with transaction.atomic():
#             accountDetailCreator(role_list)
#     except IntegrityError:
#         return queue_error
#     except Exception:
#         return server_error
#     return None

# def update(role:Role, data:dict) -> dict | None:
#     try:
#         if role.name == data["name"].title():
#             return {"error": "Nothing to update.", "status": 400}
#         with transaction.atomic():
#             roleUpdate(role, data)
#     except IntegrityError:
#         return {"error": "Role record already exists.", "status": 400}
#     except DatabaseError:
#         return queue_error
#     except Exception as e:
#         print(str(e))
#         return server_error
#     return None

# def delete_one(role:Role) -> dict | None:
#     try:
#         with transaction.atomic():
#             role.delete()
#     except Role.DoesNotExist:
#         return role_404
#     except DatabaseError:
#         return queue_error
#     except Exception as e:
#         print(str(e))
#         return server_error
#     return None

# def delete_many(role_ids:list) -> dict | None:
#     try:
#         with transaction.atomic():
#             print("IN DELETE", role_ids)
#             roles = Role.objects.select_for_update(
#                 nowait=True
#             ).filter(id__in=role_ids)
#             if not roles.exists():
#                 raise Role.DoesNotExist
#             roles.delete()
#     except Role.DoesNotExist:
#         return role_404
#     except DatabaseError:
#         return queue_error
#     except Exception:
#         return server_error
#     return None