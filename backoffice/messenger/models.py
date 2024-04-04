from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from passlib.context import CryptContext

# from system.models import Customer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Chat(models.Model):
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Клиент")

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

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.sender}. {self.created_at.strftime("%Y-%m-%d %H:%M")}'
