from django.contrib.auth import views as auth_views
from django.urls import path

from users.apps import UsersConfig
from users.views import (
    ActivateUserView,
    CustomLoginView,
    CustomLogoutView,
    MailingToggleEnabledView,
    ManagerDashboardView,
    ProfileUpdateView,
    RegisterDoneView,
    RegisterView,
    UserDashboardView,
    UserDetailView,
    UserListView,
    UserToggleActiveView,
)

app_name = UsersConfig.name

urlpatterns = [
    # =========================================================================
    # AUTH
    # =========================================================================
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("register/done/", RegisterDoneView.as_view(), name="register_done"),
    path("activate/<uidb64>/<token>/", ActivateUserView.as_view(), name="activate"),
    # =========================================================================
    # PASSWORD RESET (built-in)
    # =========================================================================
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset_form.html",
            email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
            success_url="done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url="/users/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # =========================================================================
    # PROFILE / LK
    # =========================================================================
    path("profile/", UserDetailView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("lk/", UserDashboardView.as_view(), name="lk"),
    # =========================================================================
    # MANAGERS
    # =========================================================================
    path("manage/", ManagerDashboardView.as_view(), name="manager_dashboard"),
    path("manage/users/<int:pk>/toggle-active/", UserToggleActiveView.as_view(), name="user_toggle_active"),
    path(
        "manage/mailings/<int:pk>/toggle-enabled/", MailingToggleEnabledView.as_view(), name="mailing_toggle_enabled"
    ),
]
