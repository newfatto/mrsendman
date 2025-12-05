from django.db import models


class Recipient(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150, verbose_name='Фамилия Имя Отчество')
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Владелец',
                              related_name='recipients')

    def __str__(self):
        return f'{self.full_name} {self.email}'

    class Meta:
        verbose_name = 'получатель'
        verbose_name_plural = 'получатели'
        ordering = ['email']


