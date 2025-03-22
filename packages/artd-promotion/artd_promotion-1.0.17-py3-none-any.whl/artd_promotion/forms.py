from django.core.exceptions import ValidationError
from artd_promotion.models import Coupon, PromotionRule
from django import forms
from django.utils.translation import gettext_lazy as _
from dal import autocomplete
from django.contrib import admin


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = "__all__"

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date:
            return start_date
        else:
            raise ValidationError(_("Start date cannot be empty"))

    def clean_end_date(self):
        end_date = self.cleaned_data.get("end_date")
        if end_date:
            start_date = self.cleaned_data.get("start_date")
            if start_date and end_date < start_date:
                raise ValidationError(
                    _("The end date must be later than the start date")
                )
            return end_date
        else:
            raise ValidationError(_("End date cannot be empty"))

    # create a validation: is_percentage the value must be between 0 and 100 if is_percentage is True
    # if is_percentage is False, the value must be greater than or equal to 0
    def clean_value(self):
        is_percentage = self.cleaned_data.get("is_percentage")
        value = self.cleaned_data.get("value")
        if is_percentage and (value < 0 or value > 100):
            raise ValidationError(
                _(
                    "If you selected the discount type as a percentage, the value must be between 0 and 100"
                )
            )
        elif not is_percentage and value < 0:
            raise ValidationError(_("Coupon value field must be greater than 0"))
        return value


class PromotionRuleForm(forms.ModelForm):
    class Meta:
        model = PromotionRule
        fields = "__all__"
        widgets = {
            "products": autocomplete.ModelSelect2Multiple(
                url="product-autocomplete",
            )
        }
