#from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import UUIDField, CreationDateTimeField
from django.core.validators import MinValueValidator
from chasebot import settings
from django.template.loader import get_template
from django.template.context import Context
from django.core.mail import send_mail
from django.contrib.gis.db import models


class Company(models.Model):
    company_name        = models.CharField(max_length=50)
    company_email       = models.EmailField()
    def __unicode__(self):
        return self.company_name
    class Meta:
        verbose_name = _(u'Company')
        verbose_name_plural = _(u'Companies')


class Currency(models.Model):
    currency            = models.CharField(_(u'Currency'), max_length=20)    
    def __unicode__(self):
        return self.currency
    class Meta:
        verbose_name = _(u'Currency')
        verbose_name_plural = _(u'Currencies')


class LicenseTemplate(models.Model):
    name        = models.CharField(_(u'License Type'), max_length=50)
    description = models.TextField(_(u'Description'))
    max_users   = models.PositiveIntegerField(_(u'Maximum Users'))
    price       = models.DecimalField(_(u'Price'), decimal_places=2, max_digits=12, validators=[MinValueValidator(0.01)])
    currency    = models.ForeignKey(Currency)
        
    def __unicode__(self):
        return u'%s' % (self.name)
    class Meta:
        verbose_name = _(u'License')
        verbose_name_plural = _(u'Licenses')


