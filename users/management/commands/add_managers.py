from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


class Command(BaseCommand):
    help = "Добавляет пользователей в группу Manager без пароля. Пароль задаётся через восстановление."

    def handle(self, *args, **options):
        managers_group = Group.objects.get(name="Manager")

        managers_emails = [
            "manager2@example.com",
            "manager3@example.com",
        ]

        for email in managers_emails:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"is_active": True},
            )

            user.groups.add(managers_group)

            if created:
                user.set_unusable_password()
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Создан менеджер {email}. Пароль задаётся через восстановление."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Менеджер уже существует: {email}")
                )
