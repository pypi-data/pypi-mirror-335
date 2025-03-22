from django.core.management.base import BaseCommand
from artd_customer.models import MacroTaxSegment, TaxSegment
from artd_location.models import Country
from artd_customer.data.tax_segments import TAX_SEGMENTS


class Command(BaseCommand):
    help = "Create or update MacroTaxSegments and TaxSegments from predefined data"

    def handle(self, *args, **kwargs):
        for segment_data in TAX_SEGMENTS:
            country_id = segment_data["country_id"]
            macro_tax_segment_id = segment_data["macro_tax_segment_id"]
            macro_tax_segment_name = segment_data["macro_tax_segment_name"]
            macro_tax_segment_code = segment_data["macro_tax_segment_code"]
            segments = segment_data["segments"]

            # Obtener o crear el país
            try:
                country = Country.objects.get(id=country_id)
            except Country.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Country with id {country_id} does not exist.")
                )
                continue

            # Crear o actualizar MacroTaxSegment
            macro_tax_segment, created = MacroTaxSegment.objects.update_or_create(
                id=macro_tax_segment_id,
                defaults={
                    "name": macro_tax_segment_name,
                    "code": macro_tax_segment_code,
                    "country": country,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"MacroTaxSegment '{macro_tax_segment_name}' created."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"MacroTaxSegment '{macro_tax_segment_name}' updated."
                    )
                )

            # Crear o actualizar los segmentos relacionados (TaxSegments)
            for segment in segments:
                tax_segment_id = segment["tax_segment_id"]
                tax_segment_name = segment["tax_segment_name"]
                tax_segment_code = segment["tax_segment_code"]

                tax_segment, created = TaxSegment.objects.update_or_create(
                    id=tax_segment_id,
                    defaults={
                        "name": tax_segment_name,
                        "code": tax_segment_code,
                        "macrosegment": macro_tax_segment,
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"TaxSegment '{tax_segment_name}' created.")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"TaxSegment '{tax_segment_name}' updated.")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "All MacroTaxSegments and TaxSegments have been processed."
            )
        )
