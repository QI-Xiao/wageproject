import xlwt
import datetime, os


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print('a new folder')
    else:
        print('there is a folder')

file = r'.\aaaaa'
mkdir(file)

workbook = xlwt.Workbook(encoding = 'ascii')
worksheet = workbook.add_sheet('My Worksheet')

date_format = xlwt.XFStyle()
date_format.num_format_str = 'yyyy/mm/dd'

worksheet.write(0, 0, label = 'Row 0, 齐笑啊啊啊啊啊啊啊啊啊 0 Value')
worksheet.write(0, 1, label = 'Row 0, 齐笑0 Value')
worksheet.write(0, 2, label = 'Row 0, 齐')
worksheet.write(1, 0, label = 'Value')
worksheet.write(2, 0, datetime.datetime.now(), date_format)
worksheet.write(2, 1, 43480, date_format)

workbook.save('aaa/Excel_Workbook.xls')

aaa = [1,2,3,4]
for i in aaa:
    print(aaa.index(i))

def writeexcel(titlelist, otherlists, path):
    workbook = xlwt.Workbook(encoding='ascii')
    sheet = workbook.add_sheet('sheet 1')
    for col in range(len(titlelist)):
        print('行：', 0, '列：', col, '值：', titlelist[col])
        sheet.write(0, col, label=titlelist[col])
        print('add finished')
    for row in range(len(otherlists)):
        onelist = otherlists[row]
        for col in range(len(onelist)):
            print('行：', row+1, '列：', col, '值：', onelist[col])
            sheet.write(row+1, col, label=onelist[col])
            print('add finished')
    workbook.save(path)

# titlelist = [1,2,3]
# otherlists = [[4,5,6],[1,2,3,4]]
# writeexcel(titlelist, otherlists, path='./aaa.xls')

