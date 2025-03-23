from django.utils.translation import gettext_lazy as _

ORDER_STATUSES = (
    (
        0,
        "new",
        _("New"),
    ),
    (
        1,
        "in_progress",
        _("In progress"),
    ),
    (
        2,
        "done",
        _("Done"),
    ),
    (
        3,
        "canceled",
        _("Canceled"),
    ),
    (
        4,
        "closed",
        _("Closed"),
    ),
    (
        5,
        "pending_payment",
        _("Pending payment"),
    ),
    (
        6,
        "failed_payment",
        _("Failed payment"),
    ),
    (
        7,
        "success_payment",
        _("Success payment"),
    ),
)
