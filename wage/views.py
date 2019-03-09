from django.shortcuts import render, HttpResponse, reverse, get_object_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.conf import settings
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required

from .models import Employee, Order, Monthlymoney, Config
from PIL import Image, ImageDraw, ImageFont

import xlrd, xlwt, datetime, re, os


thismonth = datetime.date.today()
year = thismonth.year
month = thismonth.month
day = thismonth.day
firstday = thismonth.replace(day=1)
lastmonth = firstday + datetime.timedelta(days=-10)
yearaccount = lastmonth.year
monthaccount = lastmonth.month
dayaccount = lastmonth.day


def getdate(request):
    global month, year, monthaccount, yearaccount
    month_input = request.GET.get('my_month')
    year_input = request.GET.get('my_year')
    if month_input and year_input:
        print('month_input',month_input,'year_input',year_input)
        month = int(month_input) + 1
        year = int(year_input)

    month_account = request.GET.get('account_month')
    year_account = request.GET.get('account_year')
    if month_account and year_account:
        print('month_account',month_account,'year_account',year_account)
        monthaccount = int(month_account) + 1
        yearaccount = int(year_account)


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print('a new folder')
    else:
        print('there is a folder')

@login_required
def inputorder(request):
    if request.method == "POST":
        inf_message = []
        orderfile = request.FILES.get("orderinput", None)
        if not orderfile:
            return HttpResponseRedirect(reverse('wage:index'))
        orderfiletype = orderfile.name.split('.')[-1]
        if orderfiletype != 'xlsx' and orderfiletype != 'xls':
            inf_message.append('文件类型不对')
            return render(request, 'wage/inputresult.html', {'inf_message': inf_message})
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
                inf_message.append('订单编号：'+ order_number + ' error：订单日期在结婚日期之后')
                continue
            type_dic = {'单租':1, '定制':2, '大牌':3, '璀璨':4, '升级':5}
            order_type = type_dic.get(data[3].strip())
            print('开始订单类型计算')
            if not order_type:
                print('不符合的订单类型:', data[3])
                inf_message.append('订单编号：'+ order_number + ' error：不符合的订单类型 ' + data[3])
                continue
            # moneyminus = float(data[6]) - float(data[7])
            # if abs(moneyminus) <= 0.01:
            #     status = 2
            #     print('已付全款')
            # elif moneyminus > 0.01:
            #     status = 1
            #     print('已付定金')
            # else:
            #     print('订单价格有误')
            #     inf_message.append('订单编号：'+ order_number + ' error：订单价格有误')
            #     continue
            # print('差值计算完毕')
            try:
                whose_order = Employee.objects.get(name=data[9].strip())
            except Employee.DoesNotExist:
                print('没有该员工：', data[9])
                inf_message.append('订单编号：' + order_number + ' error：没有该员工' + data[9])
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
                    status=1,
                    whose_order=whose_order,
                )
                print('订单编号：'+ order_number + '写入成功')
                inf_message.append('订单编号：' + order_number + '写入成功')
            else:
                print('订单已存在')
                inf_message.append('订单编号：'+ order_number + ' error：订单已存在')
                continue
            print()
        return render(request, 'wage/inputresult.html', {'inf_message': inf_message})
    return HttpResponseRedirect(reverse('wage:index'))

