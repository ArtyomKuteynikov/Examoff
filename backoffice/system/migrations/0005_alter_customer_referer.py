# Generated by Django 4.2.5 on 2024-03-21 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_subscriptions_customer_referer_settings_max_refers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='referer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='system.customer'),
        ),
    ]
