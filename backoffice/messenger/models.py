from ckeditor.fields import RichTextField
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
