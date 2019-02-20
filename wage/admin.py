from django.contrib import admin

from .models import Employee, Order, Monthlymoney, Config


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name','base_pay','task_quantity','teacher','shop_manager','on_job','calculate_finished')
    list_filter = ['name']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('client_name','money','type','order_time','wedding_time','is_task_order','status','whose_order','order_number','calculated')
    list_filter = ['order_time','wedding_time']


class MonthlymoneyAdmin(admin.ModelAdmin):
    list_display = ('month','whose_salary','base_salary','commission_current','commission_before','commission_passive','total_salary','task_finished')
    list_filter = ['month', 'whose_salary']


class ConfigAdmin(admin.ModelAdmin):
    list_display = ('key','val')


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Monthlymoney, MonthlymoneyAdmin)
admin.site.register(Config, ConfigAdmin)
