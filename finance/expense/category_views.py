from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import CategoryForm, Categoryformset
from .models import Category
from dashboard.views import category_temp_name


@method_decorator(login_required, name="dispatch")
class CategoryView(View):
    def get(self, request):
        queryset = Category.objects.all()
        return render(
            request, category_temp_name, {"categories":queryset, "count":queryset.count()}
        )

    def post(self, request):
        user_name = f"{request.user.first_name} {request.user.last_name}" 

        categories = request.POST.getlist("categories")
        category_list, errors = set(), []
        formset = Categoryformset()
        for category_name in categories:
            if not category_name.strip():
                continue

            form = CategoryForm(
                data={"name": category_name}
            )

            if form.is_valid():
                category_list.add(form.cleaned_data["name"])
            else:
                errors.append({
                    "value": category_name.title(),
                    "errors": form.errors,
                })
        if not errors:
            categories = list(Category.objects.filter(name__in=category_list).values_list("name", flat=True))
            if len(categories) != len(category_list):
                new_categories = [
                    Category(
                        name=name, 
                        created_by_user=request.user,
                        created_by=user_name
                    ) for name in category_list 
                        if name not in categories
                ] 
                Category.objects.bulk_create(new_categories)
                return redirect("category")
            errors.append({
                    "value": categories,
                    "errors": {'name': ['Data already exists.']}
                })
        queryset = Category.objects.all()
        return render(
            request, category_temp_name, {
                "categories":queryset, "form":formset,
                "category_errors": errors
            }
        )
        

@login_required
def edit_category(request, pk):
    if request.method != "POST":
        return redirect("category")
    
    category = Category.objects.filter(id=pk).first()
    form = CategoryForm(data=request.POST)
    if category is None:
        form.add_error("name", "Category not found")
    else:
        if form.is_valid():
            name = form.cleaned_data["name"]
            if category.name != name:
                category.name = name
                category.updated_by_user = request.user
                category.save()
                category.refresh_from_db()
                return redirect("category")    
            form.add_error("name", "Nothing to update.")
    queryset = Category.objects.all()
    return render(
        request, category_temp_name, {
            "categories":queryset, "form":form
        }
    )
    
@login_required
def delete_category(request, pk):
    if request.method != "POST":
        return redirect("category")
    print(pk, "PK")
    category = Category.objects.filter(id=pk).first()
    if category:
        category.delete()
        return redirect("category")
    errors = [{
        "value": "",
        "errors": {'name': ['Category not found']}
    }]
    queryset = Category.objects.all()
    return render(
        request, category_temp_name, {
            "categories":queryset, "form":CategoryForm(),
            "category_errors":errors
        }, status=400
    )

@login_required
def delete_categories(request):
    if request.method != "POST":
        return redirect("category")
    category_ids = request.POST.getlist("category_ids")
    if len(category_ids) > 0:
        categories = Category.objects.filter(id__in=category_ids)
        categories.delete()
    return redirect("category")



    