class UserProfile(models.Model):
    user                = models.OneToOneField(User)
    company             = models.ForeignKey(Company)
    is_cb_superuser     = models.BooleanField()
    license             = models.ForeignKey(LicenseTemplate)
    ip                  = models.CharField(max_length=45, blank=True, null=True)
    country             = models.CharField(max_length=100, blank=True, null=True)
    city                = models.CharField(max_length=100, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s, %s' % (self.user.username, self.company.company_name)
    class Meta:
        verbose_name = _(u'User Profile')
        verbose_name_plural = _(u'User Profiles')


class ContactType(models.Model):
    contact_type = models.CharField(_(u'Contact Type'), max_length=30)    
    def __unicode__(self):
        return self.contact_type
    class Meta:
        verbose_name = _(u'Contact Type')
        verbose_name_plural = _(u'Contact Types')


class MaritalStatus(models.Model):
    martial_status_type = models.CharField(_(u'Marital Status'), max_length=30)    
    def __unicode__(self):
        return self.martial_status_type
    class Meta:
        verbose_name = _(u'Marital Status')
        verbose_name_plural = _(u'Marital Statuses')


class Country(models.Model):
    country_code = models.CharField(_(u'Country Code'), max_length=2)
    country_name = models.CharField(_(u'Country'), max_length=50)    
    def __unicode__(self):
        return self.country_name
    class Meta:
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')


class Gender(models.Model):
    gender       = models.CharField(_(u'Sex'), max_length=25)    
    def __unicode__(self):
        return self.gender
    class Meta:
        verbose_name = _(u'Sex')
        verbose_name_plural = _(u'Sexes')


class Contact(models.Model):
    RATING_CHOICES = (               
               (1, _(u'Less Important')),
               (2, _(u'Important')),
               (3, _(u'Very Important')),
               )
    
    first_name          = models.CharField(_(u'First Name'),             max_length=30, blank=True)
    last_name           = models.CharField(_(u'Last Name'),              max_length=50)
    dear_name           = models.CharField(_(u'Preferred Name'),         max_length=15, blank=True)
    address             = models.TextField(_(u'Address'),                blank=True)
    city                = models.CharField(_(u'City'),                   max_length=30, blank=True)
    state               = models.CharField(_(u'State'),                  max_length=30, blank=True)
    postcode            = models.CharField(_(u'Zip Code'),               max_length=30, blank=True)
    country             = models.ForeignKey(Country,                     null=True, blank=True)
    company_name        = models.CharField(_(u'Company Name'),           max_length=30, blank=True)
    position            = models.CharField(_(u'Position'),               max_length=30, blank=True)
    work_phone          = models.CharField(_(u'Work Phone'),             max_length=30, blank=True)
    home_phone          = models.CharField(_(u'Home Phone'),             max_length=30, blank=True)
    mobile_phone        = models.CharField(_(u'Cell Phone'),             max_length=30, blank=True)
    fax_number          = models.CharField(_(u'Fax Number'),             max_length=30, blank=True)
    email               = models.EmailField(_(u'Email'),                 blank=True)
    birth_date          = models.DateField(_(u'Birthday'),               null=True, blank=True)
    prev_meeting_places = models.TextField(_(u'Previous meetings'),      max_length=50, blank=True)
    contact_type        = models.ForeignKey(ContactType)
    referred_by         = models.CharField(_(u'Referred By'),            max_length=50, blank=True)
    contact_notes       = models.TextField(_(u'Personality Notes'),      blank=True)
    marital_status      = models.ForeignKey(MaritalStatus,               null=True, blank=True)
    gender              = models.ForeignKey(Gender,                      null=True, blank=True)
    contacts_interests  = models.TextField(_(u"Contact's Interests"),    blank=True)
    spouse_first_name   = models.CharField(_(u"Spouse's First Name"),    max_length=30, blank=True)
    spouse_last_name    = models.CharField(_(u"Spouse's Last Name"),     max_length=50, blank=True)
    spouses_interests   = models.TextField(_(u"Spouse's Interests"),     blank=True)
    children_names      = models.CharField(_(u'Children Names'),         max_length=75, blank=True)
    home_town           = models.CharField(_(u'Home Town'),              max_length=30, blank=True)
    company             = models.ForeignKey(Company)    
    important_client    = models.PositiveSmallIntegerField(_(u'Important Client'), blank=True, null=True, choices=RATING_CHOICES)

    def __unicode__(self):
        return self.last_name
    
    class Meta:
        verbose_name = _(u'Contact')
        verbose_name_plural = _(u'Contacts')
    
#   Show all open deals for this contact  
    def get_open_deals(self):
        query = 'SELECT l1.* \
                 FROM chasebot_app_deal AS l1 \
                 INNER JOIN ( \
                    SELECT deal_id, MAX(deal_datetime) AS time_stamp_max \
                    FROM chasebot_app_deal \
                    GROUP BY deal_id \
                 ) AS l2 \
                 ON    \
                 l1.deal_id     = l2.deal_id AND \
                 l1.deal_datetime = l2.time_stamp_max \
                 INNER JOIN ( \
                 SELECT deal_id, deal_datetime, MAX(id) AS trans_max \
                 FROM chasebot_app_deal \
                 GROUP BY deal_id, deal_datetime \
                 ) AS l3 \
                 ON \
                 l1.deal_id     = l3.deal_id AND l1.deal_datetime = l3.deal_datetime AND l1.id   = l3.trans_max \
                 WHERE contact_id = %s and l1.deal_id not in (select deal_id from chasebot_app_deal where status_id in (5, 6))'
        return Deal.objects.raw(query, [self.id])


class SalesItem(models.Model):        
    item_name    = models.CharField(_(u'Item Name'), max_length=40)
    company             = models.ForeignKey(Company)
    def __unicode__(self):
        return self.item_name
    class Meta:
        verbose_name = _(u'Sales Item')
        verbose_name_plural = _(u'Sales Items')

class SalesTerm(models.Model):    
    sales_term          = models.CharField(_(u'Sales Term'), max_length=40)
    def __unicode__(self):
        return self.sales_term
    class Meta:
        verbose_name = _(u'Sales Term')
        verbose_name_plural = _(u'Sales Terms')

class DealStatus(models.Model):
    deal_status         = models.CharField(_(u'Deal Status'), max_length=40)
    def __unicode__(self):
        return self.deal_status
    class Meta:
        verbose_name = _(u'Deal Status')
        verbose_name_plural = _(u'Deal Statuses')


class DealTemplate(models.Model):    
    company             = models.ForeignKey(Company)
    deal_name           = models.CharField(_(u'Deal Name'), max_length=40)
    deal_description    = models.TextField(_(u'Deal Description'),     blank=True)
    sales_item          = models.ManyToManyField(SalesItem)    
    currency            = models.ForeignKey(Currency)
    price               = models.DecimalField(_(u'Price'), decimal_places=2, max_digits=12, validators=[MinValueValidator(0.01)])
    sales_term          = models.ForeignKey(SalesTerm)
    quantity            = models.PositiveIntegerField(_(u'Quantity'))    
    def __unicode__(self):
        return self.deal_name 
    class Meta:
        verbose_name = _(u'Deal Type')
        verbose_name_plural = _(u'Deal Types')


class Conversation(models.Model):
    contact             = models.ForeignKey(Contact)
    conversation_datetime = models.DateTimeField()    
    subject             = models.CharField(_(u'Subject'),      max_length=50)
    notes               = models.TextField(_(u'Notes'),        blank=True)
    
    class Meta:
        get_latest_by   = 'conversation_datetime'            
        verbose_name = _(u'Conversation')
        verbose_name_plural = _(u'Conversations')    
    def __unicode__(self):
        return self.subject


class Deal(models.Model):    
    def __init__(self, *args, **kwargs):
        super(Deal, self).__init__(*args, **kwargs)
        
    deal_id             = UUIDField()
    status              = models.ForeignKey(DealStatus, null=True, blank=True)    
    contact             = models.ForeignKey(Contact)
    deal_template       = models.ForeignKey(DealTemplate)
    deal_template_name  = models.CharField(_(u'Deal Template Name'), max_length=100, blank=True)
    deal_datetime       = models.DateTimeField()
    conversation        = models.ForeignKey(Conversation)
    set                 = models.PositiveIntegerField(_(u'Set Number'))
    deal_instance_name  = models.CharField(_(u'Deal Name'), max_length=100, blank=True)        
    deal_description    = models.TextField(_(u'Deal Description'),     blank=True)    
    price               = models.DecimalField(_(u'Price'), decimal_places=2, max_digits=12, validators=[MinValueValidator(0.01)])
    sales_item          = models.ManyToManyField(SalesItem)
    currency            = models.ForeignKey(Currency)
    sales_term          = models.ForeignKey(SalesTerm)
    quantity            = models.PositiveIntegerField(_(u'Quantity'))
    
    def __unicode__(self): 
        deal_name = ''
        if self.deal_template:
            deal_name = self.deal_template.deal_name            
        return u'{0}{1}{2}'.format(deal_name, _(u' - Set No.'), self.set)
    
    def save(self, *args, **kwargs):
        self.deal_instance_name = self.__unicode__()
        self.deal_template_name = self.deal_template.deal_name
        super(Deal, self).save(*args, **kwargs) # Call the "real" save() method.
    
    class Meta:
        verbose_name = _(u'Deal')
        verbose_name_plural = _(u'Deals')
    
    

class Invitation(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    code = models.CharField(max_length=20)
    sender = models.ForeignKey(User)
    
    def __unicode__(self):
        return u'%s, %s' % (self.sender.username, self.email)    

    def send(self):
        subject = u'Invitation to join Chasebot'
        link = 'http://%s/colleague/accept/%s/' % (settings.SITE_HOST, self.code)
        template = get_template('registration/invitation_email.txt')
        context = Context({'name': self.name, 'link': link, 'sender': self.sender.username, })
        message = template.render(context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])    
    

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name    