from django.urls import path
from .views import (
    shops_view,
    create_view,
    detail_view,
    delete_view,
    edit_view,
    reservation_create_view,
    reservation_list_view,
    reservation_delete,
    barber_reservations_view,
    delete_reservation_view,
    my_reservations_view,
)

app_name = "shops"
urlpatterns = [
    path("", shops_view, name="shops_url"),
    path("create/", create_view, name="create_url"),
    path("detail/<int:pk>/", detail_view, name="detail_url"),
    path("delete/<int:pk>/", delete_view, name="delete_url"),
    path("edit/<int:pk>/", edit_view, name="edit_url"),
    path(
        "reservation-create/<int:pk>/",
        reservation_create_view,
        name="reservation_create_url",
    ),
    path(
        "reservation-list/<int:pk>/", reservation_list_view, name="reservation_list_url"
    ),
    path(
        "reservation/<int:pk>/delete/",
        reservation_delete,
        name="reservation_delete_url",
    ),
    path("my/reservations/", barber_reservations_view, name="barber_reservations_url"),
    path("my/bookings/", my_reservations_view, name="my_reservations_url"),
    path(
        "my/bookings/delete/<int:reservation_id>/",
        delete_reservation_view,
        name="delete_reservation_url",
    ),
]
