# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Product
from reversion.admin import VersionAdmin


class ProductAdmin(VersionAdmin):
    list_display = (
        'id',
        'name',
        'code',
        'company',
    )
    list_filter = ('company',)
    search_fields = ('name',)
admin.site.register(Product, ProductAdmin)
