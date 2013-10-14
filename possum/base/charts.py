# -*- coding: utf-8 -*-
#
#    Copyright 2009-2013 Sébastien Bonnegent
#
#    This file is part of POSSUM.
#
#    POSSUM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    POSSUM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with POSSUM.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db import models
from django.db.models import Max, Avg
from decimal import Decimal
import datetime
from possum.base.category import Categorie
from possum.base.product import Produit
from possum.base.payment import PaiementType
from possum.base.utils import nb_sorted
from possum.base.monthlystat import MonthlyStat
import logging
from chartit import PivotDataPool, PivotChart

logger = logging.getLogger(__name__)

def month_name(*t):
    """Sert à trier les mois."""
    logger.debug(t)
    names = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Avr', 
            5: 'Mai', 6: 'Jui', 7: 'Jui', 8: 'Aou', 
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    month_num = int(t[0][0])
    logger.debug("names[%d] > [%s]" % (month_num, names[month_num]))
    return (names[month_num], )

def month_sort(*x):
    logger.debug(x)
    return (int(x[0][1][0]),)

def get_datapool_year(year, keys):
    logger.debug(" ")
    series = []
    objects = MonthlyStat.objects.filter(year=year)
    for key in keys.keys():
        series.append({'options': {
            'source': objects.filter(key=key),
            'categories': 'month'},
            'terms': {keys[key]: Avg('value')}
            })
    return PivotDataPool(
            series = series,
            sortf_mapf_mts=(month_sort, month_name, True))

def get_chart(datasource, graph, keys, title, xaxis):
    """
    graph: line / pie
    """
    terms = [keys[x] for x in keys.keys()]
    return PivotChart(
                datasource = datasource,
                series_options = [{
                    'options': {
                        'type': graph,
                        'stacking': False
                        },
                    'terms': terms
                    }],
                chart_options = {
                    'title': {
                        'text': title},
                    'credits': {
                        'enabled': False
                        },
                    'xAxis': {
                        'title': {
                            'text': xaxis}},
                    'yAxis': {
                        'title': {
                            'text': ''}},
                    })

def get_chart_year_ttc(year):
    keys = {"total_ttc": 'total ttc',
            "guests_total_ttc": 'restauration',
            "bar_total_ttc": 'bar'}
    try:
        datasource = get_datapool_year(year, keys)
    except:
        return False
    return get_chart(datasource, 'line', keys, "Total TTC pour l'année %s" % year, "Mois")

def get_chart_year_bar(year):
    keys = {"bar_average": 'TM/facture',
            "bar_nb": 'nb factures',
            "bar_total_ttc": 'total ttc bar'}
    try:
        datasource = get_datapool_year(year, keys)
    except:
        return False
    return get_chart(datasource, 'line', keys, "Activité bar pour l'année %s" % year, "Mois")

def get_chart_year_guests(year):
    keys = {"guests_average": 'TM/couvert',
            "guests_nb": 'nb couverts',
            "guests_total_ttc": 'total ttc restaurant'}
    try:
        datasource = get_datapool_year(year, keys)
    except:
        return False
    return get_chart(datasource, 'line', keys, "Activité restaurant pour l'année %s" % year, "Mois")
