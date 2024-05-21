# Generated by Django 4.2.5 on 2024-05-12 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0014_rename_audio_customer_audio_file'),
        ('messenger', '0009_file_chat'),
    ]

    operations = [
        migrations.CreateModel(
            name='HelpChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(0, 'INIT'), (1, 'FILE_LOADED'), (2, 'PAUSED'), (3, 'FINISHED')], default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer')),
            ],
            options={
                'db_table': 'help_chat',
            },
        ),
    ]
