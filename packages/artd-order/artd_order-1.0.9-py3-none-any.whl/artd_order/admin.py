from django.contrib import admin
from artd_order.models import (
    OrderStatus,
    Order,
    OrderProduct,
    OrderStatusHistory,
    OrderPaymentHistory,
    OrderDeliveryMethod,
    OrderAdress,
    OrderPaymentMethod,
)
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderProductInline(admin.StackedInline):
    model = OrderProduct
    extra = 1
    show_change_link = True
    fields = (
        "product",
        "quantity",
    )


class OrderAdressInline(admin.StackedInline):
    model = OrderAdress
    extra = 2
    show_change_link = True
    fields = (
        "address_type",
        "city",
        "phone",
        "address",
        "firstname",
        "lastname",
        "email",
    )


class OrderPaymentHistoryInline(admin.StackedInline):
    model = OrderPaymentHistory
    extra = 1
    show_change_link = True
    fields = ("payment_code",)


class OrderStatusHistoryInline(admin.StackedInline):
    model = OrderStatusHistory
    extra = 1
    show_change_link = True
    fields = (
        "order_status",
        "comment",
    )


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = (
        "status_description",
        "id",
        "status_code",
        "status",
    )
    search_fields = (
        "id",
        "status_code",
        "status_description",
    )
    list_filter = ("status",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    fieldsets = [
        (
            _("Order status information"),
            {
                "fields": (
                    "status_code",
                    "status_description",
                )
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
                    "json_data",
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
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(OrderDeliveryMethod)
class OrderDeliveryMethodAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_method_description",
        "id",
        "delivery_method_code",
        "partner",
        "status",
    )
    search_fields = (
        "id",
        "delivery_method_code",
        "delivery_method_description",
        "partner__name",
    )
    list_filter = ("status",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    fieldsets = [
        (
            _("Order delivery method information"),
            {
                "fields": (
                    "delivery_method_code",
                    "delivery_method_description",
                    "partner",
                )
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
                    "json_data",
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
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "increment_id",
        "id",
        "partner",
        "customer",
        "order_status",
        "created_at",
        "payment_code",
        "grand_total",
        "status",
    )
    search_fields = (
        "id",
        "payment_code",
        "partner__name",
        "order_status__status_code",
        "created_at",
        "increment_id",
        "customer__email",
    )
    list_filter = (
        "partner",
        "payment_code",
        "order_status",
        "status",
    )
    ordering = ("created_at",)
    readonly_fields = (
        "id",
        "increment_id",
        "created_at",
        "updated_at",
        "payment_code",
        "discount_amount",
        "weight",
        "subtotal",
        "tax_amount",
        "shipping_amount",
        "grand_total",
        "total_paid",
    )

    fieldsets = [
        (
            _("Order information"),
            {
                "fields": (
                    "increment_id",
                    "partner",
                    "customer",
                    "order_status",
                    "payment_code",
                    "order_payment_method",
                    "delivery_method",
                    "weight",
                )
            },
        ),
        (
            _("Disccount Information"),
            {
                "fields": (
                    "coupon_code",
                    "discount_amount",
                ),
            },
        ),
        (
            _("Total Information"),
            {
                "fields": (
                    "subtotal",
                    "tax_amount",
                    "shipping_amount",
                    "grand_total",
                    "total_paid",
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
                    "json_data",
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

    inlines = [
        OrderProductInline,
        OrderAdressInline,
        OrderPaymentHistoryInline,
        OrderStatusHistoryInline,
    ]

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "base_amount",
        "total",
        "status",
        "created_at",
    )
    search_fields = (
        "id",
        "order__increment_id",
        "product__name",
        "quantity",
        "base_amount",
        "total",
    )
    list_filter = ("status",)
    ordering = ("order",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = [
        (
            _("Order product information"),
            {
                "fields": (
                    "order",
                    "product",
                    "quantity",
                )
            },
        ),
        (
            _("Order product totals information"),
            {
                "fields": (
                    "base_amount",
                    "base_discount_amount",
                    "base_tax_amount",
                    "base_total",
                    "amount",
                    "discount_amount",
                    "tax_amount",
                    "total",
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
                    "json_data",
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

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "id",
        "order_status",
        "created_at",
    )
    search_fields = (
        "id",
        "order__increment_id",
        "order_status__status_code",
        "comment",
    )
    list_filter = (
        "order_status",
        "status",
    )
    ordering = ("order",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = [
        (
            _("Order status history information"),
            {
                "fields": (
                    "order",
                    "order_status",
                    "comment",
                )
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
                    "json_data",
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

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(OrderPaymentHistory)
class OrderPaymentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "id",
        "payment_code",
        "created_at",
        "status",
    )
    search_fields = (
        "id",
        "order__increment_id",
        "payment_code",
        "order__partner__name",
    )
    list_filter = (
        "order",
        "payment_code",
        "created_at",
    )
    ordering = ("order",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    fieldsets = [
        (
            _("Order payment history information"),
            {
                "fields": (
                    "order",
                    "payment_code",
                )
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
                    "json_data",
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

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(OrderAdress)
class OrderAdressAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "id",
        "address_type",
        "city",
        "phone",
        "created_at",
        "status",
    )
    search_fields = (
        "id",
        "order__increment_id",
        "address_type",
        "city__name",
        "address",
        "phone",
    )
    list_filter = (
        "address_type",
        "status",
    )
    ordering = ("order",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    fieldsets = [
        (
            _("Order address information"),
            {
                "fields": (
                    "order",
                    "address_type",
                    "city",
                    "phone",
                    "address",
                    "firstname",
                    "lastname",
                    "email",
                )
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
                    "json_data",
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
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(OrderPaymentMethod)
class OrderPaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "code",
        "partner",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "id",
        "name",
        "code",
        "partner__name",
    )
    list_filter = ("status",)
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    fieldsets = [
        (
            _("Order payment method information"),
            {
                "fields": (
                    "name",
                    "code",
                    "partner",
                )
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
                    "json_data",
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
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
