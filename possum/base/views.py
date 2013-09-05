# -*- coding: utf-8 -*-
#
#    Copyright 2009, 2010, 2011 Sébastien Bonnegent
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

from possum.base.stats import StatsJourProduit, StatsJourCategorie
from possum.base.bill import Facture
from possum.base.product import Produit, ProduitVendu
from possum.base.payment import PaiementType, Paiement
from possum.base.color import Couleur
from possum.base.category import Categorie
from possum.base.options import Cuisson, Sauce, Accompagnement
from possum.base.location import Zone, Table

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
#from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth.models import User, UserManager, Permission
from django.conf import settings
from django.contrib import messages
from django.utils.functional import wraps


def get_user(request):
    data = {}
    data['perms'] = PermWrapper(request.user)
    data['user'] = request.user
#    data.update(csrf(request))
    return data

def permission_required(perm, **kwargs):
    """This decorator redirect the user to '/'
    if he hasn't the permission.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            else:
                messages.add_message(request, messages.ERROR, "Vous n'avez pas"
                        " les droits nécessaires (%s)." % perm.split('.')[1])
                return HttpResponseRedirect('/')
        return wraps(view_func)(_wrapped_view)
    return decorator

@login_required
def accueil(request):
#    today = datetime.date.today()
    data = get_user(request)

    return render_to_response('base/accueil.html',
            data,
            context_instance=RequestContext(request))

@permission_required('base.p6')
def carte(request):
    """This is not used.
    """
    data = get_user(request)
    data['menu_carte'] = True
    return render_to_response('base/carte.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products(request, cat_id, only_enable=False):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    data['menu_carte'] = True
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    data['cat_current'] = cat
    products = Produit.objects.filter(categorie=cat)
    if only_enable:
        data['products'] = products.filter(actif=True)
        data['only_enable'] = True
    else:
        data['products'] = products
    return render_to_response('base/products.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_new(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    name = request.POST.get('name', '').strip()
    billname = request.POST.get('billname', '').strip()
    prize = request.POST.get('prize', '').strip()
    if name:
        if billname:
            if prize:
                product = Produit()
                product.categorie = cat
                product.nom = name
                product.nom_facture = billname
                product.prix = prize
                try:
                    product.save()
                    logging.info("[%s] new product [%s]" % (data['user'].username, name))
                except:
                    logging.warning("[%s] new product failed: [%s]" % (data['user'].username, name))
                    messages.add_message(request, messages.ERROR, "Le nouveau produit n'a pu être créé.")
            else:
                messages.add_message(request, messages.ERROR, "Vous devez définir un prix pour le nouveau produit.")
        else:
            messages.add_message(request, messages.ERROR, "Vous devez choisir un nom qui s'affichera sur la facture pour le nouveau produit.")
    else:
        messages.add_message(request, messages.ERROR, "Vous devez choisir un nom pour le nouveau produit.")
    return HttpResponseRedirect('/carte/products/cat/%s/' % cat_id)

@permission_required('base.p6')
def products_details(request, product_id):
    data = get_user(request)
    product = get_object_or_404(Produit, pk=product_id)
    data['product'] = product
    return render_to_response('base/a_product.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def products_change(request, product_id):
    data = get_user(request)
    name = request.POST.get('name', '').strip()
    billname = request.POST.get('billname', '').strip()
    prize = request.POST.get('prize', '').strip()
    product = get_object_or_404(Produit, pk=product_id)
    if prize != str(product.prix):
        # new prize, so we have to create a new product to keep statistics
        # and historics
        logging.info("[%s] new prize for [%s]: [%s] > [%s]" % (data['user'].username, product.nom, product.prix, prize))
        old = product
        product = Produit()
        product.actif = old.actif
        old.actif = False
        old.save()
        product.prix = prize
        product.nom = old.nom
        product.nom_facture = old.nom_facture
        product.choix_cuisson = old.choix_cuisson
        product.choix_accompagnement = old.choix_accompagnement
        product.choix_sauce = old.choix_sauce
        product.categorie = old.categorie
        try:
            product.save()
            for c in old.categories_ok.distinct():
                product.categories_ok.add(c)
            for p in old.produits_ok.distinct():
                product.produits_ok.add(p)
            messages.add_message(request, messages.INFO,
                    "Le prix d'un produit ne peut être modifié, en conséquence un nouveau produit a été créé et l'ancien a été désactivé.")
        except:
            messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
            logging.warning("[%s] save failed for product [%s]" % (data['user'].username, product.nom))
            return HttpResponseRedirect('/carte/products/cat/%s/' % product.categorie.id)
    if name != product.nom:
        logging.info("[%s] new product name: [%s] > [%s]" % (data['user'].username, product.nom, name))
        product.nom = name
    if billname != product.nom_facture:
        logging.info("[%s] new product bill name [%s]: [%s] > [%s]" % (data['user'].username, product.nom, product.nom_facture, billname))
        product.nom_facture = billname

    try:
        product.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logging.warning("[%s] save failed for product [%s]" % (data['user'].username, product.nom))
    return HttpResponseRedirect('/carte/products/cat/%s/' % product.categorie.id)


@permission_required('base.p6')
def categories(request):
    data = get_user(request)
    data['menu_carte'] = True
    data['categories'] = Categorie.objects.order_by('priorite', 'nom')
    return render_to_response('base/categories.html',
                    data,
                    context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_delete(request, cat_id):
    data = get_user(request)
    data['current_cat'] = get_object_or_404(Categorie, pk=cat_id)
    data['categories'] = Categorie.objects.order_by('priorite', 'nom').exclude(id=cat_id)
    cat_report_id = request.POST.get('cat_report', '').strip()
    action = request.POST.get('valide', '').strip()
    if action == "Supprimer":
        # we have to report stats and products ?
        if cat_report_id:
            try:
                report = Categorie.objects.get(id=cat_report_id)
                # we transfert all statistics
                for stat in StatsJourCategorie.objects.filter(categorie__id=cat_id):
                    try:
                        new = StatsJourCategorie.objects.get(date=stat.date, categorie=report)
                        new.nb += stat.nb
                        new.valeur += stat.valeur
                        new.save()
                        stat.delete()
                    except StatsJourCategorie.DoesNotExist:
                        stat.categorie = report
                        stat.save()
                # we transfert all products
                for product in Produit.objects.filter(categorie__id=cat_id):
                    product.categorie = report
                    product.save()
            except Categorie.DoesNotExist:
                logging.warning("[%s] categorie [%s] doesn't exist" % (data['user'].username, cat_report_id))
                messages.add_message(request, messages.ERROR, "La catégorie n'existe pas.")
                return HttpResponseRedirect('/carte/categories/%s/delete/' % cat_id)
        # now, we have to delete the categorie and remove all products remains
        for product in Produit.objects.filter(categorie__id=cat_id):
            for stat in StatsJourProduit.objects.filter(produit=product):
                stat.delete()
            product.delete()
        for stat in StatsJourCategorie.objects.filter(categorie__id=cat_id):
            stat.delete()
        logging.info("[%s] categorie [%s] deleted" % (data['user'].username, data['current_cat'].nom))
        data['current_cat'].delete()
        return HttpResponseRedirect('/carte/categories/')
    elif action == "Annuler":
        return HttpResponseRedirect('/carte/categories/')
    return render_to_response('base/categories_delete.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p6')
def categories_new(request):
    data = get_user(request)
    priority = request.POST.get('priority', '').strip()
    name = request.POST.get('name', '').strip()
    if name:
        cat = Categorie()
        cat.nom = name
        if priority:
            cat.priorite = priority
        try:
            cat.save()
            logging.info("[%s] new categorie [%s]" % (data['user'].username, name))
        except:
            logging.warning("[%s] new categorie failed: [%s] [%s]" % (data['user'].username, cat.priorite, cat.nom))
            messages.add_message(request, messages.ERROR, "La nouvelle catégorie n'a pu être créée.")
    else:
        messages.add_message(request, messages.ERROR, "Vous devez choisir un nom pour la nouvelle catégorie.")
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_less_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.priorite -= nb
    cat.save()
    logging.info("[%s] cat [%s] priority - %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_more_priority(request, cat_id, nb=1):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    cat.priorite += nb
    cat.save()
    logging.info("[%s] cat [%s] priority + %d" % (data['user'].username, cat.nom, nb))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_surtaxable(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.surtaxable
    cat.surtaxable = new
    cat.save()
    logging.info("[%s] cat [%s] surtaxable: %s" % (data['user'].username, cat.nom, cat.surtaxable))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_alcool(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.alcool
    cat.alcool = new
    cat.save()
    logging.info("[%s] cat [%s] alcool: %s" % (data['user'].username, cat.nom, cat.alcool))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_change(request, cat_id):
    data = get_user(request)
    name = request.POST.get('name', '').strip()
    color = request.POST.get('color', '').strip()
    cat = get_object_or_404(Categorie, pk=cat_id)
    if not cat.couleur or color != cat.couleur.web():
        logging.info("[%s] new categorie color [%s]" % (data['user'].username, cat.nom))
        c = Couleur()
        if c.set_from_rgb(color):
            try:
                old_color = Couleur.objects.get(red=c.red, green=c.green, blue=c.blue)
                c = old_color
            except Couleur.DoesNotExist:
                c.save()
            cat.couleur = c
        else:
            logging.warning("[%s] invalid color [%s]" % (data['user'].username, color))
            messages.add_message(request, messages.ERROR, "La nouvelle couleur n'a pu être enregistrée.")
    if name != cat.nom:
        logging.info("[%s] new categorie name: [%s] > [%s]" % (data['user'].username, cat.nom, name))
        cat.nom = name

    try:
        cat.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logging.warning("[%s] save failed for [%s]" % (data['user'].username, cat.nom))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p6')
def categories_disable_surtaxe(request, cat_id):
    data = get_user(request)
    cat = get_object_or_404(Categorie, pk=cat_id)
    new = not cat.disable_surtaxe
    cat.disable_surtaxe = new
    cat.save()
    logging.info("[%s] cat [%s] disable_surtaxe: %s" % (data['user'].username, cat.nom, cat.disable_surtaxe))
    return HttpResponseRedirect('/carte/categories/')

@permission_required('base.p5')
def pos(request):
    data = get_user(request)
    data['menu_pos'] = True
    return render_to_response('base/pos.html',
                                data,
                                context_instance=RequestContext(request))

@login_required
def jukebox(request):
    data = get_user(request)
    data['menu_jukebox'] = True
    return render_to_response('base/jukebox.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p7')
def stats(request):
    data = get_user(request)
    data['menu_stats'] = True
    return render_to_response('base/stats.html',
                                data,
                                context_instance=RequestContext(request))

@login_required
def profile(request):
    data = get_user(request)
    data['menu_profile'] = True
    data['perms_list'] = settings.PERMS
    old = request.POST.get('old', '').strip()
    new1 = request.POST.get('new1', '').strip()
    new2 = request.POST.get('new2', '').strip()
    if old:
        if data['user'].check_password(old):
            if new1 and new1 == new2:
                data['user'].set_password(new1)
                data['user'].save()
                data['success'] = "Le mot de passe a été changé."
                logging.info('[%s] password changed' % data['user'].username)
            else:
                data['error'] = "Le nouveau mot de passe n'est pas valide."
                logging.warning('[%s] new password is not correct' % data['user'].username)
        else:
            data['error'] = "Le mot de passe fourni n'est pas bon."
            logging.warning('[%s] check password failed' % data['user'].username)
    return render_to_response('base/profile.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p1')
def users(request):
    data = get_user(request)
    data['menu_users'] = True
    data['perms_list'] = settings.PERMS
    data['users'] = User.objects.all()
    for user in data['users']:
        user.permissions = [p.codename for p in user.user_permissions.all()]
    return render_to_response('base/users.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p1')
def users_new(request):
    data = get_user(request)
    # data is here to create a new user ?
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    if login:
        user = User()
        user.username = login
        user.first_name = first_name
        user.last_name = last_name
        user.email = mail
        try:
            user.save()
            logging.info("[%s] new user [%s]" % (data['user'].username, login))
            #users(request)
        except:
            #data['error'] = "Le nouvel utilisateur n'a pu être créé."
            logging.warning("[%s] new user failed: [%s] [%s] [%s] [%s]" % (data['user'].username, login, first_name, last_name, mail))
            messages.add_message(request, messages.ERROR, "Le nouveau compte n'a pu être créé.")
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_change(request, user_id):
    data = get_user(request)
    login = request.POST.get('login', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    mail = request.POST.get('mail', '').strip()
    user = get_object_or_404(User, pk=user_id)
    if login != user.username:
        logging.info("[%s] new login: [%s] > [%s]" % (data['user'].username, user.username, login))
        user.username = login
    if first_name != user.first_name:
        logging.info("[%s] new first name for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.first_name, first_name))
        user.first_name = first_name
    if last_name != user.last_name:
        logging.info("[%s] new last name for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.last_name, last_name))
        user.last_name = last_name
    if mail != user.email:
        logging.info("[%s] new mail for [%s]: [%s] > [%s]" % (data['user'].username, user.username, user.email, mail))
        user.email = mail

    try:
        user.save()
    except:
        messages.add_message(request, messages.ERROR, "Les modifications n'ont pu être enregistrées.")
        logging.warning("[%s] save failed for [%s]" % (data['user'].username, user.username))
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_active(request, user_id):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    new = not user.is_active
    p1 = Permission.objects.get(codename="p1")
    if not new and p1.user_set.count() == 1 and p1 in user.user_permissions.all():
        messages.add_message(request, messages.ERROR, "Il doit rester au moins un compte actif avec la permission P1.")
        logging.warning("[%s] we must have at least one active user with P1 permission.")
    else:
        user.is_active = new
        user.save()
        logging.info("[%s] user [%s] active: %s" % (data['user'].username, user.username, user.is_active))
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_passwd(request, user_id):
    """Set a new random password for a user.
    """
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    passwd = UserManager().make_random_password(length=10)
    user.set_password(passwd)
    user.save()
    messages.add_message(request, messages.SUCCESS, "Le nouveau mot de passe l'utilisateur %s est : %s" % (user.username, passwd))
    logging.info("[%s] user [%s] new password" % (data['user'].username, user.username))
    return HttpResponseRedirect('/users/')

@permission_required('base.p1')
def users_change_perm(request, user_id, codename):
    data = get_user(request)
    user = get_object_or_404(User, pk=user_id)
    # little test because because user can do ugly things :)
    # now we are sure that it is a good permission
    if codename in settings.PERMS:
        perm = Permission.objects.get(codename=codename)
        if perm in user.user_permissions.all():
            if codename == 'p1' and perm.user_set.count() == 1:
                # we must have at least one person with this permission
                logging.info("[%s] user [%s] perm [%s]: at least should have one person" % (data['user'].username, user.username, codename))
                messages.add_message(request, messages.ERROR, "Il doit rester au moins 1 compte avec la permission P1.")
            else:
                user.user_permissions.remove(perm)
                logging.info("[%s] user [%s] remove perm: %s" % (data['user'].username, user.username, codename))
        else:
            user.user_permissions.add(perm)
            logging.info("[%s] user [%s] add perm: %s" % (data['user'].username, user.username, codename))
    else:
        logging.warning("[%s] wrong perm info : [%s]" % (data['user'].username, codename))
    return HttpResponseRedirect('/users/')

@permission_required('base.p5')
def bill_new(request):
    """Create a new bill"""
    data = get_user(request)
    data['menu_bills'] = True
    bill = Facture()
    bill.save()
    return render_to_response('base/facture.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def table_select(request, bill_id):
    """Select/modify table of a bill"""
    data = get_user(request)
    data['menu_bills'] = True
    data['zones'] = Zone.objects.all()
    data['bill_id'] = bill_id
    return render_to_response('base/tables.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def table_set(request, bill_id, table_id):
    """Select/modify table of a bill"""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    table = get_object_or_404(Table, pk=table_id)
    bill.set_table(table)
    data['facture'] = bill
    return render_to_response('base/facture.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def couverts_select(request, bill_id):
    """List of couverts for a bill"""
    data = get_user(request)
    data['menu_bills'] = True
    data['nb_couverts'] = range(35)
    data['bill_id'] = bill_id
    return render_to_response('base/couverts.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p5')
def couverts_set(request, bill_id, number):
    """Set couverts of a bill"""
    data = get_user(request)
    bill = get_object_or_404(Facture, pk=bill_id)
    bill.set_couverts(number)
    data['facture'] = bill
    return render_to_response('base/facture.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p3')
def factures(request):
    data = get_user(request)
    data['menu_bills'] = True
#    data['factures'] = Facture.objects.all()
    data['factures'] = Facture().non_soldees()
    return render_to_response('base/factures.html',
                                data,
                                context_instance=RequestContext(request))

@permission_required('base.p3')
def bill_view(request, bill_id):
    data = get_user(request)
    data['facture'] = get_object_or_404(Facture, pk=bill_id)
    return render_to_response('base/facture.html',
                                data,
                                context_instance=RequestContext(request))

#   return render_to_response('login.html', data,
#           context_instance=RequestContext(request))

