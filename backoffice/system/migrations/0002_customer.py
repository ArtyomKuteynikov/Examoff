# Generated by Django 4.2.5 on 2024-03-20 16:58

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(max_length=32, verbose_name='Телефон')),
                ('name', models.CharField(max_length=64, verbose_name='Имя')),
                ('surname', models.CharField(max_length=64, verbose_name='Фамилия')),
                ('confirmed', models.BooleanField(default=False)),
                ('show', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True, verbose_name='Статус активности')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
                'db_table': 'customer',
                'ordering': ('id',),
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
