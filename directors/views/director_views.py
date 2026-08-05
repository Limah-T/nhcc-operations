from django.db import IntegrityError, DatabaseError
from core.utils.custom_exceptions import NothingToUpdateError
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from dashboard.views import director_temp_name
from core.utils.error_responses import (
    UNIQUE_DATA_ERROR, UNIQUE_DATA_ERRORS, DIRECTOR_NOT_FOUND,
    DIRECTORS_NOT_FOUND, DIRECTOR_CREATED, DIRECTORS_CREATED,
    DIRECTOR_UPDATED, DIRECTOR_DELETED, DIRECTORS_DELETED,
    SERVER_ERROR, NOTHING_TO_UPDATE, QUEUE_ERROR
)
from ..forms import DirectorForm
from ..services.director_service import (
    DirectorPayloadParser, DirectorDataCreate,
    DirectorDataUpdate, DirectorDataDelete,
    director_context_data
)
from ..models import Director

director_url_name = "directors"

def error_response(request, code):
    return render(
        request=request, 
        template_name=director_temp_name, 
        context=director_context_data(),
        status=code
    )

@method_decorator(login_required, "dispatch")
class DirectorGetCreateView(View):
    def get(self, request):
        
        return render(
            request=request, 
            template_name=director_temp_name, 
            context=director_context_data(),
            status=200
        )

    def _single_handler(self, request):
        request_data = DirectorPayloadParser(request).parse_single()
        form = DirectorForm(data=request_data)
        if form.is_valid():
            try:
                DirectorDataCreate(
                    form.cleaned_data, request.user
                ).create_single()
                messages.success(request, DIRECTOR_CREATED)
                return redirect(director_url_name)
            except IntegrityError:
                code = 400
                messages.error(request, UNIQUE_DATA_ERROR)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)
        else: 
            messages.error(request, form.errors)
            code = 400
        return error_response(request, status=code)

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

    def _bulk_handler(self, request):
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
                return error_response(request, code=400)
            data_list.append(form.cleaned_data)

        try:
            DirectorDataCreate(data_list, request.user).create_bulk()
            messages.success(request, DIRECTORS_CREATED)
            return redirect(director_url_name)
        except IntegrityError:
            code = 400
            messages.error(request, UNIQUE_DATA_ERRORS)
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
class DirectorUpdateView(View):
    def get(self, request, id=None):

        return redirect(director_url_name)
    
    def _single_handler(self, request, id:int):
        request_data = DirectorPayloadParser(request).parse_single()
        form = DirectorForm(data=request_data)
        if form.is_valid():
            try:
                DirectorDataUpdate(
                    form.cleaned_data, request.user
                ).update_single(id)
                messages.success(request, DIRECTOR_UPDATED)
                return redirect(director_url_name)
            except Director.DoesNotExist:
                code = 404
                messages.error(request, DIRECTOR_NOT_FOUND)
            except IntegrityError:
                code = 400
                messages.error(request, UNIQUE_DATA_ERROR)
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

    def post(self, request, id=None):
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request, id)
        
        return redirect(director_url_name)

@method_decorator(login_required, "dispatch")
class DirectorDeleteView(View):
    def get(self, request, id=None):

        return redirect(director_url_name)

    def _single_handler(self, request, id:int):
        try:
            DirectorDataDelete().delete_single(id)
            messages.success(request, DIRECTOR_DELETED)
            return redirect(director_url_name)
        except Director.DoesNotExist:
            code = 404
            messages.error(request, DIRECTOR_NOT_FOUND)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def _bulk_handler(self, request):
        director_ids = request.POST.getlist("director_ids")
        try:
            if director_ids:
                DirectorDataDelete().delete_bulk(director_ids)
                messages.success(request, DIRECTORS_DELETED)
            return redirect(director_url_name)
        except Director.DoesNotExist:
            code = 404
            messages.error(request, DIRECTORS_NOT_FOUND)
        except DatabaseError:
            code = 400
            messages.error(request, QUEUE_ERROR)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")
        
        if action == "single":
            return self._single_handler(request, id)
        elif action == "bulk":
            return self._bulk_handler(request)
        
        return redirect(director_url_name)
