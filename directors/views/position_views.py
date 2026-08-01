from django.db import IntegrityError
from core.utils.custom_exceptions import NothingToUpdateError
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from dashboard.views import director_temp_name
from core.utils.error_responses import SERVER_ERROR, NOTHING_TO_UPDATE
from ..forms import PositionForm
from ..services.director_service import director_context_data
from ..utils.error_responses import (
    POSITION_EXISTS, POSITIONS_EXISTS, POSITION_NOT_FOUND,
    POSITIONS_NOT_FOUND, POSITION_CREATED, POSITIONS_CREATED,
    POSITION_UPDATED, POSITION_DELETED, POSITIONS_DELETED
)
from ..services.position_service import (
    PostionPayloadParser, PositionDataCreate, 
    PositionDataUpdate, PositionDataDelete
)
from ..models import Position

director_url = "director_records"

@method_decorator(login_required, "dispatch")
class PositionGetCreateView(View):
    def get(self, request):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _get_context(self, form:PositionForm) -> dict:
        context = director_context_data()
        context.update({"form": form})
        return context

    def _handle_single_data(self, request):
        request_data = PostionPayloadParser(request).parse_single()
        form = PositionForm(data=request_data)
        if form.is_valid():
            try:
                PositionDataCreate(
                    form.cleaned_data, request.user
                ).create_single()
                messages.success(request, POSITION_CREATED)
                return redirect(director_url)
            except IntegrityError:
                code = 400
                messages.error(request, POSITION_EXISTS)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: code = 400
        return render(
            request=request, 
            template_name=director_temp_name, 
            context=self._get_context(form), status=code
        )

    def _handle_bulk_data(self, request):
        request_data = PostionPayloadParser(request).parse_bulk()
        data_list = []
        for name in request_data["name"]:
            form = PositionForm(data={"name":name})
            if not form.is_valid():
                messages.error(request, form.errors)
                return render(
                    request, director_temp_name, 
                    self._get_context(form), status=400
                    )
            data_list.append(form.cleaned_data)

        try:
            PositionDataCreate(data_list, request.user).create_bulk()
            messages.success(request, POSITIONS_CREATED)
            return redirect(director_url)
        except IntegrityError:
            code = 400
            messages.error(request, POSITIONS_EXISTS)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)
        return render(
            request=request, 
            template_name=director_temp_name, 
            context=self._get_context(form),
            status=code
        )

    def post(self, request):
        action = request.POST.get("action")
        if action == "single":
            response = self._handle_single_data(request)
        else:
            response = self._handle_bulk_data(request)
        return response
                

@method_decorator(login_required, "dispatch")
class PositionUpdateView(View):
    def get(self, request, pk=None):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _get_context(self, form:PositionForm) -> dict:
        context = director_context_data()
        context.update({"form": form})
        return context

    def _handle_single_data(self, request, pk):
        request_data = PostionPayloadParser(request).parse_single()
        form = PositionForm(data=request_data)
        if form.is_valid():
            try:
                PositionDataUpdate(
                    form.cleaned_data, request.user
                ).update_single(pk)
                messages.success(request, POSITION_UPDATED)
                return redirect(director_url)
            except Position.DoesNotExist:
                messages.error(request, POSITION_NOT_FOUND)
                code = 404
            except IntegrityError:
                messages.error(request, POSITION_EXISTS)
                code = 400
            except NothingToUpdateError:
                messages.error(request, NOTHING_TO_UPDATE)
                code = 400
            except Exception:
                messages.error(request, SERVER_ERROR)
                code = 500

        else: code = 400
        return render(
            request=request, 
            template_name=director_temp_name, 
            context=self._get_context(form),
            status=code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")

        if action == "single":
            response = self._handle_single_data(request, pk)
            return response
        return redirect(director_url)

@method_decorator(login_required, "dispatch")
class PositionDeleteView(View):
    def get(self, request, pk=None):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _get_context(self, form:PositionForm=None) -> dict:
        context = director_context_data()
        context.update({"form": form})
        return context

    def _handle_single_data(self, request, pk):
        try:
            PositionDataDelete().delete_single(pk)
            messages.success(request, POSITION_DELETED)
            return redirect(director_url)
        except Position.DoesNotExist:
            messages.error(request, POSITION_NOT_FOUND)
            code = 404
        except Exception:
            messages.error(request, SERVER_ERROR)
            code = 500

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=self._get_context(),
            status=code
        )

    def _handle_bulk_data(self, request):
        position_ids = request.POST.getlist("position_ids")
        try:
            PositionDataDelete().delete_bulk(position_ids)
            messages.success(request, POSITIONS_DELETED)
            return redirect(director_url)
        except Position.DoesNotExist:
            messages.error(request, POSITIONS_NOT_FOUND)
            code = 404
        except Exception:
            messages.error(request, SERVER_ERROR)
            code = 500

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=self._get_context(),
            status=code
        )

    def post(self, request, pk=None):
        action = request.POST.get("action")
        if action == "single":
            response = self._handle_single_data(request, pk)
        else:
            response = self._handle_bulk_data(request)
        return response