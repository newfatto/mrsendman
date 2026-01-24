from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from mailings.models import Mailing, MailingAttempt, Recipient


@dataclass(frozen=True)
class MailingSendResult:
    """
    Результат отправки рассылки.
    """
    total: int
    success: int
    failed: int
    error: Optional[str] = None


def send_mailing(mailing: Mailing) -> MailingSendResult:
    """
    Отправляет письма всем получателям рассылки.

    Правила:
    - Отправка разрешена только если текущее время в окне start_time..end_time (включительно).
    - На каждого получателя создаётся MailingAttempt со статусом success/failed.
    - server_response хранит 'OK' или текст ошибки.

    Args:
        mailing: объект рассылки.

    Returns:
        MailingSendResult: сводка по отправке.
    """
    now = timezone.now()

    mailing.update_status()

    if not (mailing.start_time <= now <= mailing.end_time):
        return MailingSendResult(
            total=0,
            success=0,
            failed=0,
            error="Рассылка не может быть запущена сейчас: текущее время вне окна отправки.",
        )

    recipients = list(mailing.recipients.all())
    total = len(recipients)

    success_count = 0
    failed_count = 0

    subject = mailing.message.subject
    body = mailing.message.content
    from_email = getattr(settings, "EMAIL_HOST_USER", None) or "no-reply@example.com"

    for recipient in recipients:
        try:
            # send_mail возвращает количество успешно отправленных сообщений (обычно 1)
            sent = send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            if sent == 1:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status="success",
                    server_response="OK",
                )
                success_count += 1
            else:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    recipient=recipient,
                    status="failed",
                    server_response="Письмо не было отправлено (send_mail вернул 0).",
                )
                failed_count += 1

        except Exception as exc:  # noqa: BLE001
            MailingAttempt.objects.create(
                mailing=mailing,
                recipient=recipient,
                status="failed",
                server_response=str(exc),
            )
            failed_count += 1

    return MailingSendResult(
        total=total,
        success=success_count,
        failed=failed_count,
        error=None,
    )