@login_required
# 有 bug，必须保证没有徒弟的先输入进去，不然会出错
def inputemployee(request):
    if request.method == "POST":
        inf_message = []
        employeefile = request.FILES.get("inputemployee", None)
        if not employeefile:
            return HttpResponseRedirect(reverse('wage:index'))
        filetype = employeefile.name.split('.')[-1]
        if filetype != 'xlsx' and filetype != 'xls':
            inf_message.append('文件类型不对')
            return render(request, 'wage/inputresult.html', {'inf_message': inf_message})
        destination = open("wage/media/"+employeefile.name, 'wb+')
        print('打开成功')
        for chunk in employeefile.chunks():
            destination.write(chunk)
        destination.close()
        print('保存至服务器')
        workbook = xlrd.open_workbook("wage/media/"+employeefile.name)
        sheet = workbook.sheets()[0]
        nrows = sheet.nrows
        ncols = sheet.ncols
        print('nrows',nrows, 'ncols',ncols)
        for rownum in range(1,nrows):
            data = sheet.row_values(rownum)
            print(rownum, data, '\ndata[0]:', data[0])
            name = str(data[0]).strip()
            if not name:
                continue

            try:
                teacher = Employee.objects.get(name=data[5].strip())
            except:
                # inf_message.append('员工姓名：' + name + ' error：师父不存在')
                teacher = None
            shop_manage = data[6].strip()
            on_job = data[7].strip()
            if shop_manage == '是':
                shop_manage = True
            elif shop_manage == '否':
                shop_manage = False
            else:
                inf_message.append('员工姓名：' + name + ' error：是否店长有错')
                continue

            if on_job == '是':
                on_job = True
            elif on_job == '否':
                on_job = False
            else:
                inf_message.append('员工姓名：' + name + ' error：是否在职有错')
                continue

            try:
                Employee.objects.get(name=name)
            except Employee.DoesNotExist:
                print('开始写入employee')
                Employee.objects.create(
                    name=name,
                    base_pay=float(data[1]),
                    commission_rate=data[2].strip(),
                    task_quantity=int(data[3]),
                    superior_income_rate =data[4].strip(),
                    teacher=teacher,
                    shop_manager=shop_manage,
                    on_job=on_job
                )
                inf_message.append('员工姓名：' + name + '写入成功')
            else:
                print('员工已存在')
                inf_message.append('员工姓名：'+ name + ' error：员工已存在')
                continue
            print()
        return render(request, 'wage/inputresult.html', {'inf_message': inf_message})
    return HttpResponseRedirect(reverse('wage:index'))


def len_byte(value):
    length = len(value)
    utf8_length = len(value.encode('utf-8'))
    length = (utf8_length - length) / 2 + length
    return int(length)


def writeexcel(lists, path):
    workbook = xlwt.Workbook(encoding='ascii')
    sheet = workbook.add_sheet('sheet 1')
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy-mm-dd'
    datastyle.alignment = alignment
    strstyle = xlwt.XFStyle()
    strstyle.alignment = alignment

    # 确定栏位宽度
    col_width = []
    for i in range(len(lists)):
        for j in range(len(lists[i])):
            if i == 0:
                col_width.append(len_byte(str(lists[i][j])))
            else:
                if col_width[j] < len_byte(str(lists[i][j])):
                    col_width[j] = len_byte(str(lists[i][j]))
    # 设置栏位宽度，栏位宽度小于10时候采用默认宽度
    for i in range(len(col_width)):
        if col_width[i] >= 10:
            sheet.col(i).width = 256 * (col_width[i] + 1)

    for row in range(len(lists)):
        onelist = lists[row]
        for col in range(len(onelist)):
            item = onelist[col]
            if isinstance(item, datetime.date):
                sheet.write(row, col, item, datastyle)
            else:
                sheet.write(row, col, item, strstyle)
            # print('行:', row, ' 列:', col, ' 值:', item)
    workbook.save(path)

