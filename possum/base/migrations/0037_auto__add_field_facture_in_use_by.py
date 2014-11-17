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

import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Facture.in_use_by'
        db.add_column(u'base_facture', 'in_use_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(
                          to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Facture.in_use_by'
        db.delete_column(u'base_facture', 'in_use_by_id')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': (
                'django.db.models.fields.CharField',
                [],
                {'unique': 'True',
                 'max_length': '80'}),
            'permissions': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'to': u"orm['auth.Permission']",
                 'symmetrical': 'False',
                 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {
                'ordering':
                "(u'content_type__app_label', u'content_type__model', u'codename')",
                'unique_together': "((u'content_type', u'codename'),)",
                'object_name': 'Permission'},
            'codename': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '100'}),
            'content_type': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': (
                'django.db.models.fields.DateTimeField',
                [],
                {'default': 'datetime.datetime.now'}),
            'email': (
                'django.db.models.fields.EmailField',
                [],
                {'max_length': '75',
                 'blank': 'True'}),
            'first_name': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '30',
                 'blank': 'True'}),
            'groups': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'to': u"orm['auth.Group']",
                 'symmetrical': 'False',
                 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'True'}),
            'is_staff': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'is_superuser': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'last_login': (
                'django.db.models.fields.DateTimeField',
                [],
                {'default': 'datetime.datetime.now'}),
            'last_name': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '30',
                 'blank': 'True'}),
            'password': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '128'}),
            'user_permissions': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'to': u"orm['auth.Permission']",
                 'symmetrical': 'False',
                 'blank': 'True'}),
            'username': (
                'django.db.models.fields.CharField',
                [],
                {'unique': 'True',
                 'max_length': '30'})
        },
        'base.categorie': {
            'Meta': {'ordering': "['priorite']", 'object_name': 'Categorie'},
            'color': (
                'django.db.models.fields.CharField',
                [],
                {'default': "'#ffdd82'",
                 'max_length': '8'}),
            'disable_surtaxe': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_in_kitchen': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'nom': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '60'}),
            'priorite': (
                'django.db.models.fields.PositiveIntegerField',
                [],
                {'default': '0'}),
            'surtaxable': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'vat_onsite': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'blank': 'True',
                 'related_name': "'categorie-vat-onsite'",
                 'null': 'True',
                 'to': "orm['base.VAT']"}),
            'vat_takeaway': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'blank': 'True',
                 'related_name': "'categorie-vat-takeaway'",
                 'null': 'True',
                 'to': "orm['base.VAT']"})
        },
        'base.config': {
            'Meta': {'ordering': "['key']", 'object_name': 'Config'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '32'}),
            'value': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '64'})
        },
        'base.cuisson': {
            'Meta': {'object_name': 'Cuisson'},
            'color': (
                'django.db.models.fields.CharField',
                [],
                {'default': "'#ffdd82'",
                 'max_length': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '60'}),
            'nom_facture': (
                'django.db.models.fields.CharField',
                [],
                {'default': "''",
                 'max_length': '35'}),
            'priorite': (
                'django.db.models.fields.PositiveIntegerField',
                [],
                {'default': '0'})
        },
        'base.dailystat': {
            'Meta': {'object_name': 'DailyStat'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '32'}),
            'value': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'})
        },
        'base.facture': {
            'Meta': {'object_name': 'Facture'},
            'category_to_follow': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'to': "orm['base.Categorie']",
                 'null': 'True',
                 'blank': 'True'}),
            'couverts': (
                'django.db.models.fields.PositiveIntegerField',
                [],
                {'default': '0'}),
            'date_creation': (
                'django.db.models.fields.DateTimeField',
                [],
                {'auto_now_add': 'True',
                 'blank': 'True'}),
            'following': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'symmetrical': 'False',
                 'to': "orm['base.Follow']",
                 'null': 'True',
                 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_use_by': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'to': u"orm['auth.User']",
                 'null': 'True',
                 'blank': 'True'}),
            'onsite': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'True'}),
            'paiements': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'related_name': "'les paiements'",
                 'symmetrical': 'False',
                 'to': "orm['base.Paiement']"}),
            'produits': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'related_name': "'les produits vendus'",
                 'symmetrical': 'False',
                 'to': "orm['base.ProduitVendu']"}),
            'restant_a_payer': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'}),
            'saved_in_stats': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'surcharge': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'table': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'blank': 'True',
                 'related_name': "'facture-table'",
                 'null': 'True',
                 'to': "orm['base.Table']"}),
            'total_ttc': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'}),
            'vats': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'related_name': "'vat total for each vat on a bill'",
                 'symmetrical': 'False',
                 'to': "orm['base.VATOnBill']"})
        },
        'base.follow': {
            'Meta': {'ordering': "['date']", 'object_name': 'Follow'},
            'category': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'to': "orm['base.Categorie']"}),
            'date': (
                'django.db.models.fields.DateTimeField',
                [],
                {'auto_now_add': 'True',
                 'blank': 'True'}),
            'done': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produits': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'related_name': "'les produits envoyes'",
                 'symmetrical': 'False',
                 'to': "orm['base.ProduitVendu']"})
        },
        'base.monthlystat': {
            'Meta': {
                'ordering': "['year', 'month']",
                'object_name': 'MonthlyStat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '32'}),
            'month':
            ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'value': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'}),
            'year':
            ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'base.note': {
            'Meta': {'ordering': "['message']", 'object_name': 'Note'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': (
                'django.db.models.fields.CharField',
                [],
                {'default': "''",
                 'max_length': '35'})
        },
        'base.option': {
            'Meta': {'ordering': "['name']", 'object_name': 'Option'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': (
                'django.db.models.fields.CharField',
                [],
                {'default': "''",
                 'max_length': '16'})
        },
        'base.paiement': {
            'Meta': {'object_name': 'Paiement'},
            'date': (
                'django.db.models.fields.DateTimeField',
                [],
                {'auto_now_add': 'True',
                 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'montant': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'}),
            'nb_tickets': (
                'django.db.models.fields.PositiveIntegerField',
                [],
                {'default': '0'}),
            'type': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'related_name': "'paiement-type'",
                 'to': "orm['base.PaiementType']"}),
            'valeur_unitaire': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '1',
                 'max_digits': '9',
                 'decimal_places': '2'})
        },
        'base.paiementtype': {
            'Meta': {'ordering': "['nom']", 'object_name': 'PaiementType'},
            'fixed_value': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '60'})
        },
        'base.printer': {
            'Meta': {'object_name': 'Printer'},
            'billing': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'footer': (
                'django.db.models.fields.TextField',
                [],
                {'default': "''"}),
            'header': (
                'django.db.models.fields.TextField',
                [],
                {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kitchen': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'manager': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            'name': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '40'}),
            'options': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '120'}),
            'width': (
                'django.db.models.fields.PositiveIntegerField',
                [],
                {'default': '27'})
        },
        'base.produit': {
            'Meta': {
                'ordering': "['categorie', 'nom']",
                'object_name': 'Produit'},
            'actif': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'True'}),
            'categorie': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'related_name': "'produit-categorie'",
                 'to': "orm['base.Categorie']"}),
            'categories_ok': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'to': "orm['base.Categorie']",
                 'symmetrical': 'False'}),
            'choix_cuisson': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '60'}),
            'options_ok': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'symmetrical': 'False',
                 'to': "orm['base.Option']",
                 'null': 'True',
                 'blank': 'True'}),
            'price_surcharged': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '7',
                 'decimal_places': '2'}),
            'prix': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '7',
                 'decimal_places': '2'}),
            'produits_ok': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'related_name': "'produits_ok_rel_+'",
                 'to': "orm['base.Produit']"}),
            'vat_onsite': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '7',
                 'decimal_places': '2'}),
            'vat_surcharged': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '7',
                 'decimal_places': '2'}),
            'vat_takeaway': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '7',
                 'decimal_places': '2'})
        },
        'base.produitvendu': {
            'Meta': {'ordering': "['produit']", 'object_name': 'ProduitVendu'},
            'contient': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'related_name': "'contient_rel_+'",
                 'to': "orm['base.ProduitVendu']"}),
            'cuisson': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'blank': 'True',
                 'related_name': "'produitvendu-cuisson'",
                 'null': 'True',
                 'to': "orm['base.Cuisson']"}),
            'date': (
                'django.db.models.fields.DateTimeField',
                [],
                {'auto_now_add': 'True',
                 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_with': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'related_name': "'produit-kitchen'",
                 'null': 'True',
                 'to': "orm['base.Categorie']"}),
            'notes': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'symmetrical': 'False',
                 'to': "orm['base.Note']",
                 'null': 'True',
                 'blank': 'True'}),
            'options': (
                'django.db.models.fields.related.ManyToManyField',
                [],
                {'symmetrical': 'False',
                 'to': "orm['base.Option']",
                 'null': 'True',
                 'blank': 'True'}),
            'prix': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '7',
                 'decimal_places': '2'}),
            'produit': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'related_name': "'produitvendu-produit'",
                 'to': "orm['base.Produit']"}),
            'sent': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'})
        },
        'base.table': {
            'Meta': {'object_name': 'Table'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '60'}),
            'zone': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'related_name': "'table-zone'",
                 'to': "orm['base.Zone']"})
        },
        'base.vat': {
            'Meta': {'ordering': "['name']", 'object_name': 'VAT'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '32'}),
            'tax': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '4',
                 'decimal_places': '2'}),
            'value': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '6',
                 'decimal_places': '4'})
        },
        'base.vatonbill': {
            'Meta': {'object_name': 'VATOnBill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'}),
            'vat': (
                'django.db.models.fields.related.ForeignKey',
                [],
                {'related_name': "'bill-vat'",
                 'to': "orm['base.VAT']"})
        },
        'base.weeklystat': {
            'Meta': {
                'ordering': "['year', 'week']",
                'object_name': 'WeeklyStat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '32'}),
            'value': (
                'django.db.models.fields.DecimalField',
                [],
                {'default': '0',
                 'max_digits': '9',
                 'decimal_places': '2'}),
            'week':
            ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'year':
            ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'base.zone': {
            'Meta': {'object_name': 'Zone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nom': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '60'}),
            'surtaxe': (
                'django.db.models.fields.BooleanField',
                [],
                {'default': 'False'})
        },
        u'contenttypes.contenttype': {
            'Meta': {
                'ordering': "('name',)",
                'unique_together': "(('app_label', 'model'),)",
                'object_name': 'ContentType',
                'db_table': "'django_content_type'"},
            'app_label': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '100'}),
            'name': (
                'django.db.models.fields.CharField',
                [],
                {'max_length': '100'})
        }
    }

    complete_apps = ['base']
