# Generated by Django 3.0.8 on 2020-07-12 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.TextField(default='123', verbose_name='Юзернейм'),
        ),
    ]