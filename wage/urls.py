from django.urls import path, re_path

from . import views

app_name = 'wage'
urlpatterns = [
    path('', views.index, name='index'),
    path(r'calculate/', views.calculate, name='calculate'),
    path(r'search/', views.search, name='search'),
    path(r'inputorder/', views.inputorder, name='inputorder'),
    path(r'calculate/<int:onemoney_id>/', views.detail, name='detail'),
    path(r'calculate/paymentoutput/', views.paymentoutput, name='paymentoutput'),
    path(r'calculatebefore/', views.calculatebefore, name='calculatebefore'),
    path(r'inputemployee/', views.inputemployee, name='inputemployee'),
    path(r'findstatus/', views.findstatus, name='findstatus'),
    path(r'findtask/', views.findtask, name='findtask'),
    path(r'findorderpeople/', views.findorderpeople, name='findorderpeople'),
    path(r'findorderpeople/<int:order_id>/', views.orderdetail, name='orderdetail'),
    path(r'findorderpeople/<int:order_id>/change', views.changeorderpeople, name='changeorderpeople'),
    path(r'changestatus/', views.changestatus, name='changestatus'),
    path(r'changetask/', views.changetask, name='changetask'),
    path(r'changechargeback/', views.changechargeback, name='changechargeback'),
    path(r'calculateagain/', views.calculateagain, name='calculateagain'),
]
