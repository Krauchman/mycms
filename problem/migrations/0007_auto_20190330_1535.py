# Generated by Django 2.1.4 on 2019-03-30 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0006_auto_20190330_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='polygon_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='problem.PolygonAccount'),
        ),
    ]