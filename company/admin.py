# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Company
from reversion.admin import VersionAdmin


class CompanyAdmin(VersionAdmin):
    list_display = (
        u'id',
        'nip',
        'name',
        'address',
        'plCapital',
        'plCapital_notes',
    )
    search_fields = ('name',)
admin.site.register(Company, CompanyAdmin)