@login_required
def paymentoutputexcel(request):
    if request.method == "POST":
        em_lists = [['姓名', '底薪', '提点', '任务单量', '给师傅提点', '师傅', '店长', '在职', '计算完毕']]
        money_lists = [['店员', '底薪', '完成任务单', '总任务单', '当月订单提成', '以往留存提成', '带徒弟提成', '店长提成', '退单', '额外调整', '总金额']]
        path = settings.MEDIA_ROOT + str(yearaccount)+'年'+str(monthaccount)+'月'
        mkdir(path)

        for employee in Employee.objects.filter(on_job=True):
            em_lists.append([employee.name, employee.base_pay, employee.commission_rate, employee.task_quantity, employee.superior_income_rate, str(employee.teacher), employee.shop_manager, employee.on_job, employee.calculate_finished])
            # print(employee)
            money = employee.monthlymoney_set.get(month=datetime.date(yearaccount, monthaccount, 10))
            money_lists.append([str(money.whose_salary), format(money.base_salary,'.2f'), money.task_finished, money.whose_salary.task_quantity, format(money.commission_current,'.2f'), format(money.commission_before,'.2f'), format(money.commission_passive,'.2f'), format(money.commission_shop_manager,'.2f'), format(money.commission_minus,'.2f'), format(money.other_salary,'.2f'), format(money.total_salary,'.2f')])
            # print('money_lists:',money_lists)
            orders = Order.objects.filter(Q(order_time__month=monthaccount, order_time__year=yearaccount, whose_order=employee) | Q(wedding_time__month=monthaccount, wedding_time__year=yearaccount, whose_order=employee)).order_by('-is_task_order', 'order_time', 'money')
            order_lists = [['顾客', '金额', '提点', '类型', '预定日期', '婚期', '任务', '折扣', '状态', '负责人', '编号', '计算完毕', '服务结束日期', '退单日期']]
            for order in orders:
                order_lists.append([order.client_name, order.money, order.commission_rate, order.get_type_display(), order.order_time, order.wedding_time, order.is_task_order, order.is_discount_order, order.get_status_display(), str(order.whose_order), order.order_number, order.calculated, order.orderfinish_date, order.chargeback_date])
            # print('order_lists:', order_lists)
            writeexcel(order_lists, path + '/' + str(yearaccount) + '年' + str(monthaccount) + '月订单明细' + employee.name + '.xls')
            order_lists = []
            # print('结束', employee)

        writeexcel(em_lists, path + '/' + str(yearaccount)+'年'+str(monthaccount)+'月员工总表' + '.xls')
        writeexcel(money_lists, path + '/' + str(yearaccount)+'年'+str(monthaccount)+'月工资总表' + '.xls')
        return HttpResponse('导出成功')
    return HttpResponseRedirect(reverse('wage:calculate'))


def part_jpg(items, title, width_now, height_now, draw, color, font, addline=False):
    if items:
        height_now += 46
        draw.text((width_now, height_now), title, color, font)
        height_now += font.size + 46
        for item in items:
            draw.text((width_now, height_now), '          '.join(item), color, font)
            height_now += 54
        height_now += font.size
        if addline:
            draw.line(((width_now, height_now), (1060, height_now)), (0, 0, 0), width=5)
    return width_now, height_now


def createjpg(itemlists, path):

    print(itemlists)

    width = 1125
    height = 330 + 144*6 + len(itemlists['task_order'])*54 + len(itemlists['new_order'])*54 + len(itemlists['wedding_order'])*54 + len(itemlists['student'])*54 + len(itemlists['shop_manager'])*54 + len(itemlists['chargeback_order'])*54 + 236 + 80 + 46
    # newIm = Image.open('sample.jpg')
    newIm = Image.new('RGB', (width, height), 'white')

    # font_type = '/System/Library/Fonts/AdobeSongStd-Light.otf'
    font_type = 'AdobeHeitiStd-Regular.otf'
    header_font = ImageFont.truetype(font_type, 110)
    title_font = ImageFont.truetype(font_type, 63)
    font = ImageFont.truetype(font_type, 26)
    end_font = ImageFont.truetype(font_type, 80)
    color = "#000000"

    draw = ImageDraw.Draw(newIm)

    draw.text((58, 74), u'%s' % itemlists['name'], color, header_font)
    draw.text((58, 226), u'%s' % itemlists['date'], color, title_font)
    draw.line(((58, 329), (1060, 329)), (0, 0, 0), width=5)
    # draw.line(((58, 340), (1060, 340)), (0, 0, 0), width=5)
    width_now = 58
    height_now = 330

    width_now, height_now = part_jpg(itemlists['task_order'], '任务单', width_now, height_now, draw, color, font)
    width_now, height_now = part_jpg(itemlists['new_order'], '当月订单提点', width_now, height_now, draw, color, font)
    width_now, height_now = part_jpg(itemlists['wedding_order'], '当月完成服务提点', width_now, height_now, draw, color, font)

    if itemlists['task_order'] or itemlists['new_order'] or itemlists['wedding_order']:
        draw.line(((58, height_now), (1060, height_now)), (0, 0, 0), width=5)

    width_now, height_now = part_jpg(itemlists['student'], '传帮带提点', width_now, height_now, draw, color, font, True)
    width_now, height_now = part_jpg(itemlists['shop_manager'], '全店提点', width_now, height_now, draw, color, font, True)
    width_now, height_now = part_jpg(itemlists['chargeback_order'], '退单扣减', width_now, height_now, draw, color, font, True)

    height_now += 46
    draw.text((width_now, height_now), '基础底薪', color, font)
    draw.text((800, height_now), itemlists['base_pay'], color, font)
    height_now += 46 + font.size
    draw.text((width_now, height_now), '额外调整', color, font)
    draw.text((800, height_now), itemlists['other_salary'], color, font)
    height_now += 46 + font.size
    draw.line(((58, height_now), (1060, height_now)), (0, 0, 0), width=5)
    height_now += 46
    draw.text((750, height_now), itemlists['total_salary'], color, end_font)
    newIm.save(path)

