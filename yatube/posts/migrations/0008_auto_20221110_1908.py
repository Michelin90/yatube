# Generated by Django 2.2.16 on 2022-11-10 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20221110_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
    ]