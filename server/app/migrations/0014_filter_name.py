# Generated by Django 3.0.8 on 2020-07-18 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20200717_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]
