from django.contrib import admin
from .models import Product , Company, Order
# Register your models here.


class urun(admin.ModelAdmin):
    list_display=('name','size', 'company',)

admin.site.register(Product,urun)


class sirket(admin.ModelAdmin):
    list_display=('name',)
    
    
admin.site.register(Company, sirket)
admin.site.register(Order)