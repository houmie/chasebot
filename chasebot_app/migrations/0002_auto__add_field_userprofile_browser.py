# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserProfile.browser'
        db.add_column('chasebot_app_userprofile', 'browser',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserProfile.browser'
        db.delete_column('chasebot_app_userprofile', 'browser')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'chasebot_app.company': {
            'Meta': {'object_name': 'Company'},
            'company_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'chasebot_app.contact': {
            'Meta': {'object_name': 'Contact'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'children_names': ('django.db.models.fields.CharField', [], {'max_length': '75', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Company']"}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'contact_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contacts_interests': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'blank': 'True'}),
            'dear_name': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'fax_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'home_town': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'important_client': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'marital_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.MaritalStatus']", 'null': 'True', 'blank': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'pet_names': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'prev_meeting_places': ('django.db.models.fields.TextField', [], {'max_length': '50', 'blank': 'True'}),
            'referred_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'spouse_first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'spouse_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'spouses_interests': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        'chasebot_app.conversation': {
            'Meta': {'object_name': 'Conversation'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Contact']"}),
            'conversation_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'chasebot_app.currency': {
            'Meta': {'object_name': 'Currency'},
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'chasebot_app.deal': {
            'Meta': {'object_name': 'Deal'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Company']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Contact']"}),
            'conversation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Conversation']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Currency']"}),
            'deal_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'deal_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deal_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'deal_instance_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'deal_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.DealTemplate']", 'null': 'True', 'blank': 'True'}),
            'deal_template_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'sales_item': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['chasebot_app.SalesItem']", 'symmetrical': 'False'}),
            'sales_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.SalesTerm']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.DealStatus']", 'null': 'True', 'blank': 'True'}),
            'total_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'})
        },
        'chasebot_app.dealstatus': {
            'Meta': {'object_name': 'DealStatus'},
            'deal_status': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'deal_status_en': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'deal_status_en_gb': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'chasebot_app.dealtemplate': {
            'Meta': {'object_name': 'DealTemplate'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Company']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Currency']"}),
            'deal_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'deal_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'sales_item': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['chasebot_app.SalesItem']", 'symmetrical': 'False'}),
            'sales_term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.SalesTerm']"})
        },
        'chasebot_app.event': {
            'Meta': {'object_name': 'Event'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Company']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Contact']"}),
            'deal_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'due_date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reminder_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reminder': ('django.db.models.fields.CharField', [], {'default': "'15m'", 'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'reminder_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'call'", 'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'chasebot_app.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'chasebot_app.licensetemplate': {
            'Meta': {'object_name': 'LicenseTemplate'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Currency']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_users': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'})
        },
        'chasebot_app.maritalstatus': {
            'Meta': {'object_name': 'MaritalStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'martial_status_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'martial_status_type_en': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'martial_status_type_en_gb': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'chasebot_app.salesitem': {
            'Meta': {'object_name': 'SalesItem'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Company']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'chasebot_app.salesterm': {
            'Meta': {'object_name': 'SalesTerm'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sales_term': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'chasebot_app.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'browser': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.Company']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'is_cb_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chasebot_app.LicenseTemplate']"}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'chasebot_app.worldborder': {
            'Meta': {'object_name': 'WorldBorder'},
            'area': ('django.db.models.fields.IntegerField', [], {}),
            'fips': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lon': ('django.db.models.fields.FloatField', [], {}),
            'mpoly': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pop2005': ('django.db.models.fields.IntegerField', [], {}),
            'region': ('django.db.models.fields.IntegerField', [], {}),
            'subregion': ('django.db.models.fields.IntegerField', [], {}),
            'un': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['chasebot_app']