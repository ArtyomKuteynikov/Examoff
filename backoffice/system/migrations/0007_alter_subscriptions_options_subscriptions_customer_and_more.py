# Generated by Django 4.2.5 on 2024-03-21 16:48

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_settings_referer_tokens_settings_subscription_price_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'ordering': ('id',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='customer',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='system.customer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='end',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='start',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('type', models.IntegerField(choices=[(0, 'Оплата подписки'), (1, 'Оплата токенов'), (2, 'Оплата подписки и токенов')], default=0)),
                ('method', models.IntegerField(choices=[(0, 'Оплата картой(ЮКасса)'), (1, 'Оплата токенами TON')], default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer')),
            ],
            options={
                'verbose_name': 'Транзакция',
                'verbose_name_plural': 'Транзакции',
                'ordering': ('id',),
            },
        ),
    ]
