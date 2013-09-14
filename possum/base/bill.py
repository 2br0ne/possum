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
import logging
import datetime
from decimal import Decimal
from django.db.models import Sum
from possum.base.payment import Paiement
from possum.base.payment import PaiementType
from django.contrib.auth.models import User
import os
from possum.base.stats import StatsJourGeneral, StatsJourPaiement, \
        StatsJourProduit, StatsJourCategorie
from possum.base.category import Categorie
from possum.base.log import LogType
from django.contrib.auth import authenticate


def remplissage(nb,  caractere,  largeur):
    """caractere est le caractere de remplissage"""
    milieu = caractere
    # on ajoute len(milieu) a nb
    nb += 1
    while nb < largeur:
        milieu += caractere
        nb += 1
    return milieu


class Suivi(models.Model):
    """Suivi des etats"""
    facture = models.ForeignKey('base.Facture', related_name="suivi-facture")
    etat = models.ForeignKey('Etat', related_name="suivi-etat")
    date = models.DateTimeField('depuis le', auto_now_add=True)

    def __unicode__(self):
        return "Facture %s : etat %s" % (self.facture, self.etat.nom)


class Facture(models.Model):
    date_creation = models.DateTimeField('creer le', auto_now_add=True)
    table = models.ForeignKey('Table', \
            null=True, blank=True, \
            related_name="facture-table")
    couverts = models.PositiveIntegerField("nombre de couverts", default=0)
    produits = models.ManyToManyField('ProduitVendu', \
        related_name="les produits vendus", \
        limit_choices_to = {'date__gt': datetime.datetime.today()})
    total_ttc = models.DecimalField(max_digits=9, decimal_places=2, 
            default=0)
    paiements = models.ManyToManyField('Paiement',
        related_name="les paiements",
        limit_choices_to = {'date__gt': datetime.datetime.today()})
    vats = models.ManyToManyField('VATOnBill',
        related_name="vat total for each vat on a bill")
    restant_a_payer = models.DecimalField(max_digits=9, decimal_places=2, 
            default=0)
    etats = models.ManyToManyField('Suivi', related_name="le suivi")
    saved_in_stats = models.BooleanField(default=False)
    onsite = models.BooleanField(default=True)

    class Meta:
        get_latest_by = 'id'
        permissions = (
            ("p1", "can modify users and permissions"),
            ("p2", "can play games"),
            ("p3", "can view all bills"),
            ("p4", "can modify all bills"),
            ("p5", "can use POS"),
            ("p6", "can modify la carte"),
            ("p7", "can view results"),
            ("p8", "can change music"),
            ("p9", "can modify music"),
        )

    def __unicode__(self):
        if self.id:
            id = self.id
        else:
            id = 0
        if self.date_creation:
