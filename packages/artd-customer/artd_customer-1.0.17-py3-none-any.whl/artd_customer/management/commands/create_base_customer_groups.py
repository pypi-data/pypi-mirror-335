from django.core.management.base import BaseCommand
from artd_customer.models import CustomerGroup
from artd_partner.models import Partner

CUSTOMER_GROUPS = [
    {
        "group_code": "new",
        "group_name": "New customers",
        "description": "New customers",
    },
    {
        "group_code": "wholesale",
        "group_name": "Wholesale customers",
        "description": "Wholesale customers",
    },
    {
        "group_code": "vip",
        "group_name": "VIP customers",
        "description": "VIP customers",
    },
]


class Command(BaseCommand):
    help = "Create the base customer groups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--partner_slug",
            type=str,
            help="Slug of the partner",
            default=None,
        )

    def handle(self, *args, **options):
        partner_slug = options["partner_slug"]
        print(partner_slug)
        if partner_slug:
            complement = f"_{partner_slug}"
        else:
            complement = ""
        for group in CUSTOMER_GROUPS:
            try:
                if (
                    CustomerGroup.objects.filter(
                        group_code=group["group_code"] + complement,
                        partner__partner_slug=partner_slug,
                    ).count()
                    == 0
                ):
                    customer_group = CustomerGroup.objects.create(
                        group_code=group["group_code"] + complement,
                        group_name=group["group_name"] + complement,
                        group_description=group["description"],
                    )
                    if partner_slug:
                        partner = Partner.objects.filter(
                            partner_slug=partner_slug
                        ).last()
                        if partner:
                            customer_group.partner = partner
                            customer_group.save()
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"Partner {partner_slug} not found")
                            )
                    self.stdout.write(
                        self.style.WARNING(
                            f'Customer group {group["group_code"]} created'
                        )
                    )
                else:
                    if partner_slug:
                        partner = Partner.objects.filter(
                            partner_slug=partner_slug
                        ).last()
                        if partner:
                            customer_group = CustomerGroup.objects.filter(
                                group_code=group["group_code"] + complement,
                                partner=partner,
                            ).last()
                            customer_group.group_name = group["group_name"] + complement
                            customer_group.group_description = group["description"]
                            customer_group.save()
                        else:
                            self.stdout.write(
                                self.style.ERROR(f"Partner {partner_slug} not found")
                            )

                    else:
                        customer_group = CustomerGroup.objects.filter(
                            group_code=group["group_code"] + complement
                        ).last()
                        customer_group.group_name = group["group_name"] + complement
                        customer_group.group_description = group["description"]
                        customer_group.save()
                    self.stdout.write(
                        self.style.ERROR(
                            f'Customer group {group["group_code"]} updated'
                        )
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
