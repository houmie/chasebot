import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class Company(models.Model):
    company_name = models.CharField(max_length=50)
    company_email = models.EmailField()

    def __unicode__(self):
        return self.company_name



class UserProfile(models.Model):
    user = models.OneToOneField(User)
    company = models.ForeignKey(Company)

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

