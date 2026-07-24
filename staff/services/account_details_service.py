from django.utils import timezone
from account.services.profile_service import getFullName
from ..models import AccountDetail, Staff

class AccountDataRetrieval:

    @staticmethod
    def retrieve_all() -> AccountDetail:
        return AccountDetail.objects.all().order_by("-account_name")

    @staticmethod
    def retrieve_one(id) -> AccountDetail | None:
        return AccountDetail.objects.filter(id=id).first()

    
class AccountDataInserter:
    def __init__(self, data:list[dict] | dict, user):    
        self.data = data
        self.user = user
        self.full_name = getFullName(user)
    
    def insert_one(self):
        AccountDetail.objects.create(
            staff=self.data["staff"],
            bank_name=self.data["bank_name"],
            account_name=self.data["account_name"],
            account_number=self.data["account_number"],
            created_by_user=self.user,
            created_by=self.full_name
        )
        
    def insert_many(self) -> None:
        account_list = []
        for account in self.data:
            account_list.append(
                AccountDetail(
                    staff=account["staff"],
                    bank_name=account["bank_name"],
                    account_name=account["account_name"],
                    account_number=account["account_number"],
                    created_by_user=self.user,
                    created_by=self.full_name
            ))
        AccountDetail.objects.bulk_create(account_list)    

class AccountDataUpdater:

    @staticmethod
    def update_one(staff:Staff, data:dict, user) -> None:
        return AccountDetail.objects.filter(
                staff=staff
            ).update(
                bank_name=data["bank_name"],
                account_name=data["account_name"],
                account_number=data["account_number"],
                updated_at=timezone.now().date(),
                updated_by_user=user,
                updated_by=getFullName(user)
            )
