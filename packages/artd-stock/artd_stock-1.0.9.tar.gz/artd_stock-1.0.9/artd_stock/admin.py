from django.contrib import admin
from .models import Stock, StockLog
from django.utils.translation import gettext_lazy as _


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "partner",
        "id",
        "stock",
        "stock_min",
        "stock_max",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "partner__name",
        "product__name",
        "product__sku",
        "stock",
        "stock_min",
        "stock_max",
        "status",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = [
        (
            "Stock",
            {
                "fields": [
                    "product",
                    "partner",
                ]
            },
        ),
        (
            _("Stock Information"),
            {
                "fields": (
                    "stock",
                    "stock_min",
                    "stock_max",
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
    ]


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = (
        "partner",
        "product",
        "stock",
        "stock_min",
        "stock_max",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "partner__name",
        "product__name",
        "stock",
        "stock_min",
        "stock_max",
        "status",
    )
    readonly_fields = [
        "created_at",
        "updated_at",
        "status",
        "partner",
        "product",
        "stock",
        "stock_min",
        "stock_max",
        "source",
        "external_id",
    ]
    fieldsets = [
        (
            "Stock",
            {
                "fields": [
                    "product",
                    "partner",
                ]
            },
        ),
        (
            _("Stock Information"),
            {
                "fields": (
                    "stock",
                    "stock_min",
                    "stock_max",
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
    ]
