from django.shortcuts import render, HttpResponse, reverse, get_object_or_404
from django.utils import timezone
from .models import Employee, Order, Monthlymoney
import pandas
import csv
import datetime
from django.http import HttpResponseRedirect
import re
from collections import namedtuple
# with open('employeetest.csv','a',encoding='utf-8',) as csvfile:
#     reader = csv.reader(csvfile)
#     print(reader)
#     for item in reader:
#         print(item)

year = yearnow = timezone.now().year
month = monthnow = timezone.now().month
day = daynow = timezone.now().day


def orderinput(request):
    if request.method == "POST":
        orderfile = request.FILES.get("orderinput", None)
        if not orderfile:
            return HttpResponse('没有文件')
        if orderfile.name.split('.')[-1] != 'csv':
            return HttpResponse('文件类型不对')
        destination = open("wage/media/"+orderfile.name, 'wb+')
        for chunk in orderfile.chunks():
            destination.write(chunk)
        destination.close()
        with open("wage/media/"+orderfile.name, 'r') as file:
            f_csv = csv.reader(file)
            headings = next(f_csv)
            print(headings)
            for row in f_csv:
                print(row)
                if row[0]:
                    order_time = row[3].replace('/','-')
                    wedding_time = row[4].replace('/', '-')
                    whose_order = Employee.objects.get(name=row[8])
                    print(order_time)
                    print('aaaaaa')
                    order, created = Order.objects.get_or_create(
                        client_name = row[0],
                        money = row[1],
                        type = row[2],
                        order_time = order_time,
                        wedding_time = wedding_time,
                        status = row[7],
                        whose_order = whose_order,
                        order_number = row[9],)
                    print('finished')
                    input('请确认')

        # try:
        #     file = orderfile.read()
        #     print('file',type(file), file)
        #     file = file.decode('utf-8')
        #     print('file2',type(file), file)
        # except Exception as e:
        #     print(e)
        #     return HttpResponse('编码不对')
        # f_csv = csv.reader(file)
        # print('file3', type(f_csv), f_csv)
        # # headings = next(f_csv)
        # # Row = namedtuple('Row', headings)
        # print('读取成功')
        # for row in f_csv:
        #     print(row)
        #     #row = Row(*r)
        #     #print(row.name)
        #
        # orderfile.close()
        return HttpResponse('写入成功')
    return HttpResponse('要post呀')


def paymentoutput(request):
    if request.method == "POST":
        em_list = []
        for employee in Employee.objects.filter(on_job=True):
            monthlymoney = Monthlymoney.objects.filter(month=datetime.date(year, month, 10))
            ordersnew = Order.objects.filter(order_time__month=month, order_time__year=year, whose_order=employee)
            orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year, whose_order=employee)
            em_list.append([employee.name,employee.base_pay,employee.commission_rate,employee.task_quantity,employee.superior_income_rate,employee.teacher,employee.shop_manager,employee.on_job,employee.calculate_finished])
            with open('wage/media/'+str(year)+'年'+str(month)+'月明细'+employee.name+'.csv','w',newline='',encoding='utf-8') as file:
                f_csv = csv.writer(file)
                for order in (ordersnew or orderswed):
                    f_csv.writerow([order.client_name,order.money,order.commission_rate,order.type,order.order_time,order.wedding_time,order.is_task_order,order.is_discount_order,order.is_chargeback,order.status,order.whose_order,order.order_number,order.calculated,order.origin_status,order.change_date,])

        print(em_list)
        with open("wage/media/"+str(year)+'年'+str(month)+'月总表'+'.csv', 'w', newline='', encoding='utf-8') as file:
            f_csv = csv.writer(file)
            f_csv.writerows(em_list)

        return HttpResponse('导出成功')
    return HttpResponseRedirect(reverse('wage:calculate'))


