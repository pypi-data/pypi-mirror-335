from django.core.management.base import BaseCommand

from artd_order.data.order_status import ORDER_STATUSES as STATUSES
from artd_order.models import OrderStatus


class Command(BaseCommand):
    help = "Create order statuses"

    def handle(self, *args, **kwargs):
        for status in STATUSES:
            if OrderStatus.objects.filter(id=status[0]).count() == 0:
                OrderStatus.objects.create(
                    id=status[0],
                    status_code=status[1],
                    status_description=status[2],
                )
                self.stdout.write(self.style.SUCCESS(f"{status[2]} was created"))
            else:
                status_obj = OrderStatus.objects.get(
                    id=status[0],
                )
                status_obj.status_code = status[1]
                status_obj.status_description = status[2]
                status_obj.save()
                self.stdout.write(self.style.WARNING(f"{status[2]} was updated"))
