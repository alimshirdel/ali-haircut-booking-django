from django import forms
from .models import Schedule, ShopComment, ShopRating


class CreateForm(forms.Form):
    name = forms.CharField(
        label="آدرس", widget=forms.TextInput(attrs={"placeholder": "نام ارایشگاه"})
    )
    image = forms.ImageField()
    descriptions = forms.CharField(
        label="آدرس", widget=forms.Textarea(attrs={"placeholder": "توضیحات ارایشگاه"})
    )
    address = forms.CharField(
        label="آدرس", widget=forms.TextInput(attrs={"placeholder": "ادرس ارایشگاه"})
    )
    create_date = forms.DateField(widget=forms.DateInput)
    is_show = forms.BooleanField()
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)


class EditForm(forms.Form):
    name = forms.CharField(
        label="آدرس", widget=forms.TextInput(attrs={"placeholder": "نام ارایشگاه"})
    )
    image = forms.ImageField(required=False)
    descriptions = forms.CharField(
        label="آدرس", widget=forms.Textarea(attrs={"placeholder": "توضیحات ارایشگاه"})
    )
    address = forms.CharField(
        label="آدرس", widget=forms.TextInput(attrs={"placeholder": "ادرس ارایشگاه"})
    )
    create_date = forms.DateField(widget=forms.DateInput)
    is_show = forms.BooleanField()
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["date", "start_time", "end_time"]
        labels = {
            "date": "تاریخ روز کاری",
            "start_time": "ساعت شروع کار",
            "end_time": "ساعت پایان کار",
        }
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "placeholder": "تاریخ را انتخاب کنید",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                    "placeholder": "ساعت شروع",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                    "placeholder": "ساعت پایان",
                }
            ),
        }


class ShopCommentForm(forms.ModelForm):
    class Meta:
        model = ShopComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "دیدگاه خود را بنویسید..."}
            )
        }


class ShopRatingForm(forms.ModelForm):
    class Meta:
        model = ShopRating
        fields = ["value"]
