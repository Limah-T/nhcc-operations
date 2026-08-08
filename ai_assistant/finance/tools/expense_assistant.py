from finance.expense.models import Expense, Diesel, EKEDC
import datetime

class ExpenseRecord:
    @staticmethod
    def get_expense_record(start_date:datetime.date, end_date:datetime.date):
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        expenses = Expense.objects.select_related("category").filter(
            created_at__gte=start,
            created_at__lte=end
        )
        return [
            {
                "category": exp.category_name,
                "item": exp.name,
                "total": exp.total,
                "purchased_date": exp.created_at
            } for exp in expenses
        ]

class DieselRecord:
    @staticmethod
    def get_diesel_record(start_date:datetime.date, end_date:datetime.date):
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        diesels = Diesel.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        )

        return [
            {
                "litres": diesel.litres,
                "price": diesel.price,
                "transport": diesel.transport,
                "total": diesel.total,
                "supplier_name": diesel.supplier_name,
                "purchased_date": diesel.created_at
                
        } for diesel in diesels
    ]

class EKEDCRecord:
    @staticmethod
    def get_ekedc_record(start_date:datetime.date, end_date:datetime.date):
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
        ekedc = EKEDC.objects.filter(
            created_at__gte=start,
            created_at__lte=end
        )

        return [
            {
                "kwh": meter.kwh,
                "amount": meter.amount,
                "purchased_date": meter.created_at
                
        } for meter in ekedc
    ]

