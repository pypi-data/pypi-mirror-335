from django.core.management.base import BaseCommand

from artd_order.data.order_delivery_methods import ORDER_DELIVERY_METHODS as METHODS
from artd_order.models import OrderDeliveryMethod
from artd_partner.models import Partner


class Command(BaseCommand):
    help = "Create order delivery methods in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "partner_slug", type=str, help="Mandatory value for partner_slug"
        )

    def handle(self, *args, **kwargs):
        partner_slug = kwargs["partner_slug"]
        if Partner.objects.filter(partner_slug=partner_slug).count() > 0:
            partner = Partner.objects.get(partner_slug=partner_slug)
            for method in METHODS:
                if OrderDeliveryMethod.objects.filter(id=method[0]).count() == 0:
                    OrderDeliveryMethod.objects.create(
                        id=method[0],
                        partner=partner,
                        delivery_method_code=method[1],
                        delivery_method_description=method[2],
                    )
                    self.stdout.write(self.style.SUCCESS(f"{method[2]} was created"))
                else:
                    status_obj = OrderDeliveryMethod.objects.get(
                        id=method[0],
                    )
                    status_obj.delivery_method_code = method[1]
                    status_obj.delivery_method_description = method[2]
                    status_obj.save()
                    self.stdout.write(self.style.WARNING(f"{method[2]} was updated"))
        else:
            self.stdout.write(
                self.style.ERROR(f"Partner with slug {partner_slug} does not exist")
            )
