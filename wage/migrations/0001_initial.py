# Generated by Django 2.1.5 on 2019-03-12 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=20, verbose_name='键')),
                ('val', models.TextField(verbose_name='值')),
            ],
            options={
                'verbose_name': '配置',
                'verbose_name_plural': '配置',
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='店员')),
                ('base_pay', models.FloatField(verbose_name='底薪')),
                ('commission_rate', models.CharField(max_length=100, verbose_name='提点')),
                ('task_quantity', models.IntegerField(verbose_name='任务单量')),
                ('superior_income_rate', models.TextField(verbose_name='徒弟提点')),
                ('shop_manager', models.BooleanField(default=False, verbose_name='店长')),
                ('which_shop', models.CharField(choices=[('A', 'A'), ('B', 'B')], max_length=10, verbose_name='员工所属门店')),
                ('on_job', models.BooleanField(default=True, verbose_name='在职')),
                ('calculate_finished', models.BooleanField(default=False, verbose_name='计算完毕')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='students', to='wage.Employee', verbose_name='师父')),
            ],
            options={
                'verbose_name': '员工',
                'verbose_name_plural': '员工',
            },
        ),
        migrations.CreateModel(
            name='Monthlymoney',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(verbose_name='日期')),
                ('task_finished', models.IntegerField(default=0, verbose_name='已完成任务单')),
                ('base_salary', models.FloatField(default=0, verbose_name='底薪')),
                ('commission_current', models.FloatField(default=0, verbose_name='当月订单提成')),
                ('commission_before', models.FloatField(default=0, verbose_name='以往留存提成')),
                ('commission_passive', models.FloatField(default=0, verbose_name='带徒弟提成')),
                ('commission_shop_manager', models.FloatField(default=0, verbose_name='店长提成')),
                ('commission_minus', models.FloatField(default=0, verbose_name='退单')),
                ('other_salary', models.FloatField(default=0, verbose_name='额外调整')),
                ('total_salary', models.FloatField(default=0, verbose_name='总金额')),
                ('details_task', models.TextField(default='', verbose_name='任务单明细')),
                ('details_new', models.TextField(default='', verbose_name='新增订单明细')),
                ('details_wed', models.TextField(default='', verbose_name='结婚订单明细')),
                ('details_teacher', models.TextField(default='', verbose_name='师父明细')),
                ('details_manager', models.TextField(default='', verbose_name='全店明细')),
                ('details_back', models.TextField(default='', verbose_name='退单明细')),
                ('whose_salary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wage.Employee', verbose_name='店员')),
            ],
            options={
                'verbose_name': '月薪',
                'verbose_name_plural': '月薪',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=100, verbose_name='顾客')),
                ('tel', models.IntegerField(blank=True, null=True, verbose_name='电话')),
                ('money', models.FloatField(verbose_name='金额')),
                ('commission_rate', models.FloatField(default=0, verbose_name='提成')),
                ('type', models.IntegerField(choices=[(1, '单租'), (2, '定制'), (3, '大牌'), (4, '璀璨'), (5, '升级')], verbose_name='订单类型')),
                ('order_time', models.DateField(verbose_name='预定时间')),
                ('wedding_time', models.DateField(verbose_name='婚礼时间')),
                ('is_task_order', models.BooleanField(default=False, verbose_name='任务单')),
                ('is_discount_order', models.BooleanField(default=False, verbose_name='活动单')),
                ('status', models.IntegerField(choices=[(0, '不处理'), (1, '已付定金'), (2, '已付尾款'), (3, '已完成'), (4, '已退款')], verbose_name='订单状态')),
                ('which_shop', models.CharField(choices=[('A', 'A'), ('B', 'B')], max_length=10, verbose_name='订单所属门店')),
                ('order_number', models.CharField(max_length=20, unique=True, verbose_name='订单号')),
                ('calculated', models.BooleanField(default=False, verbose_name='已被计入当月提成')),
                ('chargeback_date', models.DateField(blank=True, null=True, verbose_name='退单时间')),
                ('orderfinish_date', models.DateField(blank=True, null=True, verbose_name='订单完成时间')),
                ('manual_add', models.BooleanField(default=False, verbose_name='手动修改订单')),
                ('whose_new', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='whose_order_new', to='wage.Employee', verbose_name='新订单负责人')),
                ('whose_wed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='whose_order_wed', to='wage.Employee', verbose_name='完成服务负责人')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
            },
        ),
    ]
