from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Q, QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache


from mailings.forms import MailingForm, MessageForm, RecipientForm
from mailings.models import Mailing, MailingAttempt, Message, Recipient
from mailings.services import send_mailing

# =============================================================================
# MIXINS
# =============================================================================


class OwnerQuerySetMixin:
    """
    Миксин для ограничения queryset по владельцу.
    - Обычный пользователь видит только свои объекты.
    - Менеджер (по праву users.change_customuser) может просматривать все объекты.
    """

    owner_field_name: str = "owner"

    def get_queryset(self) -> QuerySet[Any]:
        qs: QuerySet[Any] = super().get_queryset()

        user: AbstractUser = self.request.user

        if user.is_authenticated and user.has_perm("users.change_customuser"):
            return qs

        return qs.filter(**{self.owner_field_name: user})


# =============================================================================
# INDEX / PUBLIC PAGES
# =============================================================================

@method_decorator(cache_page(60 * 15), name='dispatch')
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
        context["mailings_running"] = Mailing.objects.filter(status=Mailing.STATUS_RUNNING).count()

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

    def get_queryset(self) -> Any:
        """
        Обновление статуса всех рассылок пользователя.
        Группировка по статусу.
        """
        qs = super().get_queryset().order_by("start_time")

        mailings = list(qs)

        for mailing in mailings:
            mailing.update_status()

        status = self.request.GET.get("status")
        if status in {Mailing.STATUS_CREATED, Mailing.STATUS_RUNNING, Mailing.STATUS_FINISHED}:
            mailings = [m for m in mailings if m.status == status]

        return mailings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_status"] = self.request.GET.get("status", "all")
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

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """
        Проставляет владельца рассылки перед сохранением.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)


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


class MailingStatsView(LoginRequiredMixin, TemplateView):
    """
    Статистика по рассылкам текущего пользователя:
    - успешные/неуспешные попытки
    - общее число попыток
    - количество отправленных сообщений (как число успешных отправок)
    - статистика по каждой рассылке
    """

    template_name = "mailings/stats.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)

        attempts_qs = MailingAttempt.objects.filter(mailing__owner=self.request.user)

        total_attempts: int = attempts_qs.count()
        success_attempts: int = attempts_qs.filter(status="success").count()
        failed_attempts: int = attempts_qs.filter(status="failed").count()

        sent_messages_count: int = success_attempts

        mailings_qs = (
            Mailing.objects.filter(owner=self.request.user)
            .annotate(
                attempts_total=Count("attempts", distinct=True),
                attempts_success=Count("attempts", filter=Q(attempts__status="success"), distinct=True),
                attempts_failed=Count("attempts", filter=Q(attempts__status="failed"), distinct=True),
            )
            .order_by("-start_time")
        )

        context["total_attempts"] = total_attempts
        context["success_attempts"] = success_attempts
        context["failed_attempts"] = failed_attempts
        context["sent_messages_count"] = sent_messages_count
        context["mailings_stats"] = mailings_qs

        return context


# =============================================================================
# MAILING_SEND
# =============================================================================


class MailingSendView(OwnerQuerySetMixin, SingleObjectMixin, View):
    """
    Ручной запуск рассылки пользователем через интерфейс.
    Доступен только владельцу рассылки.
    """

    model = Mailing

    def post(self, request: HttpRequest, pk: int, *args: object, **kwargs: object) -> HttpResponse:
        mailing = self.get_queryset().get(pk=pk)

        result = send_mailing(mailing)

        if result.error:
            messages.error(request, result.error)
        else:
            messages.success(
                request,
                f"Отправка завершена. Всего: {result.total}, успешно: {result.success}, ошибок: {result.failed}.",
            )

        return redirect("mailings:mailing_detail", pk=pk)
