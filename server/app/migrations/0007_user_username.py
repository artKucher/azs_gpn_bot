# Generated by Django 3.0.8 on 2020-07-12 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.TextField(blank=True, verbose_name='Юзернейм'),
        ),
    ]
