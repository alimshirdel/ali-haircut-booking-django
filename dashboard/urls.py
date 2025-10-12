from django.urls import path
from .views import (
    admin_dashboard_view,
    admin_reservations_view,
    delete_reservation_view,
    admin_comments_view,
    delete_comment_view,
)

app_name = "dashboard"

urlpatterns = [
    path("", admin_dashboard_view, name="admin_dashboard_url"),
    path("reservations/", admin_reservations_view, name="admin_reservations_url"),
    path("comments/", admin_comments_view, name="admin_comments_url"),
    path(
        "reservations/delete/<int:pk>/",
        delete_reservation_view,
        name="delete_reservation_url",
    ),
    path(
        "comments/delete/<int:pk>/",
        delete_comment_view,
        name="delete_comment_url",
    ),
]
