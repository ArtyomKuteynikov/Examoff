# Generated by Django 4.2.5 on 2024-04-06 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0004_rename_chat_states_chat_chat_state_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='response_specific_state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
