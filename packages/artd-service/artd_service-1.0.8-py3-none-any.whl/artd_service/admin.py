from django.contrib import admin
from artd_service.models import Service, InstalledApp, AppPermission, ServiceApps


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "slug",
        "created_at",
        "updated_at",
        "status",
    )


@admin.register(InstalledApp)
class InstalledAppAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "installed_app",
        "name",
        "codename",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(ServiceApps)
class ServiceAppsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service",
        "status",
        "created_at",
        "updated_at",
    )
