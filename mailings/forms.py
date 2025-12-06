from django import forms

from mailings.models import Recipient, Message, Mailing, MailingAttempt
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


class RecipientForm(StyleFormMixin, forms.ModelForm):
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
        self.user: CustomUser | None = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"placeholder": "email"})
        self.fields["full_name"].widget.attrs.update({"placeholder": "Фамилия Имя Отчество"})
        self.fields["comment"].widget.attrs.update({"placeholder": "Комментарий"})

    def save(self, commit: bool = True) -> Recipient:
        """
        Сохраняет получателя, подставляя owner из self.user, если он передан.
        """
        recipient: Recipient = super().save(commit=False)

        if self.user is not None:
            recipient.owner = self.user

        if commit:
            recipient.save()
            self.save_m2m()

        return recipient
