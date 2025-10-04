from django.urls import path
from .views import register_view, login_view, logout_view, forgot_password_view

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register_url"),
    path("login/", login_view, name="login_url"),
    path("log-out/", logout_view, name="logout_url"),
    path("forgot-password/", forgot_password_view, name="forgot_password_url"),
]
