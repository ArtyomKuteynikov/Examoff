# Generated by Django 4.2.5 on 2024-05-06 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_customer_transactions_subscriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='audio',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
