from typing import Final

from django.db import models
from django.utils import timezone

from users.models import CustomUser


class Recipient(models.Model):
    """
    Модель получателя рассылки.
    Хранит email, ФИО, комментарий, дату создания и владельца.
    Используется для формирования списка клиентов,
    которым могут отправляться письма в рамках рассылок.
    """

    email: str = models.EmailField(max_length=50, unique=True)

    full_name: str = models.CharField(max_length=150, verbose_name="Фамилия Имя Отчество")

    comment: str = models.TextField(verbose_name="Комментарий")

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    owner: CustomUser = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Владелец", related_name="recipients"
    )

    def __str__(self):
        return f"{self.full_name} {self.email}"

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        ordering = ["email"]


class Message(models.Model):
    """
    Модель письма для рассылки.
    Хранит тему, текст письма и владельца.
    """

    subject: str = models.CharField(max_length=200, verbose_name="Тема письма")

    content: str = models.TextField(verbose_name="Текст письма")

    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    owner: CustomUser = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Владелец", related_name="messages"
    )

    def __str__(self) -> str:
        return self.subject

    class Meta:
        verbose_name = "письмо"
        verbose_name_plural = "письма"
        ordering = ["created_at"]


class Mailing(models.Model):
    """
    Модель рассылки.
    Содержит время начала и окончания, статус, выбранное письмо
    и список получателей.
    """

    STATUS_CREATED: Final[str] = "created"
    STATUS_RUNNING: Final[str] = "running"
    STATUS_FINISHED: Final[str] = "finished"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_FINISHED, "Завершена"),
    ]

    start_time: models.DateTimeField = models.DateTimeField(verbose_name="Время старта", null=False, blank=False)

    end_time: models.DateTimeField = models.DateTimeField(verbose_name="Время окончания", null=False, blank=False)

    status: str = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED, verbose_name="Статус"
    )

    message: Message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Письмо", related_name="mailings"
    )

    recipients: models.ManyToManyField = models.ManyToManyField(
        Recipient, verbose_name="Получатели", related_name="mailings"
    )

    owner: CustomUser = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Владелец", related_name="mailings"
    )

    is_enabled: bool = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Менеджер может отключить рассылку. Отключённая рассылка не отправляется.",
    )

    def calculate_status(self) -> str:
        """
        Вычисляет статус рассылки на основании текущего времени.
        В БД ничего не сохраняет.
        """

        now = timezone.now()

        if now < self.start_time:
            return self.STATUS_CREATED

        if self.start_time <= now <= self.end_time:
            return self.STATUS_RUNNING

        return self.STATUS_FINISHED

    def update_status(self):
        """
        Пересчитывает статус и сохраняет в БД, если он изменился.
        """
        new_status = self.calculate_status()
        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=["status"])
        return new_status

    def __str__(self) -> str:
        return f"Старт: {self.start_time} " f"Окончание: {self.end_time} " f"Статус:{self.calculate_status()}"

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ["start_time"]
        permissions = [
            ("can_disable_mailing", "Может отключать рассылки"),
        ]


class MailingAttempt(models.Model):
    """
    Модель попытки отправки письма.
    Хранит информацию о результате отправки письма одному получателю.
    """

    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failed", "Не успешно"),
    ]

    attempt_time: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status: str = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response: str = models.TextField(verbose_name="Ответ сервера", blank=True, null=True)
    mailing: Mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="attempts"
    )
    recipient: Recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, verbose_name="Получатель")

    def __str__(self) -> str:
        return f"{self.mailing} — {self.get_status_display()} — {self.attempt_time}"

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылок"
        ordering = ["attempt_time"]
