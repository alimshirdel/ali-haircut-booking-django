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
        Schedule,
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_slot = models.TimeField()  # زمان دقیق رزرو نیم ساعتی
    created_at = models.DateTimeField(auto_now_add=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    shop_name = models.CharField(max_length=255, blank=True)
    date = models.DateField(null=True, blank=True)

    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        # اگر رزرو به Schedule متصل است و shop هنوز تنظیم نشده
        if self.schedule:
            self.shop = self.schedule.shop
            self.shop_name = self.schedule.shop.name
            self.date = self.schedule.date

            # پر کردن اطلاعات کاربر
        if self.user:
            self.username = self.user.username
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
            # فرض می‌کنیم مدل User یه فیلد phone_number داره
            self.phone_number = getattr(self.user, "phone_number", "")
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        # اگر first_name یا last_name خالی باشن، به طور امن کنار هم میذاره
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def __str__(self):
        return f"{self.user.username} - {self.time_slot} - {self.schedule.date}"

    class Meta:
        verbose_name = "رزرو"
        verbose_name_plural = "رزرو ها"
