from django.utils.translation import gettext_lazy as _

ORDER_DELIVERY_METHODS = (
    (
        0,
        "default",
        _("Default"),
    ),
    (
        1,
        "pickup",
        _("Pickup"),
    ),
    (
        2,
        "post",
        _("Post"),
    ),
    (
        3,
        "other",
        _("Other"),
    ),
    (
        4,
        "courier",
        _("Courier"),
    ),
)
