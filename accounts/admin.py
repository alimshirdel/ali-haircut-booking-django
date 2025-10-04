# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # ستون‌هایی که توی لیست نمایش داده می‌شوند
    list_display = ("username", "first_name", "last_name", "phone_number", "is_staff")
    # اینجا فیلدهای اضافی رو اضافه می‌کنیم
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "اطلاعات شخصی",
            {"fields": ("first_name", "last_name", "email", "phone_number")},
        ),  # ← شماره تلفن اینجا
        (
            "مجوزها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}),
    )
    # اگر لازم داری توی فرم اضافه هم نمایش داده بشه:
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
