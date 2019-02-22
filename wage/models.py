from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=100, verbose_name='店员')
    base_pay = models.FloatField(verbose_name='底薪')
    commission_rate = models.CharField(max_length=100, verbose_name='提点') # 五种类型，逗号分隔 ex：0.1,0.15,0.2,0.25,0.3
    task_quantity = models.IntegerField(verbose_name='任务单量')
    superior_income_rate = models.TextField(verbose_name='徒弟提点') # 徒弟的，金额:提点, ex: 0:0.05,1000:0.1,2500:0.2
    teacher = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='students', verbose_name='师父')
    shop_manager = models.BooleanField(default=False, verbose_name='店长')
    on_job = models.BooleanField(default=True, verbose_name='在职')
    calculate_finished = models.BooleanField(default=False, verbose_name='计算完毕')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = '员工'


class Order(models.Model):
    ORDER_TYPE = (
        (1, '单租'),
        (2, '定制'),
        (3, '大牌'),
        (4, '璀璨'),
        (5, '升级'),
    )
    ORDER_STATUS = (
        (0, '不处理'),
        (1, '已付定金'),
        (2, '已付尾款'),
        (3, '已完成'),
        (4, '已退款'),
    )
    client_name = models.CharField(max_length=100, verbose_name='顾客')
    tel = models.IntegerField(null=True, blank=True, verbose_name='电话')
    money = models.FloatField(verbose_name='金额')
    commission_rate = models.FloatField(default=0, verbose_name='提成')
    type = models.IntegerField(choices=ORDER_TYPE, verbose_name='订单类型')
    order_time = models.DateField(verbose_name='预定时间')
    wedding_time = models.DateField(verbose_name='婚礼时间')
    is_task_order = models.BooleanField(default=False, verbose_name='任务单')
    is_discount_order = models.BooleanField(default=False, verbose_name='活动单')
    status = models.IntegerField(choices=ORDER_STATUS, verbose_name='订单状态')
    whose_order = models.ForeignKey('Employee', on_delete=models.CASCADE, verbose_name='店员')
    order_number = models.CharField(max_length=20, unique=True, verbose_name='订单号')
    calculated = models.BooleanField(default=False, verbose_name='已被计入当月提成')
    chargeback_date = models.DateField(verbose_name='退单时间', blank=True, null=True)
    orderfinish_date = models.DateField(verbose_name='订单完成时间', blank=True, null=True)

    def __str__(self):
        return '顾客：%s，订单日期：%s，结婚日期：%s' % (self.client_name, self.order_time, self.wedding_time)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'


class Monthlymoney(models.Model):
    month = models.DateField(verbose_name='日期') # 考虑年份
    whose_salary = models.ForeignKey('Employee',on_delete=models.CASCADE, verbose_name='店员')
    task_finished = models.IntegerField(default=0, verbose_name='已完成任务单')
    base_salary = models.FloatField(default=0, verbose_name='底薪')
    commission_current = models.FloatField(default=0, verbose_name='当月订单提成')
    commission_before = models.FloatField(default=0, verbose_name='以往留存提成')
    commission_passive = models.FloatField(default=0, verbose_name='带徒弟提成')
    commission_shop_manager = models.FloatField(default=0, verbose_name='店长提成')
    commission_minus = models.FloatField(default=0, verbose_name='退单')
    other_salary = models.FloatField(default=0, verbose_name='额外调整')
    total_salary = models.FloatField(default=0, verbose_name='总金额')

    def __str__(self):
        return (
                '员工：%s，提成：%.1f，以前提成：%.1f，被动提成：%.1f'
                % (self.whose_salary, self.commission_current, self.commission_before, self.commission_passive)
        )

    class Meta:
        verbose_name = '月薪'
        verbose_name_plural = '月薪'


class Config(models.Model):
    key = models.CharField(max_length=20, verbose_name='键')
    val = models.TextField(verbose_name='值')

    def __str__(self):
        return '%s：%s' % (self.key, self.val)

    class Meta:
        verbose_name = '配置'
        verbose_name_plural = '配置'