@login_required
def paymentoutput(request):
    if request.method == "POST":
        em_lists = [['姓名', '底薪', '提点', '任务单量', '给师傅提点', '师傅', '店长', '在职', '计算完毕']]
        money_lists = [['店员', '底薪', '完成任务单', '总任务单', '当月订单提成', '以往留存提成', '带徒弟提成', '店长提成', '退单', '额外调整', '总金额']]
        path = settings.MEDIA_ROOT + str(yearaccount)+'年'+str(monthaccount)+'月'
        outputpath = settings.MEDIA_URL + str(yearaccount)+'年'+str(monthaccount)+'月'
        mkdir(path)

        output_url = []
        for employee in Employee.objects.filter(on_job=True):
            em_lists.append([employee.name, employee.base_pay, employee.commission_rate, employee.task_quantity, employee.superior_income_rate, str(employee.teacher), employee.shop_manager, employee.on_job, employee.calculate_finished])
            # print(employee)
            money = employee.monthlymoney_set.get(month=datetime.date(yearaccount, monthaccount, 10))
            money_lists.append([str(money.whose_salary), format(money.base_salary,'.2f'), money.task_finished, money.whose_salary.task_quantity, format(money.commission_current,'.2f'), format(money.commission_before,'.2f'), format(money.commission_passive,'.2f'), format(money.commission_shop_manager,'.2f'), format(money.commission_minus,'.2f'), format(money.other_salary,'.2f'), format(money.total_salary,'.2f')])
            # print('money_lists:',money_lists)
            orders = Order.objects.filter(Q(order_time__month=monthaccount, order_time__year=yearaccount, whose_order=employee) | Q(wedding_time__month=monthaccount, wedding_time__year=yearaccount, whose_order=employee)).order_by('-is_task_order', 'order_time', 'money')
            itemlists = {'name':employee.name,
                         'date':str(yearaccount) + '年' + str(monthaccount) + '月工资明细',
                         'task_order':[i.split(',') for i in money.details_task.split(';') if i],
                         'new_order':[i.split(',') for i in money.details_new.split(';') if i],
                         'wedding_order':[i.split(',') for i in money.details_wed.split(';') if i],
                         'student':[i.split(',') for i in money.details_teacher.split(';') if i],
                         'shop_manager':[i.split(',') for i in money.details_manager.split(';') if i],
                         'chargeback_order':[i.split(',') for i in money.details_back.split(';') if i],
                         'base_pay':format(money.base_salary,'.2f'),
                         'other_salary':format(money.other_salary,'.2f'),
                         'total_salary':format(money.total_salary,'.2f')
                         }
            ordersnewtotal = Order.objects.filter(order_time__month=monthaccount, order_time__year=yearaccount, whose_order=employee, calculated=True)
            orderstask = ordersnewtotal.filter(is_task_order=True)
            ordersnew = ordersnewtotal.exclude(id__in=orderstask)
            orderswed = Order.objects.filter(orderfinish_date__month=monthaccount, orderfinish_date__year=yearaccount, status=3)
            orderschargeback = Order.objects.filter(chargeback_date__month=monthaccount, chargeback_date__year=yearaccount, status=4)
            students = employee.students

            print(itemlists)

            order_lists = [['顾客', '金额', '提点', '类型', '预定日期', '婚期', '任务', '折扣', '状态', '负责人', '编号', '计算完毕', '服务结束日期', '退单日期']]
            for order in orders:
                order_lists.append([order.client_name, order.money, order.commission_rate, order.get_type_display(), order.order_time, order.wedding_time, order.is_task_order, order.is_discount_order, order.get_status_display(), str(order.whose_order), order.order_number, order.calculated, order.orderfinish_date, order.chargeback_date])
            # print('order_lists:', order_lists)
            output_url.append([employee.name, outputpath + '/' + str(yearaccount) + '年' + str(monthaccount) + '月工资明细' + employee.name + '.jpg'])
            createjpg(itemlists, path + '/' + str(yearaccount) + '年' + str(monthaccount) + '月工资明细' + employee.name + '.jpg')

            order_lists = []
            # print('结束', employee)

        # writeexcel(em_lists, path + '/' + str(yearaccount)+'年'+str(monthaccount)+'月员工总表' + '.xls')
        # writeexcel(money_lists, path + '/' + str(yearaccount)+'年'+str(monthaccount)+'月工资总表' + '.xls')
        return render(request, 'wage/outputresult.html', {'output_url': output_url})
        # return HttpResponseRedirect(reverse('wage:calculate'))
    return HttpResponseRedirect(reverse('wage:index'))

