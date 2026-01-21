from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from mailings.forms import MailingForm, MessageForm, RecipientForm
from mailings.models import Mailing, Message, Recipient

# =============================================================================
# MIXINS
# =============================================================================


class OwnerQuerySetMixin(LoginRequiredMixin):
    """
    Миксин проверяет, является ли пользователь владельцем экземпляра модели,
    при попытке её просмотра, изменения и удаления.
    Название поля в полях модели должно быть "owner",
    но может быть переопределено.
    """

    owner_field_name = "owner"

    def get_queryset(self) -> Any:
        qs = super().get_queryset()
        return qs.filter(**{self.owner_field_name: self.request.user})


# =============================================================================
# INDEX / PUBLIC PAGES
# =============================================================================


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Добавляет в контекст информацию об общем количестве получателей, писем и рассылок на сервисе.
        """
        context: dict[str, Any] = super().get_context_data(**kwargs)

        context["recipients_count"] = Recipient.objects.count()
        context["messages_count"] = Message.objects.count()
        context["mailings_count"] = Mailing.objects.count()

        return context


# =============================================================================
# RECIPIENTS
# =============================================================================


class RecipientListView(OwnerQuerySetMixin, ListView):
    """
    Просмотр списка получателей в личном кабинете пользователя.
    Пользователю доступны только те получатели, которых он добавил сам.
    """

    model = Recipient
    template_name = "recipients/recipients.html"
    context_object_name = "recipients"
    paginate_by = 30

    def get_queryset(self) -> Any:
        return super().get_queryset().order_by("created_at")


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """
    Добавление нового получателя
    """

    model = Recipient
    form_class = RecipientForm
    template_name = "recipients/recipient_create.html"
    context_object_name = "recipient"
    success_url = reverse_lazy("mailings:recipients")

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Передаём в форму текущего пользователя, чтобы она
        могла записать его в поле owner.
        """
        kwargs: dict[str, Any] = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class RecipientDetailView(OwnerQuerySetMixin, DetailView):
    """
    Просмотр информации о получателе.
    """

    model = Recipient
    template_name = "recipients/recipient_detail.html"
    context_object_name = "recipient"


class RecipientUpdateView(OwnerQuerySetMixin, UpdateView):
    """
    Редактирование информации о получателе.
    """

    model = Recipient
    form_class = RecipientForm
    template_name = "recipients/recipient_update.html"
    context_object_name = "recipient"

    def get_success_url(self):
        """
        Переадресация после успешного редактирования на просмотр информации о получаетеле.
        """
        return reverse("mailings:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(OwnerQuerySetMixin, DeleteView):
    """
    Удаление получателя.
    """

    model = Recipient
    template_name = "recipients/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipients")
    context_object_name = "recipient"


# =============================================================================
# MESSAGES
# =============================================================================


class MessageListView(OwnerQuerySetMixin, ListView):
    """
    Просмотр списка писем в личном кабинете пользователя.
    Пользователю доступны только те письма, которые он создал сам.
    """

    model = Message
    template_name = "messages/messages.html"
    context_object_name = "messages"
    paginate_by = 30

    def get_queryset(self) -> Any:
        return super().get_queryset().order_by("created_at")


class MessageCreateView(LoginRequiredMixin, CreateView):
    """
    Добавление нового письма.
    """

    model = Message
    form_class = MessageForm
    template_name = "messages/message_create.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailings:messages")

    def form_valid(self, form):
        """
        Перед сохранением письма указываем владельца.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(OwnerQuerySetMixin, DetailView):
    """
    Просмотр информации о письме.
    """

    model = Message
    template_name = "messages/message_detail.html"
    context_object_name = "message"


class MessageUpdateView(OwnerQuerySetMixin, UpdateView):
    """
    Редактирование письма.
    """

    model = Message
    form_class = MessageForm
    template_name = "messages/message_update.html"
    context_object_name = "message"

    def get_success_url(self):
        """
        Переадресация после успешного редактирования на просмотр деталей письма
        """
        return reverse("mailings:message_detail", args=[self.kwargs.get("pk")])


class MessageDeleteView(OwnerQuerySetMixin, DeleteView):
    """
    Удаление письма.
    """

    model = Message
    template_name = "messages/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:messages")
    context_object_name = "message"


# =============================================================================
# MAILINGS
# =============================================================================


class MailingListView(OwnerQuerySetMixin, ListView):
    """
    Просмотр списка рассылок в личном кабинете пользователя.
    Пользователю доступны только те рассылки, которые он создал сам.
    """

    model = Mailing
    template_name = "mailings/mailings.html"
    context_object_name = "mailings"

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Обновление статуса всех рассылок пользователя.
        Группирование по статусу и добавление их в контектст.
        """
        context = super().get_context_data(**kwargs)

        mailings = list(context["mailings"])

        for mailing in mailings:
            mailing.update_status()

        context["running"] = [m for m in mailings if m.status == Mailing.STATUS_RUNNING]
        context["created"] = [m for m in mailings if m.status == Mailing.STATUS_CREATED]
        context["finished"] = [m for m in mailings if m.status == Mailing.STATUS_FINISHED]

        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """
    Создание новой рассылки.
    """

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_create.html"
    context_object_name = "mailing"
    success_url = reverse_lazy("mailings:mailings")

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Подставляет текущего пользователя в форму, чтобы она могла
        ограничить выбор получателей и писем;
        автоматически установить владельца рассылки.
        """

        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDetailView(OwnerQuerySetMixin, DetailView):
    """
    Просмотр информации о рассылке.
    """

    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        """
        Обновляем статус рассылки при просмотре
        """
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingUpdateView(OwnerQuerySetMixin, UpdateView):
    """
    Редактирование рассылки.
    """

    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_update.html"
    context_object_name = "mailing"

    def get_success_url(self):
        return reverse("mailings:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(OwnerQuerySetMixin, DeleteView):
    """
    Удаление расссылки.
    """

    model = Mailing
    template_name = "mailings/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:mailings")
    context_object_name = "mailing"
