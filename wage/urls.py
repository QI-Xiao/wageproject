from django.urls import path

from . import views

app_name = 'wage'
urlpatterns = [
    path('', views.index, name='index'),
    path('calculate/', views.calculate, name='calculate'),
    path('employee/', views.employee, name='employee'),
    path('restart/', views.restart, name='restart'),
    path('search/', views.search, name='search'),
    path('orderinput/', views.orderinput, name='orderinput'),
    path(r'calculate/<int:onemoney_id>/', views.detail, name='detail'),
    path(r'calculate/paymentoutput/', views.paymentoutput, name='paymentoutput'),
    path(r'changestatus/', views.changestatus, name='changestatus'),
    path(r'calculatebefore/', views.calculatebefore, name='calculatebefore'),
]