@login_required
def detail(request, onemoney_id):
    getdate(request)
    onemoney = get_object_or_404(Monthlymoney, pk=onemoney_id)
    ordersnew = Order.objects.filter(order_time__month = monthaccount, order_time__year = yearaccount, whose_order=onemoney.whose_salary)
    orderswed = Order.objects.filter(wedding_time__month=monthaccount, wedding_time__year=yearaccount, whose_order=onemoney.whose_salary)
    return render(request, 'wage/detail.html', {'onemoney': onemoney, 'ordersnew':ordersnew, 'orderswed':orderswed, 'month':month, 'year':year, 'monthaccount':monthaccount, 'yearaccount':yearaccount})

@login_required
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


'''
把退单和计算的分开
保证日期一致
增加一个导出结果的返回功能
增加一个主页面直接查看结果的功能
使计算的那个页面没法直接get到
中间过程不能直接get，并且进行一些优化
计算页面翻日期是直接查看结果，不计算
'''

@login_required
def index(request):
    getdate(request)
    ordersnew = Order.objects.filter(order_time__month=month, order_time__year=year).order_by("is_task_order","order_time", "wedding_time")
    orderswed = Order.objects.filter(wedding_time__month=month, wedding_time__year=year).order_by("order_time", "wedding_time")
    orderchanged = Order.objects.exclude(id__in=ordersnew).exclude(id__in=orderswed).filter(chargeback_date__month=month, chargeback_date__year=year).order_by("order_time", "wedding_time")
    print('year,month:', year, month)
    # Order.objects.all().update(chargeback_date=None, status=1,calculated=False,orderfinish_date=None, is_task_order=False)
    # Monthlymoney.objects.all().delete()
    # Order.objects.all().update(status=1, calculated=False, chargeback_date=None)# is_task_order=False,
    # Order.objects.filter(order_number__range=[31, 65]).update(is_task_order=False, status=1, calculated=False)
    # Employee.objects.all().update(superior_income_rate='0:0.1,1000:0.1,2000:0.1')
    # Order.objects.filter(order_number__range=[31,60]).delete()
    # employees = Employee.objects.all()
    # for employee in employees:
    #     employee.task_quantity = random.randint(1,3)
    #     employee.save()
    return render(request, 'wage/index.html', {'ordersnew':ordersnew, 'orderswed':orderswed, 'orderchanged':orderchanged, 'month':month, 'year':year, 'monthaccount':monthaccount, 'yearaccount':yearaccount})


def calordernew(order, yeardef, monthdef, consider_task=True):
    onespay, created = Monthlymoney.objects.get_or_create(
        month=datetime.date(yeardef, monthdef, 10),
        whose_salary=order.whose_order,
    )
    print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
    if order.is_task_order is False:
        if onespay.task_finished < onespay.whose_salary.task_quantity and order.type != 5 and consider_task:
            print('这是任务单')
            onespay.task_finished += 1
            order.commission_rate = 0
            order.is_task_order = True
            orderlist = [order.order_number, order.client_name, str(order.order_time), str(order.wedding_time),
                         order.get_type_display(), format(order.money, '0.2f')]
            onespay.details_task += ','.join(orderlist) + ';'

        else:
            print('这不是任务单')
            commission_rate = order.whose_order.commission_rate.split(',')
            print('commission_rate:', commission_rate)
            order.commission_rate = float(commission_rate[order.type - 1])
            orderlist = [order.order_number, order.client_name, str(order.order_time), str(order.wedding_time), order.get_type_display(), format(order.money, '0.2f'), format(order.money * order.commission_rate * 0.6, '0.2f')]
            onespay.details_new += ','.join(orderlist) + ';'
        onespay.commission_current += order.money * order.commission_rate * 0.6
    else:
        orderlist = [order.order_number, order.client_name, str(order.order_time), str(order.wedding_time),
                     order.get_type_display(), format(order.money, '0.2f')]
        onespay.details_task += ','.join(orderlist) + ';'
    onespay.save()
    order.calculated = True
    order.save()
    print('order.calculated:', order.calculated)


