from django.core.management.base import BaseCommand
from artd_customer.models import (
    CustomerType,
    CustomerPersonType,
    CustomerDocumentType,
)
from artd_customer.data.cutomer_vat import (
    CUSTOMER_TYPES,
    CUSTOMER_PERSON_TYPES,
    DOCUMENT_TYPES,
)


class Command(BaseCommand):
    help = "Create or update CustomerType, CustomerPersonType and CustomerDocumentType"

    def handle(self, *args, **kwargs):
        for customer_type in CUSTOMER_TYPES:
            obj, created = CustomerType.objects.update_or_create(
                code=customer_type["code"],
                defaults={
                    "name": customer_type["name"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"CustomerType created: {obj.code} - {obj.name}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"CustomerType updated: {obj.code} - {obj.name}")
                )

        for customer_person_type in CUSTOMER_PERSON_TYPES:
            obj, created = CustomerPersonType.objects.update_or_create(
                code=customer_person_type["code"],
                defaults={
                    "name": customer_person_type["name"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CustomerPersonType created: {obj.code} - {obj.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CustomerPersonType updated: {obj.code} - {obj.name}"
                    )
                )

        for document_type in DOCUMENT_TYPES:
            obj, created = CustomerDocumentType.objects.update_or_create(
                code=document_type["code"],
                defaults={
                    "name": document_type["name"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CustomerDocumentType created: {obj.code} - {obj.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CustomerDocumentType updated: {obj.code} - {obj.name}"
                    )
                )
