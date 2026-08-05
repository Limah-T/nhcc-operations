from django.shortcuts import render, redirect
from django.views import View
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import IntegrityError
from dashboard.views import category_temp_name
from core.utils.custom_exceptions import NothingToUpdateError
from core.utils.error_responses import (
    CATEGORY_404, CATEGORIES_404, SERVER_ERROR, 
    CATEGORY_CONFLICT, CATEGORIES_CONFLICT, NOTHING_TO_UPDATE)
from core.utils.success_responses import (
    CATEGORY_CREATED, CATEGORIES_CREATED, CATEGORY_UPDATED, 
    CATEGORY_DELETED, CATEGORIES_DELETED)
from ..services.category_service import (
    CategoryPayloadParser, category_context_data,
    CategoryDataInserter, CategoryDataUpdater, CategoryDataDeleter
)
from ..forms import CategoryForm
from ..models import Category

category_url_name = "category" 

def error_response(request, code:int):
    return render(
        request=request, template_name=category_temp_name,
        context=category_context_data(), status=code
    )

@method_decorator(login_required, name="dispatch")
class CategoryGetCreateView(View):
    def get(self, request):
        return render(
            request=request, template_name=category_temp_name,
            context=category_context_data(),
            status=200
        )

    def _single_handler(self, request):
        field_data = CategoryPayloadParser(request).parse_single()
        form = CategoryForm(data=field_data)
        if form.is_valid():
            try:
                category = CategoryDataInserter(form.cleaned_data, request.user)
                category.create_single()
                messages.success(request, CATEGORY_CREATED)
                return redirect(category_url_name)
            except IntegrityError:
                code = 400
                messages.error(request, CATEGORY_CONFLICT)
            except Exception:
                code = 500
                messages.error(request, SERVER_ERROR)   
        else: 
            code = 400
            messages.error(request, form.errors)
        return error_response(request, code)
    
    def _bulk_handler(self, request):
        field_data = CategoryPayloadParser(request).parse_bulk()
        category_list = []
        for name in field_data["name"]:
            form = CategoryForm(data={"name":name})
            if not form.is_valid():
                messages.error(request, form.errors)
                return error_response(request, code=400)
            category_list.append(form.cleaned_data)

        try:
            category = CategoryDataInserter(category_list, request.user)
            category.create_bulk()
            messages.success(request, CATEGORIES_CREATED)
            return redirect(category_url_name)
        except IntegrityError:
            code = 400
            messages.error(request, CATEGORIES_CONFLICT)
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
        
        return redirect(category_url_name)

@method_decorator(login_required, "dispatch")
class CategoryUpdateView(View):
    def get(self, request, id=None):
        return redirect(category_url_name)

    def _single_handler(self, request, id):
        field_data = CategoryPayloadParser(request).parse_single()
        form = CategoryForm(data=field_data)
        if form.is_valid():
            try:
                category = CategoryDataUpdater(form.cleaned_data, request.user)
                category.update_single(id)
                messages.success(request, CATEGORY_UPDATED)
                return redirect(category_url_name)
            except NothingToUpdateError:
                code = 400
                messages.error(request, NOTHING_TO_UPDATE)
            except IntegrityError:
                code = 400
                messages.error(request, CATEGORY_CONFLICT)
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

        return redirect(category_url_name)

@method_decorator(login_required, "dispatch")
class CategoryDeleteView(View):
    def get(self, request):
       return redirect(category_url_name)

    def _single_handler(self, request, id:int):
        try:
            CategoryDataDeleter().delete_single(id)
            messages.success(request, CATEGORY_DELETED)
            return redirect(category_url_name)
        except Category.DoesNotExist:
            code = 404
            messages.error(request, CATEGORY_404)
        except IntegrityError:
            code = 400
            messages.error(request, CATEGORY_CONFLICT)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)
    
    def _bulk_handler(self, request, category_ids:list):
        try:
            if category_ids:
                CategoryDataDeleter().delete_bulk(category_ids)
                messages.success(request, CATEGORIES_DELETED)
            return redirect(category_url_name)
        except Category.DoesNotExist:
            code = 404
            messages.error(request, CATEGORIES_404)
        except IntegrityError:
            code = 400
            messages.error(request, CATEGORIES_CONFLICT)
        except Exception:
            code = 500
            messages.error(request, SERVER_ERROR)

        return error_response(request, code)

    def post(self, request, id=None) -> HttpResponse:
        action = request.POST.get("action")

        if action == "single":
            return self._single_handler(request, id)
        elif action == "bulk":
            category_ids = request.POST.getlist("category_ids")
            return self._bulk_handler(request, category_ids)
        
        return redirect(category_url_name)
