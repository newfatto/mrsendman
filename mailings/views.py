from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from mypy.dmypy.client import request

from mailings.models import Recipient, Message, Mailing
from mailings.forms import RecipientForm


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Добавляет в контекст информацию об общем количестве получателей, писем и рассылок на сервисе.
        """
        context: dict[str, Any] = super().get_context_data(**kwargs)

        context['recipients_count'] = Recipient.objects.count()
        context['messages_count'] = Message.objects.count()
        context['mailings_count'] = Mailing.objects.count()

        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """
    Добавление нового получателя
    """
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipients/recipient_create.html'
    context_object_name = 'recipient'
    success_url =  reverse_lazy('mailings:recipient_list')

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Передаём в форму текущего пользователя, чтобы она
        могла записать его в поле owner.
        """

        kwargs: dict[str, Any] = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


