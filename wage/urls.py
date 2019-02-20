from django.urls import path

from . import views

app_name = 'wage'
urlpatterns = [
    path('', views.index, name='index'),
    path('calculate/', views.calculate, name='calculate'),
    path('employee/', views.employee, name='employee'),
    path('restart/', views.restart, name='restart'),
    path('search/', views.search, name='search'),
    path('inputorder/', views.inputorder, name='inputorder'),
    path(r'calculate/<int:onemoney_id>/', views.detail, name='detail'),
    path(r'calculate/paymentoutput/', views.paymentoutput, name='paymentoutput'),
    path(r'changestatus/', views.changestatus, name='changestatus'),
    path(r'calculatebefore/', views.calculatebefore, name='calculatebefore'),
    path(r'bef_cal/', views.bef_cal, name='bef_cal'),
    path(r'bef_cal3/', views.bef_cal3, name='bef_cal3'),
    path('inputemployee/', views.inputemployee, name='inputemployee'),
    path('randomorder/', views.randomorder, name='randomorder'),
]
