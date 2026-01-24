from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from mailings.models import Mailing, MailingAttempt, Message, Recipient
from users.forms import CustomUserAuthenticationForm, CustomUserCreationForm, UserUpdateForm
from users.models import CustomUser


class RegisterView(CreateView):
    """
    Контроллер для регистрации нового пользователя
    с подтверждением по email.
    - создаёт пользователя с is_active=False
    - отправляем письмо со ссылкой активации
    - показываем страницу 'проверьте почту'
    """

    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("users:register_done")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:

        user: CustomUser = form.save(commit=False)
        user.is_active = False
        user.save()

        self._send_activation_email(request=self.request, user=user)

        return redirect(self.success_url)

    def _send_activation_email(self, request: HttpRequest, user: CustomUser) -> None:
        """
        Отправляет письмо со ссылкой активации аккаунта.
        """
        uidb64: str = urlsafe_base64_encode(force_bytes(user.pk))
        token: str = default_token_generator.make_token(user)

        activation_url: str = request.build_absolute_uri(
            reverse("users:activate", kwargs={"uidb64": uidb64, "token": token})
        )

        subject: str = "Подтверждение регистрации в Mr SendMan"
        message: str = render_to_string(
            "activation_email.html",
            {"user": user, "activation_url": activation_url},
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class RegisterDoneView(TemplateView):
    """
    Страница после регистрации: 'проверьте почту и подтвердите email'.
    """

    template_name = "activation_done.html"


class ActivateUserView(View):
    """
    Активация пользователя по ссылке из письма.
    """

    def get(self, request: HttpRequest, uidb64: str, token: str, *args: object, **kwargs: object) -> HttpResponse:
        try:
            uid: str = urlsafe_base64_decode(uidb64).decode()
            user: CustomUser = CustomUser.objects.get(pk=uid)
        except (ValueError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=["is_active"])
            messages.success(request, "Email подтверждён. Теперь вы можете войти.")
            return redirect("users:login")

        messages.error(request, "Ссылка активации недействительна или устарела.")
        return redirect("users:register")


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
