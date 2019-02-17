import xlwt
import datetime

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

workbook.save('Excel_Workbook.xls')

aaa = [1,2,3,4]
for i in aaa:
    print(aaa.index(i))

