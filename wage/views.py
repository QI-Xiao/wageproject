from django.shortcuts import render, HttpResponse, reverse, get_object_or_404
from django.utils import timezone
from .models import Employee, Order, Monthlymoney
import csv, xlrd, xlwt
import datetime
from django.http import HttpResponseRedirect
import re
from django.conf import settings
from django.db.models import Q

year = yearnow = timezone.now().year
month = monthnow = timezone.now().month
day = daynow = timezone.now().day


def getdate(request):
    global month, year
    month_input = request.GET.get('my_month')
    year_input = request.GET.get('my_year')
    if month_input and year_input:
        print('month_input',month_input,'year_input',year_input)
        month = int(month_input) + 1
        year = int(year_input)


def orderinput(request):
    if request.method == "POST":
        inf_order = []
        orderfile = request.FILES.get("orderinput", None)
        if not orderfile:
            return HttpResponseRedirect(reverse('wage:index'))
        orderfiletype = orderfile.name.split('.')[-1]
        if orderfiletype != 'xlsx' and orderfiletype != 'xls':
            inf_order.append('文件类型不对')
            return render(request, 'wage/inputresult.html', {'inf_order': inf_order})
        destination = open("wage/media/"+orderfile.name, 'wb+')
        print('打开成功')
        for chunk in orderfile.chunks():
            destination.write(chunk)
        destination.close()
        print('保存至服务器')
        workbook = xlrd.open_workbook("wage/media/"+orderfile.name)
        sheet = workbook.sheets()[0]
        nrows = sheet.nrows
        ncols = sheet.ncols
        print('nrows',nrows, 'ncols',ncols)
        for rownum in range(1,nrows):
            data = sheet.row_values(rownum)
            print(rownum, data, '\ndata[8]:', data[8])
            order_number = str(data[8]).strip().split('.')[0]
            if not order_number:
                continue
            print('开始记录日期')
            wedding_time= datetime.datetime(*xlrd.xldate_as_tuple(data[4],workbook.datemode)).date()
            print('wedding_time:', wedding_time)
            order_time = datetime.datetime(*xlrd.xldate_as_tuple(data[5], workbook.datemode)).date()
            print('order_time:', order_time)
            if wedding_time < order_time:
                print('订单日期在结婚日期之后')
                inf_order.append('订单编号：'+ order_number + ' error：订单日期在结婚日期之后')
                continue
            type_dic = {'单租':1, '定制':2, '大牌':3, '璀璨':4, '升级':5}
            order_type = type_dic.get(data[3].strip())
            print('开始订单类型计算')
            if not order_type:
                print('不符合的订单类型:', data[3])
                inf_order.append('订单编号：'+ order_number + ' error：不符合的订单类型 ' + data[3])
                continue
            print('开始处理各项数据')
            moneyminus = float(data[6]) - float(data[7])
            print('计算差值')
            if abs(moneyminus) <= 0.01:
                status = 2
                print('已付全款')
            elif moneyminus > 0.01:
                status = 1
                print('已付定金')
            else:
                print('订单价格有误')
                inf_order.append('订单编号：'+ order_number + ' error：订单价格有误')
                continue
            print('差值计算完毕')
            try:
                whose_order = Employee.objects.get(name=data[9].strip())
            except Employee.DoesNotExist:
                print('没有该员工：', data[9])
                inf_order.append('订单编号：' + order_number + ' error：没有该员工' + data[9])
                continue
            print('get the Order object', order_number)
            try:
                order = Order.objects.get(order_number=order_number)
            except:
                print('开始写入order')
                order = Order.objects.create(
                    order_number=order_number,
                    client_name=data[1].strip(),
                    # tel=int(data[2]),
                    money=float(data[6]),
                    type=order_type,
                    order_time=order_time,
                    wedding_time=wedding_time,
                    status=status,
                    whose_order=whose_order,
                )
                print('订单编号：'+ order_number + '写入成功')
                inf_order.append('订单编号：' + order_number + '写入成功')
            else:
                print('订单已存在')
                inf_order.append('订单编号：'+ order_number + ' error：订单已存在')
                continue
            print()
        # if not inf_order:
        #     inf_order.append('导入成功')
        return render(request, 'wage/inputresult.html', {'inf_order': inf_order})
    return HttpResponseRedirect(reverse('wage:index'))