#            print self.date_creation
#            date = self.date_creation.strftime("%Y/%m/%d %H:%M")
            date = self.date_creation.strftime("%H:%M %d/%m")
        else:
            date = "--:-- --/--"
        return u"%s F%06d" % (date, id)

    def __cmp__(self, other):
        """
            Les factures sont triees par date_creation.
            D'abord les plus récentes, puis les plus vielles.
        """
        return cmp(self.date_creation, other.date_creation)

    def guest_couverts(self):
        """Essaye de deviner le nombre de couverts"""
        nb = {}
        categories = ["Entrees", "Plats"]
        for categorie in categories:
            nb[categorie] = 0
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.nom in categories:
                nb[vendu.produit.categorie.nom] += 1
            for sous_produit in vendu.contient.iterator():
                if sous_produit.produit.categorie.nom in categories:
                    nb[sous_produit.produit.categorie.nom] += 1
        return max(nb.values())

    def set_couverts(self, nb):
        """Change le nombre de couvert"""
        self.couverts = nb
        self.save()

    def set_table(self, table):
        """Change la table de la facture
        On prend en compte le changement de tarification si changement
        de zone.

        On ne traite pas le cas ou les 2 tables sont surtaxées à des montants
        différents.
        """
        if self.est_surtaxe():
            if not table.zone.surtaxe:
                # la nouvelle table n'est pas surtaxée
                self.remove_surtaxe()
            self.table = table
            self.save()
        else:
            self.table = table
            self.save()
            if table.zone.surtaxe:
                # la nouvelle table est surtaxée
                self.add_surtaxe()

    def nb_soldee_jour(self, date):
        """Nombre de facture soldee le jour 'date'"""
        if date.hour > 5:
            date_min = datetime.datetime(date.year, date.month, date.day, 5)
        else:
            tmp = date - datetime.timedelta(days=1)
            date_min = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        return Facture.objects.filter(date_creation__gt=date_min, \
                                        date_creation__lt=date_max, \
                                        restant_a_payer=0).exclude( \
                                        produits__isnull=True).count()

    def non_soldees(self):
        """Retourne la liste des factures non soldees"""
        liste = []
        for i in Facture.objects.exclude(restant_a_payer=0).iterator():
            liste.append(i)
        for i in Facture.objects.filter(produits__isnull=True).iterator():
            liste.append(i)
        return liste

    def compute_total(self):
        self.total_ttc = Decimal("0")
        self.restant_a_payer = Decimal("0")
        for v in self.vats.all():
            v.total = 0
            v.save()
        for product in self.produits.all():
            self.add_product_prize(product)
        for payment in self.paiements.all():
            self.restant_a_payer -= payment.montant
        self.save()

    def get_vat(self, product):
        if self.onsite:
            vat = product.produit.categorie.vat_onsite
        else:
            vat = product.produit.categorie.vat_takeaway
        return vat

    def get_product_prize(self, product):
        """Return a TTC prize of a product.
        """
        vat = self.get_vat(product)
        if vat:
            return "%.2f" % vat.get_ttc_for(product.prix)
        else:
            return "0"

    def add_product_prize(self, product):
        """Ajout le prix HT d'un ProduitVendu sur la facture."""
        vat = self.get_vat(product)
        if vat:
            ttc = vat.get_ttc_for(product.prix)
            self.total_ttc += ttc
            self.restant_a_payer += ttc
            self.save()
            vatonbill, created = self.vats.get_or_create(vat=vat)
            vatonbill.total += vat.get_tax_for(product.prix)
            vatonbill.save()

    def del_product_prize(self, product):
        vat = self.get_vat(product)
        if vat:
            ttc = vat.get_ttc_for(product.prix)
            self.total_ttc -= ttc
            self.restant_a_payer -= ttc
            self.save()
            vatonbill, created = self.vats.get_or_create(vat=vat)
            vatonbill.total -= vat.get_tax_for(product.prix)
            vatonbill.save()

    def add_surtaxe(self):
        """Add surtaxe on all needed products
        """
        for product in self.produits.filter(produit__categorie__surtaxable=True):
            product.prix += self.table.zone.prix_surtaxe
            product.save()
        self.compute_total()

    def remove_surtaxe(self):
        """Remove surtaxe on all needed products
        """
        for product in self.produits.filter(produit__categorie__surtaxable=True):
            product.prix -= self.table.zone.prix_surtaxe
            product.save()
        self.compute_total()

    def add_product(self, vendu):
        """Ajout d'un produit à la facture.
        Si c'est le premier produit alors on modifie la date de creation
        """
        if self.produits.count() == 0:
            self.date_creation = datetime.datetime.now()

        vendu.prix = vendu.produit.prix
        vendu.save()
        if vendu.prix:
            self.produits.add(vendu)
            self.save()
            if self.est_surtaxe():
                if vendu.produit.categorie.disable_surtaxe:
                    # on doit enlever la surtaxe pour tous les produits
                    # concernés
                    self.remove_surtaxe()
                else:
                    if vendu.produit.categorie.surtaxable:
                        vendu.prix += self.table.zone.prix_surtaxe
                        vendu.save()
                    self.add_product_prize(vendu)
            else:
                self.add_product_prize(vendu)

#        else:
#            # on a certainement a faire a une reduction
#            # -10%
#            if vendu.produit.nom == "Remise -10%":
#                vendu.prix = self.get_montant() / Decimal("-10")
#                vendu.save()
#                logging.debug("la remise est de: %s" % vendu.prix)
#                self.produits.add(vendu)
#                self.restant_a_payer += vendu.prix
#                self.montant_normal += vendu.prix
#            else:
#                logging.debug("cette remise n'est pas connue")
        #self.produits.order_by('produit')