def calorderwed(orderswed, yeardef, monthdef):
    for order in orderswed:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(yeardef, monthdef, 10),
            whose_salary=order.whose_order,
        )
        print('order.money:', order.money, '; order.commission_rate:', order.commission_rate)
        moneybefore = order.money * order.commission_rate * 0.4
        onespay.commission_before += moneybefore
        orderlist = [order.order_number, order.client_name, str(order.order_time), str(order.wedding_time),
                     order.get_type_display(), format(order.money, '0.2f'), format(moneybefore, '0.2f')]
        onespay.details_wed += ','.join(orderlist) + ';'
        onespay.save()
        order.status = 3
        order.save()


def calonespay(yeardef, monthdef):
    employees = Employee.objects.filter(on_job=True)
    employees.update(calculate_finished=False)
    Employee.objects.filter(on_job=False).update(calculate_finished=True)

    while employees.filter(calculate_finished=False):
        for employee in employees.filter(calculate_finished=False):
            if (not employee.students.exists()) or employee.students.filter(calculate_finished=True).count() == employee.students.count():
                employee.calculate_finished = True
                employee.save()
                onespay, created = Monthlymoney.objects.get_or_create(
                    month=datetime.date(yeardef, monthdef, 10),
                    whose_salary=employee,
                )
                onespay.base_salary = employee.base_pay
                print('onespay.base_salary:',onespay.base_salary)
                onespay.commission_passive = 0
                onespay.details_teacher = ''
                for student in employee.students.filter(on_job=True):
                    studentpay = Monthlymoney.objects.filter(month=datetime.date(yeardef, monthdef, 10)).get(whose_salary=student)
                    studentpay_money = studentpay.commission_current + studentpay.commission_before + studentpay.commission_passive - studentpay.commission_minus
                    rates = student.superior_income_rate.split(',')
                    for rate in rates:
                        key, value = rate.split(':')
                        if int(key) <= studentpay_money:
                            super_rate = float(value)
                        elif studentpay_money < 0:
                            super_rate = float(value)
                            break
                        else:
                            break
                    teacherget_money = studentpay_money * super_rate
                    onespay.commission_passive += teacherget_money
                    onespay.details_teacher += ','.join([student.name, format(studentpay_money, '0.2f'), format(teacherget_money, '0.2f')]) + ';'
                    # print('super_rate:', super_rate, 'studentpay_money:', studentpay_money)
                    # print('studentpay.commission_current', studentpay.commission_current)
                    # print('studentpay.commission_before',studentpay.commission_before)
                    # print('studentpay.commission_passive', studentpay.commission_passive)
                    # print('student:', student)
                    # print('************************************')
                    # input('aaaaaaaaaa')
                onespay.save()
                print('月薪：', onespay.whose_salary, onespay.commission_current, onespay.commission_before, onespay.commission_passive, onespay.commission_minus)
                # input('bbbbbbbbbbbbb')
                # print('----------------------计算完成---------------------------')
            # else:
                # print('-------------------还没有计算完成------------------------')
        # print('============================================================================================')

    for employee in employees:
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(yeardef, monthdef, 10),
            whose_salary=employee,
        )
        if employee.shop_manager:
            manager_rates = Config.objects.get(key='店长提成').val.split(',')
            monthly_turnover = Order.objects.filter(order_time__month=monthdef, order_time__year=yeardef).aggregate(Sum('money')).get('money__sum')
            if monthly_turnover is None:
                onespay.commission_shop_manager = 0
            else:
                for rate in manager_rates:
                    key, val = rate.split(':')
                    if int(key) <= monthly_turnover:
                        manager_rate = float(val)
                    else:
                        break
                onespay.commission_shop_manager = manager_rate * monthly_turnover
            onespay.details_manager = ','.join([format(monthly_turnover, '0.2f'), format(onespay.commission_shop_manager, '0.2f')]) + ';'
        onespay.total_salary = onespay.base_salary + onespay.commission_current + onespay.commission_before + onespay.commission_passive + onespay.commission_shop_manager - onespay.commission_minus + onespay.other_salary
        onespay.save()
        print('total_salary:', onespay.total_salary, '; Monthlymoney:', onespay)


