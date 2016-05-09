    # -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django import forms

import django_filters
from dal import autocomplete

from .models import Product
from pola.filters import (
                          # AutocompleteChoiceFilter,
                          CrispyFilterMixin,
                          NoHelpTextFilterMixin)


class NullProductFilter(django_filters.Filter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value:
            return qs.filter(company=None)
        return qs


class ProductFilter(NoHelpTextFilterMixin,
                    CrispyFilterMixin,
                    django_filters.FilterSet):
    company_empty = NullProductFilter(label="Tylko produkty bez producenta")
    # company = AutocompleteChoiceFilter(
    #     autocomplete_name="CompanyAutocomplete")

    def __init__(self, *args, **kwargs):
        super(ProductFilter, self).__init__(*args, **kwargs)
        # TODO: Fix Autocomplete

    class Meta:
        model = Product
        fields = ['name', 'code', 'company_empty', 'company']
        order_by = (
            ('name', _('Nazwa (A-Z)')),
            ('-name', _('Nazawa (Z-A)')),
            ('company__name', _('Nazwa producenta (A-Z)')),
            ('-company__name', _('Nazwa producenta (Z-A)')),
            ('query_count', _(u'Liczba zeskanowań (rosnąco)')),
            ('-query_count', _(u'Liczba zeskanowań (malejąco)')),
        )