def writerow(row, onelist, sheet):
    for col in range(len(onelist)):
        print('行：', row, '列：', col, '值：', onelist[col])
        sheet.write(row, col, label=onelist[col])
        print('add finished')


def paymentoutput(request):
    if request.method == "POST":
        totalrow = 0
        totalbook = xlwt.Workbook(encoding='ascii')
        totalsheet = totalbook.add_sheet('sheet 1')
        em_lists = ['姓名', '底薪', '提点', '任务单量', '给师傅提点', '师傅', '店长', '在职', '计算完毕']
        writerow(totalrow, em_lists, totalsheet)

        moneyrow = 0
        moneybook = xlwt.Workbook(encoding='ascii')
        moneysheet = moneybook.add_sheet('sheet 1')
        money_lists = ['店员','底薪','完成任务单','总任务单','当月订单提成','以往留存提成','带徒弟提成','店长提成','退单','额外调整','总金额']
        writerow(moneyrow, money_lists, moneysheet)

        print('a new total sheet')
        for employee in Employee.objects.filter(on_job=True):
            orders = Order.objects.filter(Q(order_time__month=month, order_time__year=year, whose_order=employee) | Q(wedding_time__month=month, wedding_time__year=year, whose_order=employee))

            detailbook = xlwt.Workbook(encoding='ascii')
            detailsheet = detailbook.add_sheet('sheet 1')
            detailrow = 0
            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'yyyy/mm/dd'

            order_list = ['顾客', '金额', '提点', '类型', '预定日期', '婚期', '任务', '折扣', '退单', '状态', '负责人', '编号', '计算完毕', '修改日期']
            writerow(detailrow, order_list, detailsheet)

            for order in orders:
                order_list = [order.client_name, order.money, order.commission_rate, order.type, order.order_time, order.wedding_time, order.is_task_order, order.is_discount_order, order.is_chargeback, order.status, str(order.whose_order), order.order_number, order.calculated, order.change_date]
                detailrow += 1
                for col in range(len(order_list)):
                    print('行：', detailrow, '列：', col, '值：', order_list[col])
                    if col == 4 or col == 5:
                        detailsheet.write(detailrow, col, order_list[col], date_format)
                    else:
                        detailsheet.write(detailrow, col, label=order_list[col])
                    print('add finished')

                print('add detail data')
            detailbook.save(settings.MEDIA_ROOT+str(year)+'年'+str(month)+'月明细'+employee.name+'.xls')
            print('save detail data')

            print('employee:', employee, '[employee.name]:',[employee.name],'[employee.teacher]:',[employee.teacher])
            em_lists = [employee.name, employee.base_pay, employee.commission_rate, employee.task_quantity, employee.superior_income_rate, str(employee.teacher), employee.shop_manager, employee.on_job, employee.calculate_finished]
            totalrow += 1
            writerow(totalrow, em_lists, totalsheet)

            money = employee.monthlymoney_set.get(month=datetime.date(year, month, 10))
            money_lists = [str(money.whose_salary), money.base_salary, money.task_finished, money.whose_salary.task_quantity, money.commission_current, money.commission_before, money.commission_passive, money.commission_shop_manager, money.commission_minus, money.other_salary, money.total_salary]
            moneyrow += 1
            writerow(moneyrow, money_lists, moneysheet)

        totalbook.save(settings.MEDIA_ROOT + str(year)+'年'+str(month)+'月总表' + '.xls')
        moneybook.save(settings.MEDIA_ROOT + str(year) + '年' + str(month) + '月工资总表' + '.xls')
        print('save total data')
        return HttpResponse('导出成功')
    return HttpResponseRedirect(reverse('wage:calculate'))


