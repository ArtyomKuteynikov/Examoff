import datetime
import uuid

from ckeditor.fields import RichTextField
from django.db import models
from django.db.models import Sum, F, Q
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from passlib.context import CryptContext

from .utils import send_email, HOST

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Settings(models.Model):
    max_refers = models.IntegerField(default=10, verbose_name="Максимальное количество приглашений с одного аккаунта")
    referer_tokens = models.IntegerField(default=5000, verbose_name="Максимальное количество токенов за приглашение")
    subscription_price = models.FloatField(default=559, verbose_name="Стоимость подписки")
    token_price = models.FloatField(default=0.01, verbose_name="Cтоимость одного токена")
    tokens_in_subscription = models.IntegerField(default=100000, verbose_name="Токенов в подписке")
    text = RichTextField(verbose_name="Текст подписки")

    class Meta:
        ordering = ('id',)
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return 'Настройки системы'


class Customer(User):
    phone = models.CharField(max_length=32, verbose_name="Телефон", blank=True, null=True)
    name = models.CharField(max_length=64, verbose_name="Имя", blank=True, null=True)
    surname = models.CharField(max_length=64, verbose_name="Фамилия", blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    tokens = models.IntegerField(default=0)
    invite_code = models.CharField(default=uuid.uuid4)
    referer = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    auto_payments = models.BooleanField(default=False)
    show = models.BooleanField(default=True)
    active = models.BooleanField(default=True, verbose_name="Статус активности")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Время")

    def set_password_hash(self, password):
        self.password = pwd_context.hash(password)
        return

    def confirm_email(self):
            token = uuid.uuid4()
            cache.set(f"email:confirm:{token}", self.email, timeout=432000)
            message = f'''Здравствуйте, {self.name}!
Добро пожаловать в EXEMOFF!
Подтвердите аккаунт перейдя по ссылке: {HOST}/confirm/{token}

С уважением,
Examoff'''
            send_email(self.email, 'Подтверждение аккаунта', message)
            return

    def reset_password_hash(self):
            token = uuid.uuid4()
            cache.set(f"email:reset:{token}", self.email, timeout=86400)
            message = f'''Здравствуйте, {self.name}!
Для сброса пароля перейдите по ссылке: {HOST}/reset/{token}

С уважением,
Examoff'''
            send_email(self.email, 'Сброс пароля', message)
            return

    def verify_password(self, plain_password):
        print(plain_password, self.password)
        return pwd_context.verify(plain_password, self.password)

    def referrings(self):
        return Settings.objects.first().max_refers - len(Customer.objects.filter(referer=self).all())

    def referral_link(self):
        return f'{HOST}/referral/{self.invite_code}'

    def subscription(self):
        if self.subscriptions_set.filter(end__gte=datetime.datetime.now()).first():
            return self.subscriptions_set.filter(end__gte=datetime.datetime.now()).order_by('-end').first().end
        return None

    def settings(self):
        return Settings.objects.first()

    class Meta:
        db_table = "customer"
        ordering = ('id',)
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.name} {self.surname}'


class Subscriptions(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start = models.DateField(verbose_name="Дата начала")
    end = models.DateField(verbose_name="Окончания")

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return 'Подписки'


class Transactions(models.Model):
    TYPES = [
        (0, 'Оплата подписки'),
        (1, 'Покупка токенов'),
        (2, 'Оплата подписки и токенов'),
    ]

    METHODS = [
        (0, 'Оплата картой(ЮКасса)'),
        (1, 'Оплата токенами TON'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Клиент")
    amount = models.FloatField(default=0, verbose_name="Сумма")
    type = models.IntegerField(choices=TYPES, default=0, verbose_name="Тип транзакции")
    method = models.IntegerField(choices=METHODS, default=0, verbose_name="Метод оплаты")
    tokens = models.IntegerField(default=0, verbose_name="Количество токенов")
    paid = models.BooleanField(default=False, verbose_name="Оплачено")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Время")

    class Meta:
        ordering = ('id',)
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'Транзакция #{self.id}'
