from django.db import models
from django.utils.translation import gettext_lazy as _
from artd_partner.models import Partner
from artd_product.models import Product


class StockBase(models.Model):
    """Model definition for Stock."""

    created_at = models.DateTimeField(
        _("Created at"),
        help_text=_("Created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Updated at"),
        help_text=_("Updated at"),
        auto_now=True,
    )
    status = models.BooleanField(
        _("Status"),
        default=True,
        help_text=_("Status"),
    )
    partner = models.ForeignKey(
        Partner,
        verbose_name=_("Partner"),
        on_delete=models.CASCADE,
        help_text=_("Partner"),
    )
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        help_text=_("Product"),
    )
    stock = models.IntegerField(
        _("Stock"),
        help_text=_("Stock"),
        default=0,
    )
    stock_min = models.IntegerField(
        _("Stock min"),
        help_text=_("Stock min"),
        default=0,
    )
    stock_max = models.IntegerField(
        _("Stock max"),
        help_text=_("Stock max"),
        default=0,
    )
    source = models.JSONField(
        _("Source"),
        help_text=_("Source"),
        blank=True,
        null=True,
    )
    external_id = models.CharField(
        _("External ID"),
        help_text=_("External ID"),
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class StockLog(StockBase):
    """Model definition for Stock."""

    class Meta:
        verbose_name = _("Stock log")
        verbose_name_plural = _("Stock logs")

    def __str__(self):
        """Unicode representation of Stock."""
        return f"LOG #{self.id}"


class Stock(StockBase):
    class Meta:
        unique_together = (
            "partner",
            "product",
        )
        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.product}"

    def save(self, *args, **kwargs):
        StockLog.objects.create(
            partner=self.partner,
            product=self.product,
            stock=self.stock,
            stock_min=self.stock_min,
            stock_max=self.stock_max,
        )
        super(Stock, self).save(*args, **kwargs)
