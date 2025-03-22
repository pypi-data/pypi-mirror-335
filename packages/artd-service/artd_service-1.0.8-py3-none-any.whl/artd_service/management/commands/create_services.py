import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from artd_service.models import Service
from artd_service.data.service_data import SERVICES


class Command(BaseCommand):
    help = "Create or update services with images"

    def handle(self, *args, **options):
        """
        Main entry point for the command. Iterates through the SERVICES list,
        creates or updates Service instances, and downloads and saves images from URLs.
        """
        for service in SERVICES:
            service_id = service[0]
            name = service[2]
            slug = service[1]
            description = service[2]
            image_url = service[3]

            # Create or update the service instance
            service_instance, created = Service.objects.update_or_create(
                id=service_id,
                defaults={
                    "name": name,
                    "slug": slug,
                    "description": description,
                },
            )

            # Handle the image logic
            if service_instance.image and service_instance.image.name:
                if service_instance.image.url != image_url:
                    self._save_image_from_url(image_url, service_instance)
                    self.stdout.write(
                        self.style.SUCCESS(f"Service {name} image updated!")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"{name} service status already exists!")
                    )
            else:
                self._save_image_from_url(image_url, service_instance)
                self.stdout.write(self.style.SUCCESS(f"Service {name} image added!"))

    def _save_image_from_url(self, url, model_instance):
        """
        Downloads an image from the specified URL and saves it to the ImageField of the model instance.

        :param url: URL of the image to download.
        :param model_instance: Instance of the model where the image will be saved.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure the request was successful

            # Get the filename from the URL
            filename = url.split("/")[-1]

            # Create an in-memory file with the content of the image
            image_content = ContentFile(response.content)

            # Save the image to the ImageField
            model_instance.image.save(filename, image_content)

            # Save the model instance
            model_instance.save()

            print("Image successfully saved in the image field of model")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading the image: {e}")
