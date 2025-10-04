from django import template
from persiantools.jdatetime import JalaliDate
from persiantools import digits

register = template.Library()

WEEKDAYS_FA = {
    "Shanbeh": "شنبه",
    "Yekshanbeh": "یکشنبه",
    "Doshanbeh": "دوشنبه",
    "Seshanbeh": "سه‌شنبه",
    "Chaharshanbeh": "چهارشنبه",
    "Panjshanbeh": "پنجشنبه",
    "Jomeh": "جمعه",
}

MONTHS_FA = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}


@register.filter
def jalali(value):
    if not value:
        return ""
    jd = JalaliDate(value)
    weekday_fa = WEEKDAYS_FA[jd.strftime("%A")]
    day = digits.en_to_fa(str(jd.day))
    month_fa = MONTHS_FA[jd.month]
    year = digits.en_to_fa(str(jd.year))
    return f"{weekday_fa} {day} {month_fa} {year}"
