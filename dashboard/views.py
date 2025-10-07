import jdatetime, json
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q
from shops.models import Shop, Reservation
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import TruncDate


User = get_user_model()


# فقط کاربرایی که staff یا superuser هستن
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard_view(request):
    # آمار کلی
    total_users = User.objects.count()
    total_shops = Shop.objects.count()
    total_reservations = Reservation.objects.count()

    # فیلتر زمانی (پیش‌فرض ۷ روز گذشته)
    days = int(request.GET.get("days", 7))
    today = timezone.now().date()
    start_date = today - timedelta(days=days)
    end_date = today + timedelta(days=1)

    # داده‌های رزرو برای نمودار
    data = (
        Reservation.objects.filter(created_at__date__range=[start_date, today])
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    labels = [
        jdatetime.date.fromgregorian(date=item["day"]).strftime("%Y/%m/%d")
        for item in data
    ]
    values = [item["count"] for item in data]
    if not data:
        labels = [
            jdatetime.date.fromgregorian(date=start_date + timedelta(days=i)).strftime(
                "%Y/%m/%d"
            )
            for i in range(days + 1)
        ]
        values = [0 for _ in range(days + 1)]

    context = {
        "total_users": total_users,
        "total_shops": total_shops,
        "total_reservations": total_reservations,
        "labels": mark_safe(json.dumps(labels)),  # 🔥 تبدیل به JSON معتبر
        "values": mark_safe(json.dumps(values)),  # 🔥 تبدیل به JSON معتبر
        "days": days,
    }

    return render(request, "dashboard/admin_dashboard.html", context)


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_reservations_view(request):
    query = request.GET.get("q", "")
    query_date = request.GET.get("date", "")  # ورودی شمسی: 1404/07/15

    reservations = Reservation.objects.select_related(
        "user", "schedule", "schedule__shop"
    ).order_by("-schedule__date", "-time_slot")

    try:
        gregorian_date = None
        if query_date:
            jd = jdatetime.datetime.strptime(query_date, "%Y/%m/%d")
            gregorian_date = jd.togregorian().date()
    except ValueError:
        gregorian_date = None  # اگر تاریخ درست نبود، نادیده گرفته می‌شود

    # اعمال فیلترها
    if query and gregorian_date:
        # اگر هم متن جستجو و هم تاریخ هست
        reservations = reservations.filter(
            (
                Q(user__username__icontains=query)
                | Q(schedule__shop__name__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
            )
            & Q(schedule__date=gregorian_date)
        )
    elif query:
        # فقط جستجوی متن
        reservations = reservations.filter(
            Q(user__username__icontains=query)
            | Q(schedule__shop__name__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )
    elif gregorian_date:
        # فقط جستجوی تاریخ
        reservations = reservations.filter(schedule__date=gregorian_date)

    # صفحه‌بندی: هر صفحه 20 رزرو
    paginator = Paginator(reservations, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/admin_reservations.html",
        {
            "reservations": page_obj,
            "query": query,
        },
    )


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def delete_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.delete()
    messages.success(request, "رزرو با موفقیت حذف شد ✅")
    return redirect("dashboard:admin_reservations_url")
