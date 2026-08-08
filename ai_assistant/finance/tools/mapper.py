def expense_tools():
    from .expense_assistant import ExpenseRecord, DieselRecord, EKEDCRecord
    expense = ExpenseRecord()
    diesel = DieselRecord()
    ekedc = EKEDCRecord()
    return {
        "get_expense_record": expense.get_expense_record,
        "get_diesel_record": diesel.get_diesel_record,
        "get_ekedc_record": ekedc.get_ekedc_record
    }