#        self.save()

    def del_product(self, product):
        """On enleve un produit à la facture.

        Si le montant est négatif après le retrait d'un élèment,
        c'est qu'il reste certainement une remise, dans
        ce cas on enlève tous les produits.
        """
        if product in self.produits.all():
            surtaxe = self.est_surtaxe()
            self.produits.remove(product)
            if surtaxe != self.est_surtaxe():
                self.compute_total()
            else:
                self.del_product_prize(product)
        else:
            logging.warning("[%s] on essaye de supprimer un produit "\
                            "qui n'est pas dans la facture" % self)

    def del_all_payments(self):
        """On supprime tous les paiements"""
        if self.paiements.count():
            for paiement in self.paiements.iterator():
                paiement.delete()
            self.paiements.clear()
            self.restant_a_payer = self.total_ttc
            self.save()

    def del_payment(self, payment):
        """On supprime un paiement"""
        if payment in self.paiements.all():
            self.paiements.remove(payment)
            payment.delete()
            self.save()
            self.compute_total()
        else:
            logging.warning("[%s] on essaye de supprimer un paiement "\
                            "qui n'est pas dans la facture: %s %s %s %s"\
                            % (self, payment.id, payment.date,\
                            payment.type.nom, payment.montant))

    def get_users(self):
        """Donne la liste des noms d'utilisateurs"""
        users = []
        for user in User.objects.order_by('username').iterator():
            if user.is_active:
                users.append(user.username)
        return users

    def get_last_connected(self):
        try:
            return User.objects.order_by('last_login')[0].username
        except:
            return "aucun utilisateur"

    def authenticate(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.groups.filter(name='Managers').count() == 1:
                return True
            else:
                logging.debug("utilisateur non authorise: %s" % username)
                return False
        else:
            logging.debug("erreur avec: %s / %s" % (username, password))
            return False

    def getTvaNormal(self):
        """
            calcul la TVA
            On arrondi seulement à 1 parce que les 2 décimals sont dans la partie entière du montant
            # la TVA est sur le HT !!
        """
        #return self.montant_normal - ((self.montant_normal*100)/Decimal("105.5"))
        return self.montant_normal * (Decimal("0.055") / Decimal("1.055"))

    def getTvaAlcool(self):
        #return self.montant_alcool - ((self.montant_alcool*100)/Decimal("119.6"))
        return self.montant_alcool * (Decimal("0.196") / Decimal("1.196"))

    def get_resume(self):
        return "%s %s %d" % (self.table.nom, self.date_creation, self.montant)

    def get_montant(self):
        return self.montant_normal + self.montant_alcool

    def add_payment(self, type_payment, montant, valeur_unitaire="1.0"):
        """
        type_payment est un TypePaiement
        montant et valeur_unitaire sont des chaines de caracteres
        qui seront converti en Decimal

        Si le montant est superieur au restant du alors on rembourse en
        espece.
        """
        logging.debug("Nouveau paiement")
        if self.restant_a_payer <= Decimal("0"):
            logging.info("[%s] nouveau paiement ignore car restant"\
                            " a payer <= 0 (%5.2f)"
                            % (self, self.restant_a_payer))
            return False

        paiement = Paiement()
        paiement.type = type_payment
        paiement.valeur_unitaire = Decimal(valeur_unitaire)
        if self.produits:
            # le montant est-il indique ?
            if float(montant) == 0.0:
                return False
            else:
                # le montant est indique
                if type_payment.fixed_value:
                    # dans ce cas le montant est le nombre de ticket
                    paiement.nb_tickets = int(montant)
                    paiement.montant = paiement.nb_tickets * paiement.valeur_unitaire
                else:
                    paiement.montant = Decimal(montant)
                # on enregistre ce paiement
                paiement.save()
                self.paiements.add(paiement)
            # regularisation si le montant est superieur au montant du
            if paiement.montant > self.restant_a_payer:
                monnaie = Paiement()
                monnaie.type = PaiementType.objects.get(nom="Espece")
                monnaie.montant = self.restant_a_payer - paiement.montant
                monnaie.save()
                self.paiements.add(monnaie)
                self.restant_a_payer -= monnaie.montant
            self.restant_a_payer -= paiement.montant
            self.save()
            return True
        else:
            logging.debug("pas de produit, donc rien n'a payer")
            return False

    def total(self):
        return self.montant_alcool + self.montant_normal

    def est_soldee(self):
        """La facture a été utilisée et soldée"""
        if self.restant_a_payer == 0 and self.produits.count() > 0:
            return True
        else:
            return False

    def est_un_repas(self):
        """Est ce que la facture contient un element compris dans les
        categories entrees, plats, desserts ou formules
        """
        for vendu in self.produits.iterator():
            if vendu.produit.categorie.nom in ["Entrees", "Plats", "Formules"]:
                return True
        return False

    def est_vierge(self):
        """La facture est vierge"""
        if self.restant_a_payer == 0 and self.produits.count() == 0:
            return True
        else:
            return False

    def est_surtaxe(self):
        """
        Table is surtaxed et il n'y a pas de nourriture.
        """
        if self.onsite:
            for produit in self.produits.all():
                #logging.debug("test with produit: %s and categorie id: %d" % (produit.nom, produit.categorie.id))
                if produit.produit.categorie.disable_surtaxe:
                    #logging.debug("pas de surtaxe")
                    return False
            if self.table:
                return self.table.est_surtaxe()
            else:
                return False
        else:
            return False

    def check_path(self, path):
        """Verifie l'existance du chemin et cree le repertoire si besoin
        '"""
        path_splitted = path.split("/")
        for i in xrange(len(path_splitted)):
            if path_splitted[i]:
                tmp = "/".join(path_splitted[:i+1])
                if not os.path.exists(tmp):
                    os.mkdir(tmp)

    def rapport_mois(self, mois):
        """Retourne dans une liste le rapport du mois 'mois'
        'mois' est de type datetime.today()

        exemple:

        -- CA mensuel 12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        """
        logging.debug(mois)
        date_min = datetime.datetime(mois.year, mois.month, 1, 5)
        # on est le mois suivant (32 c'est pour etre sur de ne pas
        # tomber sur le 31 du mois)
        tmp = date_min + datetime.timedelta(days=32)
        # modulo pour le cas de decembre + 1 = janvier
        date_max = datetime.datetime(tmp.year, tmp.month, 1, 5)
        texte = []
        texte.append("    -- CA mensuel %s --" % mois.strftime("%m/%Y"))
        selection = StatsJourPaiement.objects.filter( \
                            date__gte=date_min, \
                            date__lt=date_max)
        for paiement in PaiementType.objects.iterator():
            total = selection.filter(paiement=paiement).aggregate(Sum('valeur'))['valeur__sum']
            if total > 0:
                texte.append("%-20s %10.2f" % (paiement.nom, total))
        selection = StatsJourGeneral.objects.filter( \
                            date__gte=date_min, \
                            date__lt=date_max)
        ca = selection.filter(type=LogType.objects.get(nom="ca")).aggregate(Sum('valeur'))['valeur__sum']
        if ca == None:
            ca = 0.0

        # IMPORTANT:
        #   ici on ne se sert pas des stats 'tva_normal' et 'tva_alcool'
        #   car il y a des erreurs d'arrondies à cause des additions
        #   successives
        montant_normal = selection.filter(type=LogType.objects.get(nom="montant_normal")).aggregate(Sum('valeur'))['valeur__sum']
        if montant_normal == None:
            tva_normal = 0.0
        else:
            tva_normal = montant_normal*(Decimal("0.055") / Decimal("1.055"))
        montant_alcool = selection.filter(type=LogType.objects.get(nom="montant_alcool")).aggregate(Sum('valeur'))['valeur__sum']
        if montant_alcool == None:
            tva_alcool = 0.0
        else:
            tva_alcool = montant_alcool*(Decimal("0.196") / Decimal("1.196"))

        texte.append("%-20s %10.2f" % ("total TTC:", ca))
        texte.append("%-20s %10.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %10.2f" % ("total TVA 19.6:", tva_alcool))
        return texte

    def rapport_mois_old(self, mois):
        """Retourne dans une liste le rapport du mois 'mois'
        'mois' est de type datetime.today()

        exemple:

        -- CA mensuel 12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        """
        date_min = datetime.datetime(mois.year, mois.month, 1, 5)
        # on est le mois suivant (32 c'est pour etre sur de ne pas
        # tomber sur le 31 du mois)
        tmp = date_min + datetime.timedelta(days=32)
        # modulo pour le cas de decembre + 1 = janvier
        date_max = datetime.datetime(tmp.year, tmp.month, 1, 5)
        total = Decimal("0")
        tva_normal = Decimal("0")
        tva_alcool = Decimal("0")
        paiements = {}
        for p in PaiementType.objects.iterator():
            paiements[p.nom] = Decimal("0")
        #nb_f = 0
        for f in Facture.objects.filter( \
                            date_creation__gt=date_min, \
                            date_creation__lt=date_max).iterator():
            if f.est_soldee():
                #nb_f += 1
                for p in f.paiements.iterator():
                    paiements[p.type.nom] += p.montant
                total += f.get_montant()
                tva_normal += f.getTvaNormal()
                tva_alcool += f.getTvaAlcool()
                #print "nb facture: %d" % nb_f
                #print "total: %s" % total
        # enregistrement
        #self.check_path(settings.PATH_TICKET)
        #filename = "%s/%s" % (settings.PATH_TICKET, \
        #                        mois.strftime("mois-%Y%m"))
        #fd = open(filename, "w")
        texte = []
        #fd.write("    -- CA mensuel %s --\n" % mois.strftime("%m/%Y"))
        texte.append("    -- CA mensuel %s --" % mois.strftime("%m/%Y"))
        for p in PaiementType.objects.iterator():
            if paiements[p.nom]:
                texte.append("%-20s %10.2f" % (p.nom, paiements[p.nom]))
                #fd.write("%-20s %10.2f\n" % (p.nom, paiements[p.nom]))
        texte.append("%-20s %10.2f" % ("total TTC:", total))
        texte.append("%-20s %10.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %10.2f" % ("total TVA 19.6:", tva_alcool))
        #fd.write("%-20s %10.2f\n" % ("total TTC:", total))
        #fd.write("%-20s %10.2f\n" % ("total TVA  5.5:", tva_normal))
        #fd.write("%-20s %10.2f\n" % ("total TVA 19.6:", tva_alcool))
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.close()
        #return filename
        return texte

    def get_factures_du_jour(self, date):
        """Retourne la liste des factures soldees du jour 'date'"""
        date_min = datetime.datetime(date.year, date.month, date.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        return Facture.objects.filter( \
                                      date_creation__gt=date_min, \
                                      date_creation__lt=date_max, \
                                      restant_a_payer = 0).exclude(\
                                      produits__isnull = True)

    def rapport_jour(self, date):
        """Retourne le rapport du jour sous la forme d'une liste
        'jour' est de type datetime.today()

        exemple:
        -- 15/12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        Menu E/P :            16
        Menu P/D :            16
        Menu Tradition :      16

        Salade cesar :         6
        ...

        plat ...
        """
        logging.debug(date)
        texte = []
        if date == None:
            logging.warning("la date fournie est inconnue")
            return texte
        stats = StatsJourGeneral()
        texte.append("       -- %s --" % date.strftime("%d/%m/%Y"))
        texte.append("CA TTC (% 4d fact.): %11.2f" % (
                                    stats.get_data("nb_factures", date),
                                    stats.get_data("ca", date)))
        # IMPORTANT:
        #   ici on ne se sert pas des stats 'tva_normal' et 'tva_alcool'
        #   car il y a des erreurs d'arrondies à cause des additions
        #   successives
        tva_normal = stats.get_data("montant_normal", date)*(Decimal("0.055") / Decimal("1.055"))
        texte.append("%-20s %11.2f" % ("total TVA  5.5:", tva_normal))
        tva_alcool = stats.get_data("montant_alcool", date)*(Decimal("0.196") / Decimal("1.196"))
        texte.append("%-20s %11.2f" % ("total TVA 19.6:", tva_alcool))
        for stats in StatsJourPaiement.objects.filter(date=date)\
                                              .order_by("paiement")\
                                              .iterator():
            texte.append("%-15s (%d) %11.2f" % (stats.paiement.nom,
                                                stats.nb,
                                                stats.valeur))
        texte.append(" ")
        for cate in ["Formules", "Entrees", "Plats", "Desserts"]:
            try:
                categorie = Categorie.objects.get(nom=cate)
                stats = StatsJourCategorie.objects.get(date=date,
                                                    categorie=categorie)
                texte.append("%-21s %10d" % (cate, stats.nb))
                for stats in StatsJourProduit.objects.filter(date=date, produit__categorie=categorie).order_by("produit").iterator():
                    texte.append(" %-20s %10d" % (stats.produit.nom, stats.nb))
                texte.append(" ")
            except StatsJourCategorie.DoesNotExist:
                continue
        return texte

    def rapport_jour_old(self, date):
        """Retourne le rapport du jour sous la forme d'une liste
        'jour' est de type datetime.today()

        exemple:
        -- 15/12/2010 --
        Cheque               285,05
        Ticket Resto         723,67
        Espece              3876,46
        ANCV                 150,00
        CB                  3355,60
        total TTC:          8386,08
        montant TVA  5,5:    353,26
        montant TVA 19,6:    263,82

        Menu E/P :            16
        Menu P/D :            16
        Menu Tradition :      16

        Salade cesar :         6
        ...

        plat ...
        """
        logging.debug(date)
        date_min = datetime.datetime(date.year, date.month, date.day, 5)
        tmp = date_min + datetime.timedelta(days=1)
        date_max = datetime.datetime(tmp.year, tmp.month, tmp.day, 5)
        total = Decimal("0")
        tva_normal = Decimal("0")
        tva_alcool = Decimal("0")
        nb_plats = {}
        categories = ["Formules", "Entrees", "Plats", "Desserts"]
        for cate in categories:
            nb_plats[cate] = {}
            nb_plats[cate]['total'] = 0
        paiements = {}
        for p in PaiementType.objects.iterator():
            paiements[p.nom] = Decimal("0")
        nb_factures = 0
        for f in Facture.objects.filter( \
                            date_creation__gt=date_min, \
                            date_creation__lt=date_max).iterator():
            if f.est_soldee():
                nb_factures += 1
                for p in f.paiements.iterator():
                    paiements[p.type.nom] += p.montant
                for p in f.produits.iterator():
                    nom = p.produit.categorie.nom
                    if nom in categories:
                        if p.produit.nom in nb_plats[nom]:
                            nb_plats[nom][p.produit.nom] += 1
                        else:
                            nb_plats[nom][p.produit.nom] = 1
                        nb_plats[nom]['total'] += 1
                total += f.get_montant()
                tva_normal += f.getTvaNormal()
                tva_alcool += f.getTvaAlcool()
        # enregistrement
        #self.check_path(settings.PATH_TICKET)
        #filename = "%s/%s" % (settings.PATH_TICKET, \
        #                        date.strftime("jour-%Y%m%d"))
        #fd = open(filename, "w")
        texte = []
        #fd.write("       -- %s --\n" % date.strftime("%d/%m/%Y"))
        #fd.write("CA TTC (% 4d fact.): %11.2f\n" % (nb_factures, total))
        #fd.write("%-20s %11.2f\n" % ("total TVA  5.5:", tva_normal))
        #fd.write("%-20s %11.2f\n" % ("total TVA 19.6:", tva_alcool))
        texte.append("       -- %s --" % date.strftime("%d/%m/%Y"))
        texte.append("CA TTC (% 4d fact.): %11.2f" % (nb_factures, total))
        texte.append("%-20s %11.2f" % ("total TVA  5.5:", tva_normal))
        texte.append("%-20s %11.2f" % ("total TVA 19.6:", tva_alcool))
        for p in PaiementType.objects.iterator():
            if paiements[p.nom]:
                #fd.write("%-20s %11.2f\n" % (p.nom, paiements[p.nom]))
                texte.append("%-20s %11.2f" % (p.nom, paiements[p.nom]))
        for cate in categories:
            if nb_plats[cate]:
                if nb_plats[cate]['total'] > 0:
#                    fd.write("%-21s %10d\n" % (cate, nb_plats[cate]['total']))
                    texte.append("%-21s %10d" % (cate, nb_plats[cate]['total']))
                    for p in nb_plats[cate]:
                        if p != "total":
                            texte.append(" %-20s %10d" % (p, nb_plats[cate][p]))
#                            fd.write(" %-20s %10d\n" % (p, nb_plats[cate][p]))
#        fd.write("\n")
#        fd.write("\n")
#        fd.write("\n")
#        fd.write("\n")
#        fd.write("\n")
#        fd.close()
#        return filename
        return texte

    def get_working_date(self):
        """Retourne la journee de travail officiel
        (qui fini a 5h du matin)"""
        tmp = self.date_creation
        if tmp:
            if tmp.hour < 5:
                # jour de travail precedent
                return tmp - datetime.timedelta(days=1)
            else:
                return tmp
        else:
            logging.warning("la facture n'a pas de date_creation")
            return None

    def maj_stats_avec_nouvelles_factures(self):
        """Calcule les stats pour toutes les nouvelles factures
        soldées."""
        selection = Facture.objects.filter(saved_in_stats=False)
        logging.info("parcours des factures")
        for facture in selection.iterator():
            facture.maj_stats()


    def maj_stats(self):
        """Calcule les statistiques pour cette facture
        si elle est soldée"""
        try:
            nb_factures = LogType.objects.get(nom="nb_factures")
            nb_couverts = LogType.objects.get(nom="nb_couverts")
            nb_bar = LogType.objects.get(nom="nb_bar")
            ca = LogType.objects.get(nom="ca")
            tva_alcool = LogType.objects.get(nom="tva_alcool")
            tva_normal = LogType.objects.get(nom="tva_normal")
            montant_alcool = LogType.objects.get(nom="montant_alcool")
            montant_normal = LogType.objects.get(nom="montant_normal")
            ca_resto = LogType.objects.get(nom="ca_resto")
            ca_bar = LogType.objects.get(nom="ca_bar")
            tm_bar = LogType.objects.get(nom="tm_bar")
            tm_resto = LogType.objects.get(nom="tm_resto")
        except LogType.DoesNotExist:
            logging.warning("il manque un type, abandon")
            return

        if self.est_soldee():
            date = self.get_working_date()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=nb_factures)[0]
            stats.valeur += 1
            stats.save()
            tmp_montant = self.get_montant()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=ca)[0]
            stats.valeur += tmp_montant
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=tva_alcool)[0]
            stats.valeur += self.getTvaAlcool()
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=tva_normal)[0]
            stats.valeur += self.getTvaNormal()
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=montant_alcool)[0]
            stats.valeur += self.montant_alcool
            stats.save()
            stats = StatsJourGeneral.objects.get_or_create(date=date, type=montant_normal)[0]
            stats.valeur += self.montant_normal
            stats.save()
            if self.est_un_repas():
                # nb_couverts
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=nb_couverts)[0]
                if self.couverts == 0:
                    self.couverts = self.guest_couverts()
                    self.save()
                stats.valeur += self.couverts
                tmp_couverts = stats.valeur
                stats.save()
                # ca_resto
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=ca_resto)[0]
                stats.valeur += tmp_montant
                tmp_ca = stats.valeur
                stats.save()
                # tm_resto
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=tm_resto)[0]
                if tmp_couverts == 0:
                    stats.valeur = 0
                else:
                    stats.valeur = tmp_ca / tmp_couverts
                stats.save()
            else:
                # nb_bar
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=nb_bar)[0]
                stats.valeur += 1
                tmp_couverts = stats.valeur
                stats.save()
                # ca_bar
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=ca_bar)[0]
                stats.valeur += tmp_montant
                tmp_ca = stats.valeur
                stats.save()
                # tm_bar
                stats = StatsJourGeneral.objects.get_or_create(date=date, type=tm_bar)[0]
                if tmp_couverts == 0:
                    stats.valeur = 0
                else:
                    stats.valeur = tmp_ca / tmp_couverts
                stats.save()
            for vendu in self.produits.iterator():
                # produit
                stats = StatsJourProduit.objects.get_or_create(date=date, produit=vendu.produit)[0]
                stats.valeur += vendu.prix
                stats.nb += 1
                stats.save()
                for sous_vendu in vendu.contient.iterator():
                    # il n'y a pas de CA donc on ne le compte pas
                    stats = StatsJourProduit.objects.get_or_create(date=date, produit=sous_vendu.produit)[0]
                    stats.nb += 1
                    stats.save()
                    # categorie
                    stats = StatsJourCategorie.objects.get_or_create(date=date, categorie=sous_vendu.produit.categorie)[0]
                    stats.nb += 1
                    stats.save()
                # categorie
                stats = StatsJourCategorie.objects.get_or_create(date=date, categorie=vendu.produit.categorie)[0]
                stats.valeur += vendu.prix
                stats.nb += 1
                stats.save()
            for paiement in self.paiements.iterator():
                stats = StatsJourPaiement.objects.get_or_create(date=date, paiement=paiement.type)[0]
                stats.valeur += paiement.montant
                if paiement.nb_tickets > 0:
                    stats.nb += paiement.nb_tickets
                else:
                    stats.nb += 1
                stats.save()
            self.saved_in_stats = True
            self.save()

    def ticket(self):
        """Retourne le ticket sous la forme d'une liste de ligne.
        """
        #self.check_path(settings.PATH_TICKET)
        #filename = "%s/%s" % (settings.PATH_TICKET, \
        #        self.date_creation.strftime("%Y%m%d%H%M%S"))
        #fd = open(filename, "w")
        texte = []
        #fd.write("           le Saint Saens\n")
        #fd.write("       -----------------------\n")
        #fd.write("       sarl Brasserie des Arts\n")
        #fd.write("       SIRET: 502 922 032 00011\n")
        #fd.write("        tel: 02.35.71.03.12\n")
        #fd.write("      120 rue du General Leclerc\n")
        #fd.write("             76000 Rouen\n")
        #fd.write("\n")
        texte.append("           le Saint Saens")
        texte.append("       -----------------------")
        texte.append("       sarl Brasserie des Arts")
        texte.append("       SIRET: 502 922 032 00011")
        texte.append("        tel: 02.35.71.03.12")
        texte.append("      120 rue du General Leclerc")
        texte.append("             76000 Rouen")
        texte.append(" ")
        if self.table != None:
            table = self.table
        else:
            table = "T--"
        #fd.write("%s - table: %s\n" % (self.date_creation.strftime("%d/%m/%Y %H:%M"), table))
        #fd.write("=======================================\n")
        texte.append("%s - table: %s" % (self.date_creation.strftime("%d/%m/%Y %H:%M"), table))
        texte.append("=======================================")
        for vendu in self.produits.order_by( \
                            "produit__categorie__priorite").iterator():
            #fd.write("  %s\n" % vendu.show())
            texte.append("  %s" % vendu.show())
        #fd.write("=======================================\n")
        texte.append("=======================================")
        if self.est_surtaxe():
            #fd.write("   Total (terrasse) : % 8.2f Euros\n" % self.total())
            texte.append("   Total (terrasse) : % 8.2f Euros" % self.total())
        else:
            #fd.write("   Total            : % 8.2f Euros\n" % self.total())
            texte.append("   Total            : % 8.2f Euros" % self.total())
        #fd.write("      dont TVA 5,5  : % 8.2f Euros\n" % self.getTvaNormal())
        #fd.write("      dont TVA 19,6 : % 8.2f Euros\n" % self.getTvaAlcool())
        #fd.write("=======================================\n")
        texte.append("      dont TVA 5,5  : % 8.2f Euros" % self.getTvaNormal())
        texte.append("      dont TVA 19,6 : % 8.2f Euros" % self.getTvaAlcool())
        texte.append("=======================================")
