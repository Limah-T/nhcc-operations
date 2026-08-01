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
from ..forms import DirectorForm
from ..services.director_service import (
    DirectorPayloadParser, DirectorDataCreate,
    DirectorDataUpdate, DirectorDataDelete,
    director_context_data
)
from ..utils.error_responses import (
    UNIQUE_DATA_ERROR, UNIQUE_DATA_ERRORS, DIRECTOR_NOT_FOUND,
    DIRECTORS_NOT_FOUND, DIRECTOR_CREATED, DIRECTORS_CREATED,
    DIRECTOR_UPDATED, DIRECTOR_DELETED, DIRECTORS_DELETED
)
from ..models import Director

@login_required
def directorRecordView(request):
    return render(
        request, 
        template_name=director_temp_name,
        context=director_context_data(),
        status=200

    )

director_url = "director_records"

@method_decorator(login_required, "dispatch")
class DirectorGetCreateView(View):
    def get(self, request):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _get_context(self, form:DirectorForm) -> dict:
        context = director_context_data()
        context.update({"form": form})
        return context

    def _handle_single_data(self, request):
        request_data = DirectorPayloadParser(request).parse_single()
        form = DirectorForm(data=request_data)
        if form.is_valid():
            try:
                DirectorDataCreate(
                    form.cleaned_data, request.user
                ).create_single()
                messages.success(request, DIRECTOR_CREATED)
                return redirect(director_url)
            except IntegrityError as error:
                code = 400
                messages.error(request, UNIQUE_DATA_ERROR)
            except Exception as error:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            messages.error(request, form.errors)
            code = 400
        return render(
            request=request, 
            template_name=director_temp_name, 
            context=self._get_context(form), status=code
        )

    def _request_data(
            self, fname, lname, email, number, title, 
            position, nationality, date_joined
        ) -> DirectorForm:
        return DirectorForm(data={
                "first_name":fname, "last_name":lname,
                "email":email, "phone_number":number,
                "title":title, "position":position,
                "nationality":nationality, "date_joined":date_joined
            })

    def _handle_bulk_data(self, request):
        data = DirectorPayloadParser(request).parse_bulk()
        data_list = []
        for fname, lname, email, number, title, \
            position, nationality, date_joined in zip(
                data["first_name"], data["last_name"],
                data["email"], data["phone_number"],
                data["title"], data["position"],
                data["nationality"], data["date_joined"]
            ):
            form = self._request_data(
                fname, lname, email, number, title, 
                position, nationality, date_joined)
            if not form.is_valid():
                messages.error(request, form.errors)
                return render(
                    request, director_temp_name, 
                    self._get_context(form), status=400
                    )
            data_list.append(form.cleaned_data)

        try:
            DirectorDataCreate(data_list, request.user).create_bulk()
            messages.success(request, DIRECTORS_CREATED)
            return redirect(director_url)
        except IntegrityError:
            code = 400
            messages.error(request, UNIQUE_DATA_ERRORS)
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
class DirectorUpdateView(View):
    def get(self, request, pk=None):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _get_context(self, form:DirectorForm) -> dict:
        context = director_context_data()
        context.update({"form": form})
        return context

    def _handle_single_data(self, request, pk):
        request_data = DirectorPayloadParser(request).parse_single()
        form = DirectorForm(data=request_data)
        if form.is_valid():
            try:
                DirectorDataUpdate(
                    form.cleaned_data, request.user
                ).update_single(pk)
                messages.success(request, DIRECTOR_UPDATED)
                return redirect(director_url)
            except Director.DoesNotExist:
                messages.error(request, DIRECTOR_NOT_FOUND)
                code = 404
            except IntegrityError:
                messages.error(request, UNIQUE_DATA_ERROR)
                code = 400
            except NothingToUpdateError:
                messages.error(request, NOTHING_TO_UPDATE)
                code = 400
            except Exception as error:
                messages.error(request, SERVER_ERROR)
                code = 500

        else: 
            messages.error(request, form.errors)
            code = 400
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
class DirectorDeleteView(View):
    def get(self, request, pk=None):

        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _get_context(self, form:DirectorForm=None) -> dict:
        context = director_context_data()
        context.update({"form": form})
        return context

    def _handle_single_data(self, request, pk):
        try:
            DirectorDataDelete().delete_single(pk)
            messages.success(request, DIRECTOR_DELETED)
            return redirect(director_url)
        except Director.DoesNotExist:
            messages.error(request, DIRECTOR_NOT_FOUND)
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
        director_ids = request.POST.getlist("director_ids")
        try:
            DirectorDataDelete().delete_bulk(director_ids)
            messages.success(request, DIRECTORS_DELETED)
            return redirect(director_url)
        except Director.DoesNotExist:
            messages.error(request, DIRECTORS_NOT_FOUND)
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
