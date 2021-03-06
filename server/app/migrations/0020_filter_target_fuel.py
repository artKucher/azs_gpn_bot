# Generated by Django 3.0.8 on 2020-07-19 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20200719_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='target_fuel',
            field=models.TextField(choices=[('diesel', 'ДТ'), ('gdiesel', 'G-ДТ'), ('gdiesel-opti', 'ДТ Опти'), ('petrol92', '92'), ('gpetrol92', 'G-92'), ('petrol92-opti', '92 Опти'), ('petrol95', '95'), ('gpetrol95', 'G-95'), ('petrol95-opti', '95 Опти'), ('petrol98', '98'), ('gpetrol100', 'G-100'), ('gas', 'ГАЗ')], default='petrol92', max_length=15),
        ),
    ]
