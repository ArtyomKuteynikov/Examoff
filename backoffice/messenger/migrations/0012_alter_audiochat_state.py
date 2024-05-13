# Generated by Django 4.2.5 on 2024-05-12 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0011_alter_audiomessage_chat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audiochat',
            name='state',
            field=models.IntegerField(choices=[(0, 'INIT'), (1, 'FILE_LOADED'), (2, 'WITHOUT_FILE'), (3, 'STARTED'), (4, 'PAUSED'), (5, 'FINISHED')], default=0),
        ),
    ]