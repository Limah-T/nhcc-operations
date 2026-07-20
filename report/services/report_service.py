from django.utils import timezone
from datetime import datetime
from weasyprint import HTML
import calendar

format = "%Y-%m-%d"

def setDate() -> tuple:
    now = timezone.now()
    month, year = now.month, now.year
    start = datetime(year, month, 1)
    end = datetime(year, month, getMonthDays())
    start_date = timezone.make_aware(value=start)
    end_date = timezone.make_aware(value=end)
    return (start_date, end_date)


def futureDate(start_date, end_date) -> bool:
    now = timezone.now()
    if (
            start_date.month > now.month or start_date.year > now.year
            ) or( end_date.month > now.month or end_date.year > now.year):
            
        return True
    return False

def getMonthDays() -> int:
    now = timezone.now()
    _, num_of_days = calendar.monthrange(now.year, now.month)
    return num_of_days

def pdfGenerator(html_string, request):
    return HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf()