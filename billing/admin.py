from django.contrib import admin
from django.contrib import admin
from billing.models import Product, Customer, Bill, BillItem, Denomination

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Bill)
admin.site.register(BillItem)
admin.site.register(Denomination)