from django.contrib import admin
from .models import Channel, Credential, Messagge, Provider, CustomerChannel
from django_json_widget.widgets import JSONEditorWidget
from django.db import models


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "status", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    fields = ("name", "slug", "status")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Credential)
class CredentialsAdmin(admin.ModelAdmin):
    list_display = ("channel", "provider", "credentials")
    search_fields = ("channel__name", "provider")
    list_filter = ("provider",)
    fields = ("channel", "provider", "credentials")

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Messagge)
class MessaageAdmin(admin.ModelAdmin):
    search_fields = ("channel__name", "customer")
    list_filter = ("result", "channel__name")
    list_display = (
        "id",
        "messages",
        "channel",
        "provider",
        "customer",
        "retries",
        "created_at",
    )
    fields = ("messages", "channel", "customer", "provider", "result", "retries")

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "status", "created_at", "updated_at")
    search_fields = ("name", "slug")
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    fields = ("name", "slug", "status")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CustomerChannel)
class CustomerChannelAdmin(admin.ModelAdmin):
    list_display = ("customer", "channel")
    search_fields = ("customer__name", "channel__name")
    list_filter = ("channel", "customer")


# Registra el modelo con el administrador
