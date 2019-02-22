import random, datetime, xlwt

def randomorder():
    base = 60 # base + 1 到 base + 30
    content = [['', '客户姓名', '', '订单类型', '婚期', '订单时间', '订单金额', '', '订单编号', '客户所属顾问']]
    for i in range(1,31):
        whose_order = name=random.choice(['徒孙2', '徒孙1', '徒弟2', '徒弟1', '师有徒', '师无徒'])
        order_number = str(i + base)
        client_name = '测二{}'.format(int(order_number))
        money = random.randrange(1000,5000,500)
        # type = random.randint(1,5)
        type = random.choice(['单租', '定制', '大牌', '璀璨', '升级'])
        order_time = datetime.date(2019,4,1) + datetime.timedelta(days=random.randint(-5,10))
        wedding_time = order_time + datetime.timedelta(25)
        status = 1
        oneorder = ['', client_name, '', type, wedding_time, order_time, money, '', order_number, whose_order]
        content.append(oneorder)
    return content


def writeexcel(lists, path):
    workbook = xlwt.Workbook(encoding='ascii')
    sheet = workbook.add_sheet('sheet 1')
    datastyle = xlwt.XFStyle()
    datastyle.num_format_str = 'yyyy-mm-dd'

    for row in range(len(lists)):
        onelist = lists[row]
        for col in range(len(onelist)):
            item = onelist[col]
            if isinstance(item, datetime.date):
                sheet.write(row, col, item, datastyle)
            else:
                sheet.write(row, col, label=item)
            print('行:', row, ' 列:', col, ' 值:', item)
    workbook.save(path)


if __name__ == '__main__':
    writeexcel(randomorder(), './00order.xls')