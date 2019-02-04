from django.shortcuts import render, HttpResponse
from django.utils import timezone
from .models import Employee, Order, Monthlymoney
import csv
import datetime
from django.db.models import Q


# with open('employeetest.csv','a',encoding='utf-8',) as csvfile:
#     reader = csv.reader(csvfile)
#     print(reader)
#     for item in reader:
#         print(item)


def index(request):
    year = timezone.now().year
    month = timezone.now().month
    ordersnew = Order.objects.filter(Q(order_time__month = month) & Q(order_time__year = year))
    orderswed = Order.objects.filter(Q(wedding_time__month=month) & Q(wedding_time__year=year))
    return render(request, 'wage/index.html', {'ordersnew':ordersnew, 'orderswed':orderswed})


def employee(request):
    employees = Employee.objects.filter(on_job=True)
    return render(request, 'wage/employee.html', {'employees':employees})


def calculate(request):
    year = timezone.now().year
    month = timezone.now().month

    employees = Employee.objects.filter(on_job=True)
    employees.update(calculate_finished=False)

    orders = Order.objects.filter((Q(order_time__month = month) & Q(order_time__year = year)) | (Q(wedding_time__month = month) & Q(wedding_time__year = year))).filter(calculated=False)
    print('筛选出了当月订单')

    if not orders:
        monthlymoney = Monthlymoney.objects.filter(month=datetime.date(year, month, 10))
        return render(request, 'wage/calculate.html',{
        'monthlymoney':monthlymoney,
        'inf_message': '没有新增订单，未重新计算，直接显示结果',
    })

    unfinished_em = employees.filter(calculate_finished=False)
    while employees.filter(calculate_finished=False):
        for employee in employees.filter(calculate_finished=False):

            ones_orders = orders.filter(whose_order=employee)
            print(employee.name, '的当月订单:', ones_orders)
            commission_rate = employee.commission_rate.split(',')
            print('commission_rate:', commission_rate)

            onespay,created = Monthlymoney.objects.get_or_create(
                month = datetime.date(year,month,10),
                whose_salary = employee,
            )
            print('Monthlymoney:', onespay)
            print('employee:',employee)
            print('created:', created)
            onespay.base_salary = employee.base_pay
            onespay.commission_current = onespay.commission_before = onespay.commission_passive = 0

            for order in ones_orders:
                order.commission_rate = float(commission_rate[order.type])
                order.calculated = True
                order.save()

                if (order.order_time.year, order.order_time.month) == (year, month):
                    if (order.wedding_time.year, order.wedding_time.month) == (year, month):
                        print('当月订单，当月结婚')
                        print('order.money:',order.money,'; order.commission_rate:',order.commission_rate)
                        onespay.commission_current += order.money * order.commission_rate
                    else:
                        print('当月订单，非当月结婚')
                        print('order.money:',order.money,'; order.commission_rate:',order.commission_rate)
                        onespay.commission_current += order.money * order.commission_rate * 0.6
                else:
                    print('非当月订单，当月结婚')
                    print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
                    onespay.commission_before += order.money * order.commission_rate * 0.4

            if not employee.students.exists() or employee.students.filter(calculate_finished=True).count() == employee.students.count():
                employee.calculate_finished = True
                employee.save()
                if employee.students.all():
                    for student in employee.students.all():
                        whopay = Monthlymoney.objects.filter(month=datetime.date(year, month, 10)).get(whose_salary=student)
                        onespay.commission_passive += (whopay.commission_current + whopay.commission_before + whopay.commission_passive) * student.superior_income_rate
                        print('whopay.commission_current', whopay.commission_current)
                        print('whopay.commission_before', whopay.commission_before)
                        print('whopay.commission_passive', whopay.commission_passive)
                        print('student:',student)
                        print('************************************')

                onespay.total_salary = onespay.base_salary + onespay.commission_current + onespay.commission_before + onespay.commission_passive + onespay.commission_shop_manager - onespay.commission_minus + onespay.other_salary
                print('total_salary:',onespay.total_salary)
                print('Monthlymoney:', onespay)
                print('employee:', employee)
                onespay.save()
                print('--------------------------------------------------------')
            else:
                print('还没有计算完')
            print('============================================================================================')

    monthlymoney = Monthlymoney.objects.filter(month = datetime.date(year,month,10))
    #employees = Employee.objects.filter(on_job=True)
    return render(request, 'wage/calculate.html',{
        # 'employees':employees,
        # 'orders':orders,
        'monthlymoney':monthlymoney,
    })


