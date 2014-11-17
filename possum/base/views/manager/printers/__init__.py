# -*- coding: utf-8 -*-
#
#    Copyright 2009-2014 Sébastien Bonnegent
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
import logging

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from possum.base.models import Printer
from possum.base.views import permission_required


LOGGER = logging.getLogger(__name__)


@permission_required('base.p1')
def home(request):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    '''
    context = {'menu_manager': True, }
    context['printers'] = Printer.objects.all()
    return render(request, 'printers/home.html', context)


@permission_required('base.p1')
def printer_add(request):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    '''
    context = {'menu_manager': True, }
    context['printers'] = Printer().get_available_printers()
    return render(request, 'printers/add.html', context)


@permission_required('base.p1')
def printer_added(request, name):
    ''' Save new printer
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param name:
    :type name:
    '''
    printer = Printer(name=name)
    printer.save()
    return redirect('printer_home')


@permission_required('base.p1')
def printer_view(request, printer_id):
    '''

    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    '''
    context = {'menu_manager': True, }
    context['printer'] = get_object_or_404(Printer, pk=printer_id)
    if request.method == 'POST':
        options = request.POST.get('options', '').strip()
        header = request.POST.get('header', '')
        footer = request.POST.get('footer', '')
        context['printer'].options = options
        context['printer'].header = header
        context['printer'].footer = footer
        try:
            context['printer'].save()
        except:
            messages.add_message(request, messages.ERROR,
                                 _("Changes could not be saved"))
    return render(request, 'printers/view.html', context)


@permission_required('base.p1')
def printer_select_width(request, printer_id):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    '''
    context = {'menu_manager': True, }
    context['printer'] = get_object_or_404(Printer, pk=printer_id)
    context['max'] = range(14, 120)
    return render(request, 'base/manager/printer_select_width.html',
                  context)


@permission_required('base.p1')
def printer_set_width(request, printer_id, number):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    :param number:
    :type number:
    '''
    printer = get_object_or_404(Printer, pk=printer_id)
    printer.width = number
    printer.save()
    return redirect('printer_view', printer_id)


@permission_required('base.p1')
def printer_test_print(request, printer_id):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    '''
    printer = get_object_or_404(Printer, pk=printer_id)
    if printer.print_test():
        messages.add_message(request, messages.SUCCESS,
                             _("Printing has been accepted"))
    else:
        messages.add_message(request, messages.ERROR,
                             _("Printing test has failed"))
    return redirect('printer_view', printer_id)


@permission_required('base.p1')
def printer_change_kitchen(request, printer_id):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    '''
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.kitchen
    printer.kitchen = new
    printer.save()
    return redirect('printer_view', printer_id)


@permission_required('base.p1')
def printer_change_billing(request, printer_id):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    '''
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.billing
    printer.billing = new
    printer.save()
    return redirect('printer_view', printer_id)


@permission_required('base.p1')
def printer_change_manager(request, printer_id):
    '''
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    '''
    printer = get_object_or_404(Printer, pk=printer_id)
    new = not printer.manager
    printer.manager = new
    printer.save()
    return redirect('printer_view', printer_id)


@permission_required('base.p1')
def kitchen_header(request, printer_id, number=-1):
    ''' Show and set numbers of lines on ticket header for kitchen
    :param HttpRequest request:
    :return rtype: HttpResponse
    :param printer_id:
    :type printer_id:
    :param number:
    :type number:
    '''
    context = {'menu_manager': True, }
    context['printer'] = get_object_or_404(Printer, pk=printer_id)
    context['numbers'] = range(0, 15)
    if number > -1:
        try:
            context['printer'].kitchen_lines = int(number)
            context['printer'].save()
        except:
            LOGGER.warning("number of lines incorrect")
    return render(request, 'printers/kitchen_header.html', context)
