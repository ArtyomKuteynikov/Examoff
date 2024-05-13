# Generated by Django 4.2.5 on 2024-05-12 22:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0014_rename_audio_customer_audio_file'),
        ('messenger', '0009_file_chat'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(0, 'INIT'), (1, 'FILE_LOADED'), (2, 'WITHOUT_FILE'), (3, 'FINISHED')], default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer')),
            ],
            options={
                'db_table': 'audio_chat',
            },
        ),
        migrations.CreateModel(
            name='AudioMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.IntegerField(choices=[(0, 'Преподаватель'), (1, 'ChatGPT')], verbose_name='Отправитель')),
                ('text', models.TextField(verbose_name='Текст сообщения')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger.chat', verbose_name='Чат')),
            ],
            options={
                'db_table': 'audio_message',
            },
        ),
        migrations.CreateModel(
            name='AudioChatFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.CharField(max_length=256)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger.audiochat', verbose_name='Чат')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.customer')),
            ],
            options={
                'db_table': 'audio_chat_files',
            },
        ),
    ]