def calchargeback(order, yeardef, monthdef):
    inf_message = '退单：' + order.order_number + '，此单尚未处理或为任务单，不进行退费'
    if order.status != 0:
        print(order, '是需要处理的订单')
        onespay, created = Monthlymoney.objects.get_or_create(
            month=datetime.date(yeardef, monthdef, 10),
            whose_salary=order.whose_order,
        )
        if order.calculated and (order.is_task_order is False):
            print('不是任务单，进行退费')
            if order.status == 1 or order.status == 2:
                minus_money = order.money * order.commission_rate * 0.6
                onespay.commission_minus += minus_money
                inf_message = '退单：' + order.order_number + '，退定金，退单金额：' + str(minus_money)
            if order.status == 3:
                minus_money = order.money * order.commission_rate
                onespay.commission_minus += minus_money
                inf_message = '退单：' + order.order_number + '，退全款，退单金额：' + str(minus_money)
            print('onespay.commission_minus:',onespay.commission_minus, 'minus_money:', minus_money)
            # input('aaaaaaa')
        else:
            minus_money = 0
        orderlist = [order.order_number, order.client_name, str(order.order_time), str(order.wedding_time), order.get_type_display(), format(order.money, '0.2f'), format(minus_money, '0.2f')]
        onespay.details_back += ','.join(orderlist) + ';'
        onespay.save()
    order.status = 4
    order.save()
    return inf_message

@login_required
def calculate(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('wage:index'))

    getdate(request)

    ordersbefore = Order.objects.filter(status__in=[1, 2], calculated=False, order_time__lt=datetime.date(yearaccount, monthaccount, 1),wedding_time__month=monthaccount, wedding_time__year=yearaccount)
    if ordersbefore:
        return render(request, 'wage/calculatebefore.html', {'ordersbefore': ordersbefore})

    inf_message = []
    ordersback = Order.objects.filter(chargeback_date__year=yearaccount,chargeback_date__month=monthaccount).exclude(status=4)
    for order in ordersback:
        inf_message.append(calchargeback(order, yearaccount, monthaccount))

    ordersnew = Order.objects.filter(order_time__month=monthaccount, order_time__year=yearaccount, status__in=[1,2], calculated=False).order_by('order_time', 'money')
    for order in ordersnew:
        calordernew(order, yearaccount, monthaccount)

    # orderswed = Order.objects.filter(wedding_time__month=monthaccount, wedding_time__year=yearaccount, status=2, calculated=True)
    orderswed = Order.objects.filter(orderfinish_date__month=monthaccount, orderfinish_date__year=yearaccount, status=2)
    if orderswed.filter(calculated=False):
        return HttpResponse('肯定不会出现这个情况，如果出现，请找程序猿。。。')
    calorderwed(orderswed, yearaccount, monthaccount)

    if not (ordersnew or orderswed or ordersback):
        for employee in Employee.objects.filter(on_job=True):
            Monthlymoney.objects.get_or_create(month=datetime.date(yearaccount, monthaccount, 10), whose_salary=employee)
        monthlymoney = Monthlymoney.objects.filter(month=datetime.date(yearaccount, monthaccount, 10))
        return render(request, 'wage/calculate.html',{
            'monthlymoney': monthlymoney,
            'inf_message': '没有新增订单，未重新计算，直接显示结果',
            # 'month': month,
            # 'year': year,
            'monthaccount': monthaccount,
            'yearaccount': yearaccount,
    })

    calonespay(yearaccount, monthaccount)
    monthlymoney = Monthlymoney.objects.filter(month=datetime.date(yearaccount, monthaccount, 10))

    return render(request, 'wage/calculate.html', {
        'monthlymoney': monthlymoney,
        'inf_message': inf_message,
        # 'month': month,
        # 'year': year,
        'monthaccount': monthaccount,
        'yearaccount': yearaccount
    })

