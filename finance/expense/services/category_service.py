from ..models import Category

def categoryQueryset() -> Category:
    return Category.objects.all()