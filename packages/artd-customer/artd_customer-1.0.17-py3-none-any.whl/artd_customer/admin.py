from django.contrib import admin
from artd_customer.models import (
    Customer,
    Tag,
    CustomerTag,
    CustomerAddress,
    CustomerAdditionalFields,
    CustomerGroup,
    CustomerGroupChangeLog,
    MacroTaxSegment,
    TaxSegment,
    CustomerDocumentType,
    CustomerPersonType,
    CustomerType,
)
from django_json_widget.widgets import JSONEditorWidget
from django.db import models
from django.utils.translation import gettext_lazy as _
from django import forms


class CustomerTagInline(admin.StackedInline):
    model = CustomerTag
    extra = 0
    fields = (
        "tag",
        "status",
    )


class CustomerAddressInline(admin.StackedInline):
    model = CustomerAddress
    extra = 0
    fields = (
        "city",
        "phone",
        "address",
        "status",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "id",
        "partner",
        "status",
    ]
    search_fields = [
        "id",
        "description",
        "partner__name",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
    ]
    fieldsets = (
        (
            _("Tag Information"),
            {
                "fields": (
                    "description",
                    "partner",
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
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = [
        "group_name",
        "partner",
        "id",
        "group_code",
        "status",
    ]
    search_fields = [
        "group_name",
        "id",
        "group_code",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Group Information"),
            {
                "fields": (
                    "partner",
                    "group_name",
                    "group_code",
                    "group_description",
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
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "id",
        "tag",
        "status",
    ]
    search_fields = [
        "customer__name",
        "customer__last_name",
        "customer__email",
        "customer__phone",
        "tag__description",
        "id",
    ]
    list_filter = [
        "status",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Tag Information"),
            {
                "fields": (
                    "customer",
                    "tag",
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
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "id",
        "city",
        "phone",
        "address",
        "status",
    ]
    search_fields = [
        "id",
        "customer__email",
        "customer__phone",
        "customer__name",
        "customer__last_name",
        "city__name",
        "phone",
        "address",
    ]
    list_filter = [
        "status",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Address Information"),
            {
                "fields": (
                    "customer",
                    "city",
                    "phone",
                    "address",
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
            _("Other Information"),
            {
                "fields": ("other_data",),
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
    )

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(CustomerAdditionalFields)
class CustomerAdditionalFieldsAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "partner__name",
        "name",
        "field_type",
        "label",
        "required",
    ]
    list_display = [
        "name",
        "id",
        "field_type",
        "label",
        "partner",
        "required",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
        "field_type",
        "required",
    ]
    fieldsets = (
        (
            _("Additional Field Information"),
            {
                "fields": (
                    "partner",
                    "name",
                    "field_type",
                    "label",
                    "required",
                ),
            },
        ),
        (
            _("Field Values"),
            {
                "fields": ("field_values",),
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
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(CustomerGroupChangeLog)
class CustomerGroupChangeLogAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "customer",
        "old_group",
        "new_group",
    ]
    list_display = [
        "customer",
        "old_group",
        "new_group",
        "status",
        "created_at",
        "updated_at",
    ]
    readonly_fields = [
        "customer",
        "old_group",
        "new_group",
        "status",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Group Change Log Information"),
            {
                "fields": (
                    "customer",
                    "old_group",
                    "new_group",
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
    )
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "name",
        "last_name",
        "phone",
        "email",
        "document",
        "partner__name",
    ]
    list_display = [
        "id",
        "name",
        "last_name",
        "phone",
        "email",
        "document",
        "status",
    ]
    list_filter = [
        "status",
        "customer_group",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Information"),
            {
                "fields": (
                    "partner",
                    "name",
                    "last_name",
                    "trade_name",
                    "phone",
                    "email",
                    "birth_date",
                    "document_type",
                    "document",
                    "document_check_digit",
                    "city",
                    "customer_group",
                ),
            },
        ),
        (
            _("Fiscal information"),
            {
                "fields": (
                    "vat_responsible",
                    "tax_segment",
                    "customer_type",
                    "customer_person_type",
                ),
            },
        ),
        (
            _("Other Information"),
            {
                "fields": ("other_data",),
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
    )
    inlines = [
        CustomerTagInline,
        CustomerAddressInline,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(MacroTaxSegment)
class MacroTaxSegmentAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "name",
        "code",
        "country__spanish_name",
        "country__english_name",
        "country__nom",
    ]
    list_display = [
        "id",
        "country",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
        "country",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Macro Tax Segment Information"),
            {
                "fields": (
                    "country",
                    "name",
                    "code",
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
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(TaxSegment)
class TaxSegmentAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "name",
        "code",
        "macrosegment__name",
        "macrosegment__country__spanish_name",
        "macrosegment__country__english_name",
        "macrosegment__country__nom",
    ]
    list_display = [
        "id",
        "macrosegment",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
        "macrosegment",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Tax Segment Information"),
            {
                "fields": (
                    "macrosegment",
                    "name",
                    "code",
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
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(CustomerType)
class CustomerTypeAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "name",
        "code",
    ]
    list_display = [
        "id",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Type Information"),
            {
                "fields": (
                    "name",
                    "code",
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
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(CustomerPersonType)
class CustomerPersonTypeAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "name",
        "code",
    ]
    list_display = [
        "id",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Person Type Information"),
            {
                "fields": (
                    "name",
                    "code",
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
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(CustomerDocumentType)
class CustomerDocumentTypeAdmin(admin.ModelAdmin):
    search_fields = [
        "id",
        "name",
        "code",
    ]
    list_display = [
        "id",
        "name",
        "code",
        "status",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "status",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (
            _("Customer Document Type Information"),
            {
                "fields": (
                    "name",
                    "code",
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
            _("Timestamps"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