@login_required
def calculatebefore(request):
    if request.method == 'POST':
        taskorder = request.POST.getlist('taskorder')
        print('taskorder:', taskorder)
        for i in taskorder:
            print('循环')
            order = Order.objects.get(id=i)
            if order.type == 5:
                return render(request, 'wage/inputresult.html', {'inf_message': ['订单：'+order.order_number+'，类型为升级，不可为任务单。']})
            order.is_task_order = True
            order.commission_rate = 0
            order.save()
            print('order是否任务单:',order.is_task_order)
        ordersbefore = Order.objects.filter(status__in=[1, 2], calculated=False, order_time__lt=datetime.date(yearaccount, monthaccount, 1), wedding_time__month=monthaccount, wedding_time__year=yearaccount)
        for order in ordersbefore:
            print('获得年份')
            yeardef = order.order_time.year
            monthdef = order.order_time.month
            print('yeardef', yeardef, 'monthdef', monthdef)
            calordernew(order, yeardef, monthdef, consider_task=order.is_task_order)
            calonespay(yeardef, monthdef)
            print('================================')
    return HttpResponseRedirect(reverse('wage:index'))

@login_required
def findstatus(request):
    orderswed = Order.objects.filter(Q(wedding_time__month=monthaccount, wedding_time__year=yearaccount, status=1) | Q(wedding_time__lt=datetime.date(yearaccount, monthaccount, 1), calculated=True, status=1))
    return render(request, 'wage/findstatus.html', {'orderswed': orderswed})

@login_required
def findtask(request):
    ordersnew = Order.objects.filter(order_time__month=monthaccount, order_time__year=yearaccount, status__in=[1,2], calculated=False)
    return render(request, 'wage/findtask.html', {'ordersnew': ordersnew})

@login_required
def findchargeback(request):
    return HttpResponse('目前计算退单请通过搜索功能')

@login_required
def changestatus(request):
    if request.method == 'POST':
        status2 = request.POST.getlist('status2')
        for i in status2:
            print('循环2')
            order = Order.objects.get(id=i)
            if order.status == 1:
                order.status = 2
                order.orderfinish_date = datetime.date(yearaccount, monthaccount, dayaccount)
                order.save()
    return HttpResponseRedirect(reverse('wage:index'))

@login_required
def changetask(request):
    if request.method == 'POST':
        taskorder = request.POST.getlist('taskorder')
        print('taskorder:', taskorder)
        inf_order = []
        for i in taskorder:
            print('循环')
            order = Order.objects.get(id=i)
            if order.is_task_order:
                continue
            onespay, created = Monthlymoney.objects.get_or_create(
                month=datetime.date(yearaccount, monthaccount, 10),
                whose_salary=order.whose_order,
            )
            if onespay.task_finished < onespay.whose_salary.task_quantity and order.type != 5:
                print('这是任务单')
                onespay.task_finished += 1
                onespay.save()
                order.commission_rate = 0
                order.is_task_order = True
                # order.change_date = datetime.date(yearaccount, monthaccount, dayaccount)
                order.save()
            elif order.type == 5:
                inf_order.append('订单：' + order.order_number + ' 为升级订单，不能为任务单')
            else:
                inf_order.append('员工：' + str(onespay.whose_salary) + ' 本月任务单已满，订单：' + order.order_number + ' 不能为任务单')
        if inf_order:
            return HttpResponse('\n'.join(inf_order))
    return HttpResponseRedirect(reverse('wage:index'))

@login_required
def changechargeback(request):
    if request.method == 'POST':
        # chargeback = request.POST.get('chargeback')

        chargeback = request.POST.getlist('chargeback')
        for back in chargeback:
            order = Order.objects.get(order_number=back)
            print('order:', order)
            if order.status != 4:
                order.chargeback_date = datetime.date(yearaccount, monthaccount, dayaccount)
                order.save()
    return HttpResponseRedirect(reverse('wage:index'))
