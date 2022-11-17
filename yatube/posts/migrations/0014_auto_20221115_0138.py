# Generated by Django 2.2.16 on 2022-11-14 20:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0013_auto_20221115_0127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='follow',
            name='author',
        ),
        migrations.AddField(
            model_name='follow',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='follow',
            name='user',
        ),
        migrations.AddField(
            model_name='follow',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
            preserve_default=False,
        ),
    ]