def changestatus(request):
    status2 = request.POST.getlist('status2')
    for i in status2:
        print('循环2')
        order = Order.objects.get(id=i)
        if order.status == 1:
            order.status = 2
            order.change_date = datetime.date(yearnow, monthnow, daynow)
            order.save()
    return HttpResponseRedirect(reverse('wage:index'))


def detail(request, onemoney_id):
    getdate(request)
    onemoney = get_object_or_404(Monthlymoney, pk=onemoney_id)
    ordersnew = Order.objects.filter(order_time__month = month, order_time__year = year, whose_order=onemoney.whose_salary)
    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year, whose_order=onemoney.whose_salary)
    return render(request, 'wage/detail.html', {'onemoney': onemoney, 'ordersnew':ordersnew, 'orderswed':orderswed, 'month':month, 'year':year})


def index(request):
    getdate(request)
    ordersnew = Order.objects.filter(order_time__month = month, order_time__year = year)
    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year)
    orderchanged = Order.objects.exclude(id__in=ordersnew).exclude(id__in=orderswed).filter(change_date__month=month, change_date__year=year)
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


def calordernew(order, yeardef, monthdef, consider_task=True):
    onespay, created = Monthlymoney.objects.get_or_create(
        month=datetime.date(yeardef, monthdef, 10),
        whose_salary=order.whose_order,
    )
    print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
    if onespay.task_finished < onespay.whose_salary.task_quantity and order.type != 5 and consider_task:
        print('这是任务单')
        onespay.task_finished += 1
        order.commission_rate = 0
        order.is_task_order = True
    else:
        print('这不是任务单')
        commission_rate = order.whose_order.commission_rate.split(',')
        print('commission_rate:', commission_rate)
        order.commission_rate = float(commission_rate[order.type - 1])
    onespay.commission_current += order.money * order.commission_rate * 0.6
    onespay.save()
    order.calculated = True
    order.save()


def calorderwed(orderswed, yeardef, monthdef):
    for order in orderswed:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(yeardef, monthdef, 10),
            whose_salary=order.whose_order,
        )
        print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
        onespay.commission_before += order.money * order.commission_rate * 0.4
        onespay.save()
        order.status = 3
        order.save()


def calonespay(yeardef, monthdef):
    employees = Employee.objects.filter(on_job=True)
    employees.update(calculate_finished=False)

    while employees.filter(calculate_finished=False):
        for employee in employees.filter(calculate_finished=False):
            print('employee:', employee)
            if (not employee.students.exists()) or employee.students.filter(calculate_finished=True).count()==employee.students.count():
                employee.calculate_finished = True
                employee.save()
                onespay, created = Monthlymoney.objects.get_or_create(
                    month=datetime.date(yeardef, monthdef, 10),
                    whose_salary=employee,
                )
                onespay.base_salary = employee.base_pay
                print('onespay.base_salary:',onespay.base_salary)
                onespay.commission_passive = 0
                for student in employee.students.all():
                    studentpay = Monthlymoney.objects.filter(month=datetime.date(yeardef, monthdef, 10)).get(whose_salary=student)
                    studentpay_money = studentpay.commission_current + studentpay.commission_before + studentpay.commission_passive - studentpay.commission_minus
                    rates = student.superior_income_rate.split(',')
                    for rate in rates:
                        if int(rate.split(':')[0]) <= studentpay_money:
                            super_rate = float(rate.split(':')[1])
                        else:
                            break
                    onespay.commission_passive += studentpay_money * super_rate
                    print('studentpay.commission_current', studentpay.commission_current)
                    print('studentpay.commission_before',studentpay.commission_before)
                    print('studentpay.commission_passive', studentpay.commission_passive)
                    print('student:', student)
                    print('************************************')
                onespay.save()
                print('----------------------计算完成---------------------------')
            else:
                print('-------------------还没有计算完成------------------------')
        print('============================================================================================')

    for employee in employees:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(yeardef, monthdef, 10),
            whose_salary=employee,
        )
        if employee.shop_manager:
            onespay.commission_shop_manager = 500
        onespay.total_salary = onespay.base_salary + onespay.commission_current + onespay.commission_before + onespay.commission_passive + onespay.commission_shop_manager - onespay.commission_minus + onespay.other_salary
        onespay.save()
        print('total_salary:', onespay.total_salary, '; Monthlymoney:', onespay)


