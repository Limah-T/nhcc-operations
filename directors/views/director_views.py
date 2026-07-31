from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from dashboard.views import director_temp_name

from core.utils.error_responses import SERVER_ERROR, NOTHING_TO_UPDATE, QUEUE_ERROR
from ..utils.error_responses import POSITION_EXISTS
from ..services.director_service import director_context_data

@login_required
def directorRecordView(request):
    return render(
        request, 
        template_name=director_temp_name,
        context=director_context_data(),
        status=200

    )

