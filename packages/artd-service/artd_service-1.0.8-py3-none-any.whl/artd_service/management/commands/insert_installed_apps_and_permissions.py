# management/commands/insert_installed_apps_and_permissions.py
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Permission
from django.apps import apps
from artd_service.models import (
    InstalledApp,
    AppPermission,
)  # Asegúrate de importar tus modelos correctamente


class Command(BaseCommand):
    help = "Insert installed apps and their permissions into the database"

    def handle(self, *args, **kwargs):
        # Obtener el listado de aplicaciones instaladas
        installed_apps = settings.INSTALLED_APPS

        for app in installed_apps:
            # Excluir las aplicaciones predeterminadas de Django
            if app.startswith("django."):
                continue

            # Crear o actualizar el registro en la base de datos para la aplicación
            installed_app, created = InstalledApp.objects.get_or_create(name=app)

            try:
                # Obtener el AppConfig para la aplicación
                app_config = apps.get_app_config(app.split(".")[-1])
            except LookupError:
                self.stdout.write(
                    self.style.WARNING(
                        f'No installed app with label {app.split(".")[-1]}'
                    )
                )
                continue

            # Obtener todos los modelos de la aplicación
            for model in app_config.get_models():
                # Obtener todos los permisos para el modelo
                permissions = Permission.objects.filter(
                    content_type__app_label=app_config.label,
                    content_type__model=model._meta.model_name,
                )
                for perm in permissions:
                    # Crear o actualizar el registro en la base de datos para el permiso
                    AppPermission.objects.get_or_create(
                        installed_app=installed_app,
                        name=perm.name,
                        codename=perm.codename,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully inserted installed apps and their permissions into the database"
            )
        )
