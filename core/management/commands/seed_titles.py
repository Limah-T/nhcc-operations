from django.core.management.base import BaseCommand

from core.models import Title


class Command(BaseCommand):

    help = "Seed default titles into the database"

    def handle(self, *args, **options):

        titles = [
            "Mr",
            "Mrs",
            "Miss",
            "Ms",
            "Dr",
            "Prof",
            "Chief",
            "Alhaji",
            "Alhaja",
            "Engr",
            "Arch",
            "Barr",
            "Hon",
            "Rev",
            "Pastor",
            "Bishop",
            "Sir",
            "Dame",
        ]

        for order, title_name in enumerate(
            titles,
            start=1
        ):

            title, created = Title.objects.get_or_create(
                name=title_name,
                defaults={
                    "display_order": order,
                    "is_active": True,
                }
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {title.name}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"Already exists: {title.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Title seeding completed successfully."
            )
        )