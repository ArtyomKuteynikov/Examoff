from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from passlib.context import CryptContext

from system.models import Customer

# from system.models import Customer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Chat(models.Model):
    user_owner = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Клиент")
    chat_state = models.CharField(max_length=100, null=True, blank=True)

    DIPLOMA_CHAT_TYPE = 'DIPLOMA_CHAT_TYPE'
    CHAT_TYPES = [
        (DIPLOMA_CHAT_TYPE, 'DIPLOMA_CHAT_TYPE'),
    ]

    chat_type = models.CharField(
        max_length=50,
        choices=CHAT_TYPES,
        default=DIPLOMA_CHAT_TYPE,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'Чат {self.id}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Чат")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель")
    text = models.TextField(verbose_name="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True)
    response_specific_state = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.sender}. {self.created_at.strftime("%Y-%m-%d %H:%M")}'
