from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from artd_partner.models import Partner
from django.core.exceptions import ValidationError
from artd_product.models import Product, Category
from artd_customer.models import CustomerGroup


class PromotionBaseModel(models.Model):
    status = models.BooleanField(
        _("status"),
        help_text=_("Designates whether this record is active or not."),
        default=True,
    )
    created_at = models.DateTimeField(
        _("created at"),
        help_text=_("Date time on which the object was created."),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        help_text=_("Date time on which the object was last updated."),
        auto_now=True,
    )
    source = models.JSONField(
        "Source",
        null=True,
        blank=True,
        help_text=_("Source"),
    )
    external_id = models.CharField(
        "External ID",
        max_length=255,
        null=True,
        blank=True,
        help_text=_("External ID"),
    )

    class Meta:
        abstract = True


class Coupon(PromotionBaseModel):
    partner = models.ForeignKey(
        Partner,
        verbose_name=_("partner"),
        help_text=_("Partner."),
        on_delete=models.CASCADE,
    )
    code = models.SlugField(
        _("code"),
        help_text=_("Coupon code."),
        max_length=50,
        unique=True,
    )
    name = models.CharField(
        _("name"),
        help_text=_("Coupon name."),
        max_length=100,
    )
    start_date = models.DateTimeField(
        _("start date"),
        help_text=_("Coupon start date."),
    )
    end_date = models.DateTimeField(
        _("end date"),
        help_text=_("Coupon end date."),
    )
    is_percentage = models.BooleanField(
        _("is percentage"),
        help_text=_("Designates whether this coupon is percentage or not."),
        default=True,
    )
    value = models.FloatField(
        _("value"),
        help_text=_("Coupon value."),
        default=0,
    )
    uses_per_coupon = models.PositiveIntegerField(
        _("uses per coupon"),
        help_text=_("Number of uses per coupon."),
        default=1,
    )
    uses = models.PositiveIntegerField(
        _("uses"),
        help_text=_("Number of uses."),
        default=0,
    )

    def use_coupon(self):
        if self.uses >= self.uses_per_coupon:
            self.status = False
        self.uses += 1
        self.save()
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")


class PromotionRule(PromotionBaseModel):
    coupon = models.OneToOneField(
        Coupon,
        verbose_name=_("coupon"),
        help_text=_("Coupon."),
        on_delete=models.CASCADE,
    )
    customer_groups = models.ManyToManyField(
        CustomerGroup,
        verbose_name=_("customer types"),
        help_text=_("Customer types."),
    )
    categories = models.ManyToManyField(
        Category,
        verbose_name=_("product categories"),
        help_text=_("Product categories."),
    )
    products = models.ManyToManyField(
        Product,
        verbose_name=_("selected products"),
        help_text=_("Selected products."),
    )

    class Meta:
        verbose_name = _("promotion rule")
        verbose_name_plural = _("promotion rules")

    def __str__(self):
        return f"Promotion rule for {self.coupon}"
