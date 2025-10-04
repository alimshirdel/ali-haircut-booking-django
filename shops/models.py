from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Shop(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    descriptions = models.TextField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=300)
    create_date = models.DateField()
    is_show = models.BooleanField(default=True)
    barber = models.ForeignKey(User, on_delete=models.CASCADE)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مغازه"
        verbose_name_plural = "مغازه‌ها"


class Schedule(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="schedules")
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()

    def __str__(self):
        return f"{self.shop.name} - {self.date} ({self.start_time}-{self.end_time})"

    class Meta:
        verbose_name = "ساعت کار"
        verbose_name_plural = "ساعات کار"


class Reservation(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="reservations"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_slot = models.TimeField()  # زمان دقیق رزرو نیم ساعتی

    def __str__(self):
        return f"{self.user.username} - {self.time_slot} - {self.schedule.date}"

    class Meta:
        verbose_name = "رزرو"
        verbose_name_plural = "رزرو ها"
