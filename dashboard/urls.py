from django.urls import path
from .views import (
    admin_dashboard_view,
    admin_reservations_view,
    delete_reservation_view,
)

app_name = "dashboard"

urlpatterns = [
    path("", admin_dashboard_view, name="admin_dashboard_url"),
    path("reservations/", admin_reservations_view, name="admin_reservations_url"),
    path(
        "reservations/delete/<int:pk>/",
        delete_reservation_view,
        name="delete_reservation_url",
    ),
]
