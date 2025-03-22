from django.contrib import admin
from .models import Ally, Alliance, AllianceStatusChange, AllianceCommentChange
from django.utils.translation import gettext_lazy as _


@admin.register(Ally)
class AllyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "dni",
        "email",
        "city_new",
        "address",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "city_new",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "dni",
        "email",
        "city_new__name",
        "address",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Alliance)
class AllianceAdmin(admin.ModelAdmin):
    list_display = (
        "ally",
        "partner",
        "service",
        "benefit",
        "benefit_type",
        "alliance_status",
        "code_alliance",
        "comments",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "benefit_type",
        "alliance_status",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "ally__name",
        "partner__name",
        "service",
        "benefit",
        "code_alliance",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "code_alliance",
        "created_at",
        "updated_at",
        "coupons",
    )
    fieldsets = (
        (
            _(""),
            {
                "fields": (
                    "ally",
                    "partner",
                    "service",
                )
            },
        ),
        (
            _("Alliance detail"),
            {
                "fields": (
                    "benefit",
                    "benefit_type",
                    "value",
                    "alliance_status",
                    "code_alliance",
                    "comments",
                )
            },
        ),
        (
            _("Coupon detail"),
            {
                "fields": (
                    "coupon_quantity",
                    "uses_per_coupon",
                    "coupon_prefix",
                    "coupon_suffix",
                    "is_permanent",
                    "start_at",
                    "end_at",
                )
            },
        ),
        (
            _("Coupons"),
            {"fields": ("coupons",)},
        ),
        (
            _("Stauts"),
            {"fields": ("status",)},
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


@admin.register(AllianceStatusChange)
class AllianceStatusChangeAdmin(admin.ModelAdmin):
    list_display = (
        "alliance",
        "new_status",
        "old_status",
        "change_date",
        "changed_by",
    )
    list_filter = (
        "change_date",
        "alliance__partner",
    )
    search_fields = (
        "alliance__partner__name",
        "new_status",
        "change_date",
        "changed_by__name",
    )


@admin.register(AllianceCommentChange)
class AllianceCommentChange(admin.ModelAdmin):
    list_display = (
        "alliance",
        "new_comment",
        "old_comment",
        "change_date",
        "changed_by",
    )
    list_filter = (
        "change_date",
        "alliance__partner",
    )
    search_fields = (
        "alliance__partner__name",
        "new_comment",
        "change_date",
        "changed_by__name",
    )
