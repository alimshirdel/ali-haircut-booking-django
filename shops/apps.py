from django.apps import AppConfig


class ShopsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shops"

    def ready(self):
        # فقط اجرا شدن فایل کافی است، نیازی نیست چیزی صدا زده شود
        import shops.signals
