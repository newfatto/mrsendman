from typing import Any

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from mailings.models import Mailing, MailingAttempt, Message, Recipient
from users.forms import CustomUserAuthenticationForm, CustomUserCreationForm, UserUpdateForm
from users.models import CustomUser


class RegisterView(CreateView):
    """Контроллер для регистрации нового пользователя.
    Создаёт пользователя, логинит, отправляет welcome-письмо.
    """

    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("users:lk")

    def form_valid(self, form):
        """
        Вызывается при валидной форме.
        Сохраняет пользователя, логинит его и отправляет письмо.
        """
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)
        self.send_welcome_email(user.email)
        return response

    def send_welcome_email(self, user_email):
        """
        Отправляет приветственное письмо новому пользователю.
        """
        subject = "Добро пожаловать в Mr SandMan"
        message = (
            "Ура! Ты зарегистрирован на сайте. Теперь тебе доступно то, что доступно зарегистрированным пользователям"
        )
        recipient_list = [
            user_email,
        ]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


class CustomLoginView(LoginView):
    """Контроллер авторизации пользователя."""

    form_class = CustomUserAuthenticationForm
    template_name = "login.html"
    next_page = reverse_lazy("users:lk")


class CustomLogoutView(LogoutView):
    """Контроллер выхода пользователя из системы."""

    next_page = reverse_lazy("mailings:index")


class UserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "edit.html"
    success_url = reverse_lazy("users:lk")

    def get_object(self, queryset=None):
        """Возвращает текущего пользователя (запрещает редактирование чужих профилей)."""
        return get_object_or_404(CustomUser, pk=self.request.user.pk)

    def get_success_url(self):
        """Динамически формирует URL для перенаправления после успешного сохранения."""
        return reverse_lazy("users:lk")

    def form_valid(self, form):
        """Дополнительная логика при валидном формировании (опционально)."""
        response = super().form_valid(form)
        # Здесь можно добавить сообщения об успехе, логирование и т.п.
        return response


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    Представление личного кабинета пользователя.
    Отображает краткую информацию об активности:
    количество получателей, писем и рассылок.
    """

    template_name = "lk.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        user = self.request.user

        context["recipients_count"] = Recipient.objects.filter(owner=user).count()
        context["messages_count"] = Message.objects.filter(owner=user).count()
        context["mailings_count"] = Mailing.objects.filter(owner=user).count()

        return context
