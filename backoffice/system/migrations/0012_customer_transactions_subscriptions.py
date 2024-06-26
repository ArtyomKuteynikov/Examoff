# Generated by Django 4.2.5 on 2024-04-22 19:58

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0011_remove_subscriptions_customer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=64, verbose_name='E-Mail')),
                ('password', models.CharField(max_length=512)),
                ('phone', models.CharField(blank=True, max_length=32, null=True, verbose_name='Телефон')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Имя')),
                ('surname', models.CharField(blank=True, max_length=64, null=True, verbose_name='Фамилия')),
                ('confirmed', models.BooleanField(default=False)),
                ('tokens', models.IntegerField(default=0)),
                ('invite_code', models.CharField(default=uuid.uuid4)),
                ('auto_payments', models.BooleanField(default=False)),
                ('show', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True, verbose_name='Статус активности')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время')),
                ('referer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='system.customer')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
                'db_table': 'system_customer',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0, verbose_name='Сумма')),
                ('type', models.IntegerField(choices=[(0, 'Оплата подписки'), (1, 'Покупка токенов'), (2, 'Оплата подписки и токенов')], default=0, verbose_name='Тип транзакции')),
                ('method', models.IntegerField(choices=[(0, 'Оплата картой(ЮКасса)'), (1, 'Оплата токенами TON')], default=0, verbose_name='Метод оплаты')),
                ('tokens', models.IntegerField(default=0, verbose_name='Количество токенов')),
                ('paid', models.BooleanField(default=False, verbose_name='Оплачено')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Время')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer', verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Транзакция',
                'verbose_name_plural': 'Транзакции',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='Дата начала')),
                ('end', models.DateField(verbose_name='Окончания')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'ordering': ('id',),
            },
        ),
    ]
