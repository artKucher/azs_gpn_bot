from django.db import models

# Create your models here.
class User(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя социальной сети',
        unique=True,
    )
    username = models.TextField(
        verbose_name='Юзернейм',
    )

    def __str__(self):
        return f'{self.external_id} {self.username}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
