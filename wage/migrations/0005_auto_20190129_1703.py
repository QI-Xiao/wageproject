# Generated by Django 2.1.5 on 2019-01-29 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wage', '0004_employee_calculate_finished'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='superior_income_rate',
            field=models.FloatField(),
        ),
    ]
