# Generated by Django 3.0.8 on 2020-07-19 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20200718_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active_filter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_filter_rel', to='app.Filter'),
        ),
    ]