def changestatus(request):
    status1 = request.POST.getlist('status1')
    status2 = request.POST.getlist('status2')
    status1 = list(set(status1))
    status2 = list(set(status2))
    print('status1:', status1)
    print('status2:', status2)
    statusintersect = list(set(status1).intersection(set(status2)))
    if statusintersect:
        print('statusintersect:', statusintersect)
        return HttpResponse('重复勾选')
    for i in status1:
        print('循环1')
        order = Order.objects.get(id=i)
        if order.status == 0:
            order.status = 1
            order.change_date = datetime.date(yearnow, monthnow, daynow)
            order.save()
    for i in status2:
        print('循环2')
        order = Order.objects.get(id=i)
        if order.status == (0 or 1):
            order.status = 2
            order.change_date = datetime.date(yearnow, monthnow, daynow)
            order.save()
    return HttpResponseRedirect(reverse('wage:index'))


def detail(request, onemoney_id):
    global month, year
    month_input = request.GET.get('my_month')
    year_input = request.GET.get('my_year')
    if month_input and year_input:
        print('month_input',month_input,'year_input',year_input)
        month = int(month_input) + 1
        year = int(year_input)
    onemoney = get_object_or_404(Monthlymoney, pk=onemoney_id)
    ordersnew = Order.objects.filter(order_time__month = month, order_time__year = year, whose_order=onemoney.whose_salary)
    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year, whose_order=onemoney.whose_salary)
    return render(request, 'wage/detail.html', {'onemoney': onemoney, 'ordersnew':ordersnew, 'orderswed':orderswed, 'month':month, 'year':year})


def index(request):
    global month, year
    month_input = request.GET.get('my_month')
    year_input = request.GET.get('my_year')
    if month_input and year_input:
        print('month_input',month_input,'year_input',year_input)
        month = int(month_input) + 1
        year = int(year_input)
    ordersnew = Order.objects.filter(order_time__month = month, order_time__year = year)
    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year)
    print('直到这一步没有问题')
    orderchanged = Order.objects.exclude(id__in=ordersnew).exclude(id__in=orderswed).filter(change_date__month=month, change_date__year=year)
    print('这一步呢')
    print('year,month:',year,month)
    return render(request, 'wage/index.html', {'ordersnew':ordersnew, 'orderswed':orderswed, 'orderchanged':orderchanged, 'month':month, 'year':year})


def employee(request):
    employees = Employee.objects.filter(on_job=True)
    return render(request, 'wage/employee.html', {'employees':employees})


def restart(request):
    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year)
    orderswed.update(status=2, is_chargeback=False, calculated=True)

    ordersnew = Order.objects.filter(order_time__month=month, order_time__year=year)
    ordersnew.update(status=1, is_chargeback=False, calculated=False, is_task_order=False)

    employees = Employee.objects.filter(on_job=True)
    employees.update(calculate_finished=False, commission_rate='0.1,0.2,0.3,0.4')

    onespay = Monthlymoney.objects.filter(month=datetime.date(year, month, 10))
    onespay.update(task_finished=0,commission_current=0,commission_before=0,commission_shop_manager=0,commission_minus=0,other_salary=0)
    print('已经重置')
    return HttpResponseRedirect(reverse('wage:index'))


def search(request):
    getcontent = request.POST.get('search')
    print('getcontent:', getcontent)
    if not getcontent:
        return HttpResponseRedirect(reverse('wage:index'))
    pattern = re.compile(r'.*%s.*' % getcontent)
    print(pattern)
    orders = Order.objects.all()
    order_matched = []
    for order in orders:
        if pattern.findall(order.order_number) or pattern.findall(order.client_name):
            order_matched.append(order)
            print('找到符合要求的：',order)
    if order_matched:
        return render(request, 'wage/search.html', {'order_matched':order_matched})
    return render(request, 'wage/search.html', {'inf_message': '没有结果'})


