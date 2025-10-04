from django.contrib import admin
from .models import Shop, Schedule, Reservation


admin.site.register(Shop)
admin.site.register(Reservation)
admin.site.register(Schedule)
