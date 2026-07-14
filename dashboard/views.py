from django.shortcuts import render


dashboard_temp_name = "dashboard/dashboard.html"
def dashboard(request):
    return render(request, dashboard_temp_name)