def calculate(request):
    global month, year
    print('month',month)
    print('year',year)
    month_input = request.GET.get('my_month')
    year_input = request.GET.get('my_year')
    if month_input and year_input:
        print('month_input',month_input,'year_input',year_input)
        month = int(month_input) + 1
        year = int(year_input)
    print('year:',year)
    print('month:',month)
    chargeback = request.POST.get('chargeback')
    if chargeback:
        print('chargeback:', chargeback)
        order= Order.objects.get(order_number = chargeback)
        print(order)
        if order.status != 4:
            if order.status != 0:
                print('是需要处理的订单')
                if order.calculated and (order.is_task_order is False):
                    print('不是任务单，进行退费')
                    onespay, created = Monthlymoney.objects.get_or_create(
                        month=datetime.date(yearnow, monthnow, 10),
                        whose_salary=order.whose_order,
                    )
                    if order.status == (1 or 2):
                        onespay.commission_minus += order.money * order.commission_rate * 0.5
                    if order.status == 3:
                        onespay.commission_minus += order.money * order.commission_rate
                    onespay.save()
                print('任务单，不做退费')
            order.status = 4
            order.is_chargeback = True
            order.change_date = datetime.date(yearnow, monthnow, daynow)
            order.save()

    ordersnew = Order.objects.filter(order_time__month=month, order_time__year=year, status__in=[1,2], calculated=False)
    for order in ordersnew:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(year, month, 10),
            whose_salary=order.whose_order,
        )
        print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
        if onespay.task_finished < onespay.whose_salary.task_quantity:
            print('这是任务单')
            onespay.task_finished += 1
            order.commission_rate = 0
            order.is_task_order = True
        else:
            print('这不是任务单')
            commission_rate = order.whose_order.commission_rate.split(',')
            order.commission_rate = float(commission_rate[order.type])
        onespay.commission_current += order.money * order.commission_rate * 0.5
        onespay.save()
        order.calculated = True
        order.save()

    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year, status=2, calculated=True)
    for order in orderswed:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(year, month, 10),
            whose_salary=order.whose_order,
        )
        print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
        onespay.commission_before += order.money * order.commission_rate * 0.5
        onespay.save()
        order.status = 3
        order.save()

    if not (ordersnew or orderswed or chargeback):
        monthlymoney = Monthlymoney.objects.filter(month=datetime.date(year, month, 10))
        return render(request, 'wage/calculate.html',{
            'monthlymoney': monthlymoney,
            'inf_message': '没有新增订单，未重新计算，直接显示结果',
            'month':month,
            'year': year,
    })

    employees = Employee.objects.filter(on_job=True)
    employees.update(calculate_finished=False)

    while employees.filter(calculate_finished=False):
        for employee in employees.filter(calculate_finished=False):
            print('employee:', employee)
            if (not employee.students.exists()) or employee.students.filter(calculate_finished=True).count()==employee.students.count():
                employee.calculate_finished = True
                employee.save()
                onespay, created = Monthlymoney.objects.get_or_create(
                    month=datetime.date(year, month, 10),
                    whose_salary=employee,
                )
                onespay.base_salary = employee.base_pay
                print('onespay.base_salary:',onespay.base_salary)
                onespay.commission_passive = 0
                for student in employee.students.all():
                    whopay = Monthlymoney.objects.filter(month=datetime.date(year, month, 10)).get(whose_salary=student)
                    onespay.commission_passive += (whopay.commission_current + whopay.commission_before + whopay.commission_passive - whopay.commission_minus) * student.superior_income_rate
                    print('whopay.commission_current', whopay.commission_current)
                    print('whopay.commission_before',whopay.commission_before)
                    print('whopay.commission_passive', whopay.commission_passive)
                    print('student:', student)
                    print('************************************')
                onespay.save()
                print('----------------------计算完成---------------------------')
            else:
                print('-------------------还没有计算完成------------------------')
        print('============================================================================================')

    for employee in employees:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(year, month, 10),
            whose_salary=employee,
        )
        if employee.shop_manager:
            onespay.commission_shop_manager = 500
        onespay.total_salary = onespay.base_salary + onespay.commission_current + onespay.commission_before + onespay.commission_passive + onespay.commission_shop_manager - onespay.commission_minus + onespay.other_salary
        onespay.save()
        print('total_salary:', onespay.total_salary, '; Monthlymoney:', onespay)

    monthlymoney = Monthlymoney.objects.filter(month = datetime.date(year,month,10))

    return render(request, 'wage/calculate.html',{
        'monthlymoney':monthlymoney,
        'month':month,
        'year': year,
    })