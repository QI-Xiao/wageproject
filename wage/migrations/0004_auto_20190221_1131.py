# Generated by Django 2.1.5 on 2019-02-21 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wage', '0003_auto_20190220_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='change_date',
        ),
        migrations.AddField(
            model_name='order',
            name='chargeback_date',
            field=models.DateField(blank=True, null=True, verbose_name='退单时间'),
        ),
        migrations.AddField(
            model_name='order',
            name='orderfinish_date',
            field=models.DateField(blank=True, null=True, verbose_name='订单完成时间'),
        ),
    ]
