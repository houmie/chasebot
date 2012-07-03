import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

# Create your models here.

class Company(models.Model):
    company_name        = models.CharField(max_length=50)
    company_email       = models.EmailField()
    def __unicode__(self):
        return self.company_name



class UserProfile(models.Model):
    user                = models.OneToOneField(User)
    company             = models.ForeignKey(Company)
    def __unicode__(self):
        return u'%s, %s' % (self.user.username, self.company.company_name)

    #def create_user_profile(sender, instance, created, **kwargs):
    #    if created:
    #        UserProfile.objects.create(user=instance)

    #post_save.connect(create_user_profile, sender=User)

#    def save(self, *args, **kwargs):
#
#        if not self.company_code:
#            self.company_code = uuid.uuid1()
#
#        super(Company, self).save(*args, **kwargs)


class ContactType(models.Model):
    contact_type = models.CharField(_(u"Contact Type"), max_length=30)
    company      = models.ForeignKey(Company)
    def __unicode__(self):
        return self.contact_type


class MaritalStatus(models.Model):
    martial_status_type = models.CharField(_(u"Marital Status"), max_length=30)
    #company             = models.ForeignKey(Company)
    def __unicode__(self):
        return self.martial_status_type


class Country(models.Model):
    country_code = models.CharField(_(u"Country Code"), max_length=2)
    country_name = models.CharField(_(u"Country"), max_length=40)
    #company      = models.ForeignKey(Company)
    def __unicode__(self):
        return self.country_name


class Gender(models.Model):
    gender       = models.CharField(_(u"Sex"), max_length=10)
    #company      = models.ForeignKey(Company)
    def __unicode__(self):
        return self.gender


#CONTACT_TYPE_CHOICES = (
#    ('S', 'Single')
#)
#contact_type        = models.CharField(max_length=1, choices=CONTACT_TYPE_CHOICES)

class Contact(models.Model):
    first_name          = models.CharField(_(u"First Name"),             max_length=30, blank=True)
    last_name           = models.CharField(_(u"Last Name"),              max_length=50)
    dear                = models.CharField(_(u"Dear"),                   max_length=15, blank=True)
    address             = models.TextField(_(u"Address"),                blank=True)
    city                = models.CharField(_(u"City"),                   max_length=30, blank=True)
    state               = models.CharField(_(u"State"),                  max_length=30, blank=True)
    postcode            = models.CharField(_(u"Zip Code"),               max_length=30, blank=True)
    country             = models.ForeignKey(Country,                     null=True, blank=True, verbose_name=_(u'Country'))
    company_name        = models.CharField(_(u"Company Name"),           max_length=30, blank=True)
    position            = models.CharField(_(u"Position"),               max_length=10, blank=True)
    work_phone          = models.CharField(_(u"Work Phone"),             max_length=30, blank=True)
    home_phone          = models.CharField(_(u"Home Phone"),             max_length=30, blank=True)
    mobile_phone        = models.CharField(_(u"Cell Phone"),             max_length=30, blank=True)
    fax_number          = models.CharField(_(u"Fax Number"),             max_length=30, blank=True)
    email               = models.EmailField(_(u"Email"),                 blank=True)
    birth_date          = models.DateField(_(u"Day Of Birth"),           null=True, blank=True)
    prev_meeting_places = models.CharField(_(u"Previous meetings"),      max_length=50, blank=True)
    contact_type        = models.ForeignKey(ContactType,                 verbose_name=_(u'Contact Type'))
    referred_by         = models.CharField(_(u"Referred By"),            max_length=50, blank=True)
    contact_notes       = models.TextField(_(u"Personality Notes"),      blank=True)
    marital_status      = models.ForeignKey(MaritalStatus,               null=True, blank=True, verbose_name=_(u'Marital Status'))
    gender              = models.ForeignKey(Gender,                      null=True, blank=True, verbose_name=_(u'Sex'))
    contacts_interests  = models.TextField(_(u"Contact's Interests"),    blank=True)
    spouse_first_name   = models.CharField(_(u"Spouse's First Name"),    max_length=30, blank=True)
    spouse_last_name    = models.CharField(_(u"Spouse's Last Name"),     max_length=50, blank=True)
    spouses_interests   = models.TextField(_(u"Spouse's Interests"),     blank=True)
    children_names      = models.CharField(_(u"Children Names"),         max_length=75, blank=True)
    home_town           = models.CharField(_(u"Home Town"),              max_length=30, blank=True)
    company             = models.ForeignKey(Company)
    #call = models.ManyToOneRel

    def __unicode__(self):
        return self.last_name


class ConversationHistory(models.Model):
    contact             = models.ForeignKey(Contact)
    contact_date        = models.DateField(_(u"Conversation Date"),      blank=True)
    contact_time        = models.DateTimeField(_(u"Conversation Time"),  blank=True)
    subject             = models.CharField(_(u"Conversation Subject"),   max_length=50, blank=True)
    notes               = models.TextField(_(u"Conversation Notes"),     blank=True)
    company             = models.ForeignKey(Company)
    def __unicode__(self):
        return self.subject