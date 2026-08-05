from django.db import IntegrityError
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from dashboard.views import director_temp_name
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.error_responses import (
    POSITION_EXISTS, POSITIONS_EXISTS, POSITION_NOT_FOUND,
    POSITIONS_NOT_FOUND, POSITION_CREATED, POSITIONS_CREATED,
    POSITION_UPDATED, POSITION_DELETED, POSITIONS_DELETED,
    SERVER_ERROR, NOTHING_TO_UPDATE, POSITION_PROTECTED_ERROR,
    POSITIONS_PROTECTED_ERROR
)
from ..services.director_service import director_context_data
from ..services.position_service import (
    PostionPayloadParser, PositionDataCreate, 
    PositionDataUpdate, PositionDataDelete
)
from .director_views import director_url_name, error_response
from ..forms import PositionForm
from ..models import Position


@method_decorator(login_required, "dispatch")
class PositionGetCreateView(View):
    def get(self, request):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _single_handler(self, request):
        request_data = PostionPayloadParser(request).parse_single()
        form = PositionForm(data=request_data)
        if form.is_valid():
            try:
                PositionDataCreate(
                    form.cleaned_data, request.user
                ).create_single()
                messages.success(request, POSITION_CREATED)
                return redirect(director_url_name)
            except IntegrityError:
                code = 400
                messages.error(request, POSITION_EXISTS)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            code = 400
            messages.error(request, form.errors)
        return error_response(request, code)

    def _bulk_handler(self, request):
        request_data = PostionPayloadParser(request).parse_bulk()
        data_list = []
        for name in request_data["name"]:
            form = PositionForm(data={"name":name})
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            data_list.append(form.cleaned_data)

        try:
            PositionDataCreate(data_list, request.user).create_bulk()
            messages.success(request, POSITIONS_CREATED)
            return redirect(director_url_name)
        except IntegrityError:
            code = 400
            messages.error(request, POSITIONS_EXISTS)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def post(self, request) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request)
        elif action == "bulk":
            return self._bulk_handler(request)

        return redirect(director_url_name)

@method_decorator(login_required, "dispatch")
class PositionUpdateView(View):
    def get(self, request, id=None):

        return redirect(director_url_name)

    def _single_handler(self, request, id:int):
        request_data = PostionPayloadParser(request).parse_single()
        form = PositionForm(data=request_data)
        if form.is_valid():
            try:
                PositionDataUpdate(
                    form.cleaned_data, request.user
                ).update_single(id)
                messages.success(request, POSITION_UPDATED)
                return redirect(director_url_name)
            except Position.DoesNotExist:
                code = 404
                messages.error(request, POSITION_NOT_FOUND)
            except IntegrityError:
                code = 400
                messages.error(request, POSITION_EXISTS)
            except NothingToUpdateError:
                code = 400
                messages.error(request, NOTHING_TO_UPDATE)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            code = 400
            messages.error(request, form.errors)
        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request, id)
        
        return redirect(director_url_name)

@method_decorator(login_required, "dispatch")
class PositionDeleteView(View):
    def get(self, request, id=None):

        return redirect(director_url_name)

    def _single_handler(self, request, id:int):
        try:
            PositionDataDelete().delete_single(id)
            messages.success(request, POSITION_DELETED)
            return redirect(director_url_name)
        except Position.DoesNotExist:
            code = 404
            messages.error(request, POSITION_NOT_FOUND)
        except ProtectedError:
            code = 400
            messages.error(request, POSITION_PROTECTED_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def _bulk_handler(self, request):
        position_ids = request.POST.getlist("position_ids")
        try:
            if position_ids:
                PositionDataDelete().delete_bulk(position_ids)
                messages.success(request, POSITIONS_DELETED)
            return redirect(director_url_name)
        except Position.DoesNotExist:
            messages.error(request, POSITIONS_NOT_FOUND)
            code = 404
        except ProtectedError:
            code = 400
            messages.error(request, POSITIONS_PROTECTED_ERROR)
        except Exception:
            messages.error(request, SERVER_ERROR)
            code = 500

        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")
        if action == "single":
            return self._single_handler(request, id)
        elif action == "bulk":
            return self._bulk_handler(request)
        
        return redirect(director_url_name)