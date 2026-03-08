from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "comment", "owner")
    list_filter = ("owner",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "owner",
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "owner", "message")
    list_filter = (
        "owner",
        "message",
    )


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("attempt_time", "status", "server_response", "mailing", "recipient")
    list_filter = ("status", "attempt_time", "recipient")
