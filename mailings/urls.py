from django.urls import path

from mailings.apps import MailingsConfig
from mailings.views import (
    IndexView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
)

app_name = MailingsConfig.name

urlpatterns = [
    # =========================================================================
    # INDEX
    # =========================================================================
    path("", IndexView.as_view(), name="index"),

    # =========================================================================
    # RECIPIENTS
    # =========================================================================
    path("recipients/", RecipientListView.as_view(), name="recipients"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipients/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipients/<int:pk>/edit/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipients/<int:pk>/confirm_delete/", RecipientDeleteView.as_view(), name="recipient_confirm_delete"),

    # =========================================================================
    # MESSAGES
    # =========================================================================
    path("messages/", MessageListView.as_view(), name="messages"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message/<int:pk>/edit/", MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/confirm_delete/", MessageDeleteView.as_view(), name="message_confirm_delete"),

    # =========================================================================
    # MAILINGS
    # =========================================================================
    path("mailings/", MailingListView.as_view(), name="mailings"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/<int:pk>/edit/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/confirm_delete/", MailingDeleteView.as_view(), name="mailing_confirm_delete"),
]
