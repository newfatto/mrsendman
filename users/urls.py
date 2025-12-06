from django.urls import path

from users.apps import UsersConfig
from users.views import (
    CustomLoginView,
    CustomLogoutView,
    ProfileUpdateView,
    RegisterView,
    UserDashboardView,
    UserDetailView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", UserDetailView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("lk/", UserDashboardView.as_view(), name="lk"),
]