def calchargeback(chargeback):
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
                    if order.status == 1 or order.status == 2:
                        onespay.commission_minus += order.money * order.commission_rate * 0.6
                    if order.status == 3:
                        onespay.commission_minus += order.money * order.commission_rate
                    onespay.save()
                print('任务单，不做退费')
            order.status = 4
            order.is_chargeback = True
            order.change_date = datetime.date(yearnow, monthnow, daynow)
            order.save()


def calculate(request):
    getdate(request)

    chargeback = request.POST.get('chargeback')
    calchargeback(chargeback)

    ordersbefore = Order.objects.filter(status__in=[1, 2], calculated=False, order_time__lt=datetime.date(year,month,1), wedding_time__month=month, wedding_time__year=year)
    if ordersbefore:
        return render(request, 'wage/calculatebefore.html', {'ordersbefore':ordersbefore})

    ordersnew = Order.objects.filter(order_time__month=month, order_time__year=year, status__in=[1,2], calculated=False)
    for order in ordersnew:
        calordernew(order, year, month)

    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year, status=2, calculated=True)
    calorderwed(orderswed, year, month)

    if not (ordersnew or orderswed or chargeback):
        monthlymoney = Monthlymoney.objects.filter(month=datetime.date(year, month, 10))
        return render(request, 'wage/calculate.html',{
            'monthlymoney': monthlymoney,
            'inf_message': '没有新增订单，未重新计算，直接显示结果',
            'month':month,
            'year': year,
    })

    calonespay(year, month)

    monthlymoney = Monthlymoney.objects.filter(month = datetime.date(year,month,10))

    return render(request, 'wage/calculate.html',{
        'monthlymoney':monthlymoney,
        'month':month,
        'year': year,
    })


def calculatebefore(request):
    taskorder = request.POST.getlist('taskorder')
    print('taskorder:', taskorder)
    for i in taskorder:
        print('循环')
        order = Order.objects.get(id=i)
        order.is_task_order = True
        order.change_date = datetime.date(yearnow, monthnow, daynow)
        order.save()
        print('order是否任务单:',order.is_task_order)
    ordersbefore = Order.objects.filter(status__in=[1, 2], calculated=False, order_time__lt=datetime.date(year, month, 1), wedding_time__month=month, wedding_time__year=year)
    for order in ordersbefore:
        print('获得年份')
        yeardef = order.order_time.year
        monthdef = order.order_time.month
        print('yeardef', yeardef, 'monthdef', monthdef)
        calordernew(order, yeardef, monthdef, consider_task=order.is_task_order)
        calonespay(yeardef, monthdef)
        print('================================')
    return HttpResponseRedirect(reverse('wage:calculate'))


# def bef_cal(request):
#     ordersbefore = Order.objects.filter(status__in=[1, 2], calculated=False, order_time__lt=datetime.date(year,month,1), wedding_time__month=month, wedding_time__year=year)
#     if ordersbefore:
#         return render(request, 'wage/calculatebefore.html', {'ordersbefore':ordersbefore})
#     return HttpResponseRedirect(reverse('wage:bef_cal2'))
#
# def bef_cal2(request):
#     ordersnew = Order.objects.filter(order_time__month=month, order_time__year=year, status__in=[1,2], calculated=False)

