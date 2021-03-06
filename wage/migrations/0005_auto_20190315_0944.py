# Generated by Django 2.1.5 on 2019-03-15 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wage', '0004_remove_order_is_discount_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='origin_status',
            field=models.IntegerField(choices=[(0, '不处理'), (1, '已付定金'), (2, '已付尾款'), (3, '已完成'), (4, '已退款')], default=0, verbose_name='退单前订单状态'),
        ),
        migrations.AlterField(
            model_name='order',
            name='task_and_changepeople',
            field=models.BooleanField(default=False, verbose_name='更换人且为任务单'),
        ),
    ]
