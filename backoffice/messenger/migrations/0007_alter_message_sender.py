# Generated by Django 4.2.5 on 2024-04-25 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_customer_transactions_subscriptions'),
        ('messenger', '0006_chat_user_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer', verbose_name='Отправитель'),
        ),
    ]