# Generated by Django 2.1.5 on 2019-01-30 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wage', '0008_auto_20190130_1554'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlymoney',
            name='remaining_task',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
    ]