# il y a 70 tirets
#       fd.write("----------------------------------------------------------------------\n")
        #fd.write(" Service tous les jours de 7h a 22h30\n")
        #fd.write("   sauf le mardi soir, mercredi soir\n")
        #fd.write("          et le dimanche soir\n")
        #fd.write("\n")
        #fd.write("       - Merci de votre visite -\n")
        #fd.write("\n")
        texte.append(" Service tous les jours de 7h a 22h30")
        texte.append("   sauf le mardi soir, mercredi soir")
        texte.append("          et le dimanche soir")
        texte.append(" ")
        texte.append("       - Merci de votre visite -")
        texte.append(" ")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.write("\n")
        #fd.close()
        #return filename
        return texte

    def show(self):
        if self.table:
            table = self.table.nom
        else:
            table = "T--"
        if self.date_creation:
            date = self.date_creation.strftime("%H:%M:%S %d/%m/%y")
        else:
            date = "--:--:-- --/--/--"
        return "%s %s" % (table, date)

    def showPaiements(self):
        result = []
        for paiement in self.paiements.all():
            deb = "%s " % paiement.type.nom_facture
            if paiement.type.fixed_value:
                deb += "(%s x %.0f) " % (paiement.valeur_unitaire, paiement.nb_tickets)
            fin = " %.2f " % paiement.montant
            result.append(deb+remplissage(len(deb+fin), ".", 30)+fin)
        return result
