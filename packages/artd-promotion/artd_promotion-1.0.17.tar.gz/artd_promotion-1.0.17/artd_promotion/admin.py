from django.contrib import admin
from artd_promotion.models import Coupon, PromotionRule
from django.utils.translation import gettext_lazy as _
from artd_promotion.forms import CouponForm, PromotionRuleForm
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from dal import autocomplete


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    form = CouponForm
    list_display = [
        "name",
        "id",
        "partner",
        "code",
        "is_percentage",
        "value",
        "status",
    ]
    list_filter = [
        "is_percentage",
        "status",
    ]
    search_fields = [
        "code",
        "name",
        "id",
        "partner__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Coupon information"),
            {
                "fields": (
                    "partner",
                    "code",
                    "name",
                    "is_percentage",
                    "value",
                    "uses_per_coupon",
                    "uses",
                )
            },
        ),
        (
            _("Date Information"),
            {
                "fields": (
                    "start_date",
                    "end_date",
                ),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    #


@admin.register(PromotionRule)
class PromotionRuleAdmin(admin.ModelAdmin):
    form = PromotionRuleForm
    list_display = [
        "coupon",
        "id",
        "status",
    ]
    list_filter = [
        "status",
    ]
    search_fields = [
        "id",
        "coupon__code",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Promotion Rule Information"),
            {
                "fields": ("coupon",),
            },
        ),
        (
            _("Customer groups"),
            {
                "fields": ("customer_groups",),
            },
        ),
        (
            _("Categories"),
            {
                "fields": ("categories",),
            },
        ),
        (
            _("Products"),
            {
                "fields": ("products",),
            },
        ),
        (
            _("Status Information"),
            {
                "fields": ("status",),
            },
        ),
        (
            _("Source Information"),
            {
                "fields": (
                    "external_id",
                    "source",
                ),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
        models.ManyToManyField: {"widget": autocomplete.ModelSelect2Multiple()},
    }
