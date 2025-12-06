from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import CustomUser


class StyleFormMixin:
    """
    Миксин автоматически добавляет Bootstrap-класс 'form-control'
    ко всем полям формы.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing_classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing_classes} form-control".strip()


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    """
    Форма регистрации пользователя.
    """

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2", "first_name", "last_name", "avatar")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["email"].label = "Ваш email"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["first_name"].label = "Имя"
        self.fields["last_name"].label = "Фамилия"
        self.fields["avatar"].label = "Аватар"

        self.fields["email"].widget.attrs["placeholder"] = "Введите email"
        self.fields["password1"].widget.attrs["placeholder"] = "Введите пароль"
        self.fields["password2"].widget.attrs["placeholder"] = "Подтвердите пароль"
        self.fields["first_name"].widget.attrs["placeholder"] = "Введите имя"
        self.fields["last_name"].widget.attrs["placeholder"] = "Введите фамилию"
        self.fields["avatar"].widget.attrs["placeholder"] = "Загрузите аватар"


class CustomUserAuthenticationForm(StyleFormMixin, AuthenticationForm):
    """
    Форма входа по email вместо username.
    """

    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    class Meta:
        model = CustomUser
        fields = ("username", "password")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Ваш email"
        self.fields["password"].label = "Пароль"

        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Введите email"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Введите пароль"})


class UserUpdateForm(StyleFormMixin, forms.ModelForm):
    """
    Форма обновления информации о пользователе.
    """

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "avatar")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["email"].label = "Ваш email"
        self.fields["first_name"].label = "Имя"
        self.fields["last_name"].label = "Фамилия"
        self.fields["avatar"].label = "Аватар"

        self.fields["email"].widget.attrs["placeholder"] = "Введите email"
        self.fields["first_name"].widget.attrs["placeholder"] = "Введите имя"
        self.fields["last_name"].widget.attrs["placeholder"] = "Введите фамилию"
        self.fields["avatar"].widget.attrs["placeholder"] = "Загрузите аватар"
