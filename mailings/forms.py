from typing import Any

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from mailings.models import Mailing, MailingAttempt, Message, Recipient
from users.models import CustomUser


class StyleFormMixin:
    """
    Миксин автоматически добавляет Bootstrap-класс 'form-control'
    ко всем полям формы, кроме чекбоксов.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing_classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing_classes} form-control".strip()


class OwnerFormMixin:
    """
    Миксин для ModelForm, который:
    - принимает параметр user при инициализации,
    - при сохранении подставляет этого пользователя в поле owner модели.
    """

    user: CustomUser | None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit: bool = True):
        """
        Сохраняет объект, подставляя owner из self.user, если:
        - self.user передан,
        - у объекта есть атрибут owner.
        """
        obj = super().save(commit=False)

        if self.user is not None and hasattr(obj, "owner"):
            obj.owner = self.user

        if commit:
            obj.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()

        return obj


class RecipientForm(OwnerFormMixin, StyleFormMixin, forms.ModelForm):
    """
    Форма создания/редактирования получателя рассылки.
    Владелец (owner) подставляется из текущего пользователя.
    """

    class Meta:
        model = Recipient
        fields = ("email", "full_name", "comment")
        labels = {
            "email": "Email",
            "full_name": "Полное имя",
            "comment": "Комментарий",
        }
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        """

        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update({"placeholder": "email"})
        self.fields["full_name"].widget.attrs.update({"placeholder": "Фамилия Имя Отчество"})
        self.fields["comment"].widget.attrs.update({"placeholder": "Комментарий"})


class MessageForm(StyleFormMixin, forms.ModelForm):
    """
    Форма создания/редактирования письма.
    Владелец (owner) подставляется из текущего пользователя.
    """

    class Meta:
        model = Message
        fields = (
            "subject",
            "content",
        )
        labels = {
            "subject": "Тема письма",
            "content": "Текст письма",
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        """

        super().__init__(*args, **kwargs)

        self.fields["subject"].widget.attrs.update({"placeholder": "введите тему"})
        self.fields["content"].widget.attrs.update({"placeholder": "текст письма"})


class MailingForm(OwnerFormMixin, StyleFormMixin, forms.ModelForm):
    """
    Форма создания/редактирования рассылки.
    Владелец (owner) подставляется из текущего пользователя.
    """

    class Meta:
        model = Mailing
        fields = ("start_time", "end_time", "message", "recipients")
        labels = {
            "start_time": "Время старта рассылки",
            "end_time": "Время окончания рассылки",
            "message": "Письмо",
            "recipients": "Получатели"
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы.
        """

        super().__init__(*args, **kwargs)

        self.fields["start_time"].widget.attrs.update({"placeholder": "время старта рассылки"})
        self.fields["end_time"].widget.attrs.update({"placeholder": "время окончания рассылки"})

        if self.user is not None:
            self.fields["message"].queryset = Message.objects.filter(owner=self.user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=self.user)

    def clean(self) -> dict[str, Any]:
        """
        Общая валидация:
        - start_time не может быть в прошлом
        - start_time должен быть раньше end_time
        """

        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        now = timezone.now()

        if start_time and start_time < now:
            self.add_error('start_time', "Время старта не может быть в прошлом")
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', "Время окончания должно быть позже времени старта")

        return cleaned_data
