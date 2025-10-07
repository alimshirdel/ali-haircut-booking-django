from .models import Shop


def has_shop_context(request):
    if request.user.is_authenticated:
        return {"has_shop": Shop.objects.filter(barber=request.user).exists()}
    return {"has_shop": False}
