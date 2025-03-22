# management/commands/insert_installed_apps.py
from django.core.management.base import BaseCommand
from django.conf import settings
from artd_service.models import InstalledApp


class Command(BaseCommand):
    help = "Insert installed apps into the InstalledApp model"

    def handle(self, *args, **kwargs):
        # Obtener el listado de aplicaciones instaladas
        installed_apps = settings.INSTALLED_APPS

        # Insertar cada aplicación en el modelo InstalledApp
        for app in installed_apps:
            # Excluir las aplicaciones predeterminadas de Django
            if app.startswith("django."):
                continue

            # Crear o actualizar el registro en la base de datos
            InstalledApp.objects.get_or_create(name=app)

        self.stdout.write(
            self.style.SUCCESS("Successfully inserted installed apps into the model")
        )
