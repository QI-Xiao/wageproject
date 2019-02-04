import csv


# with open('employeetest.csv','a',encoding='utf-8',) as csvfile:
#     reader = csv.reader(csvfile)
#     print(reader)
#     for item in reader:
#         print(item)
# csvpy3-8.csv
s='''
name,age,phone,address
1,1,1,1
2,3,4,5
5,4,2,6
6,3,2,7
'''


# with open(r'C:\Users\QiXiao\Desktop\qx.csv','r') as f:
f_csv = s.split('\n')
# headers = next(f_csv)
for row in f_csv:
    row = row.split(',')
    print(row)

'''
<form method="post" action="{% url 'wage:detail' onemoney.id %}">
    {% csrf_token %}
    <button type="submit"></button>
</form>
'''