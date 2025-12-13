from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from mailings.forms import MessageForm, RecipientForm
from mailings.models import Mailing, Message, Recipient
from users.models import CustomUser


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


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр информации о получателе.
    """

    model = Recipient
    template_name = "recipients/recipient_detail.html"
    context_object_name = "recipient"


class RecipientListView(ListView):
    """
    Просмотр списка получателей в личном кабинете пользователя.
    Пользователю доступны только те получатели, которых он добавил сам.
    """

    model = Recipient
    template_name = "recipients/recipients.html"
    context_object_name = "recipients"
    paginate_by = 30

    def get_queryset(self) -> Any:
        return Recipient.objects.filter(owner=self.request.user).order_by("created_at")


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование информации о получателе.
    """

    model = Recipient
    form_class = RecipientForm
    template_name = "recipients/recipient_update.html"
    context_object_name = "recipient"

    def get_success_url(self):
        return reverse("mailings:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "recipients/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:recipients")
    context_object_name = "recipient"


class MessageCreateView(LoginRequiredMixin, CreateView):
    """
    Добавление нового письма
    """

    model = Message
    form_class = MessageForm
    template_name = "messages/message_create.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailings:messages")

    def form_valid(self, form):
        """
        Перед сохранением письма проставляем владельца.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр информации о получателе.
    """

    model = Message
    template_name = "messages/message_detail.html"
    context_object_name = "message"


class MessageListView(ListView):
    """
    Просмотр списка получателей в личном кабинете пользователя.
    Пользователю доступны только те получатели, которых он добавил сам.
    """

    model = Message
    template_name = "messages/messages.html"
    context_object_name = "messages"
    paginate_by = 30

    def get_queryset(self) -> Any:
        return Message.objects.filter(owner=self.request.user).order_by("created_at")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование информации о получателе.
    """

    model = Message
    form_class = MessageForm
    template_name = "messages/message_update.html"
    context_object_name = "message"

    def get_success_url(self):
        return reverse("mailings:message_detail", args=[self.kwargs.get("pk")])


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "messages/message_confirm_delete.html"
    success_url = reverse_lazy("mailings:messages")
    context_object_name = "message"
