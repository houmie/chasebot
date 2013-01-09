from modeltranslation.translator import translator, TranslationOptions
from chasebot_app.models import DealStatus,\
    MaritalStatus

#class CountryTranslationOptions(TranslationOptions):
#    fields = ('country_name',)

class DealstatusTranslationOptions(TranslationOptions):
    fields = ('deal_status',)

class MaritalstatusTranslationOptions(TranslationOptions):
    fields = ('martial_status_type',)

#translator.register(Country, CountryTranslationOptions)
translator.register(DealStatus, DealstatusTranslationOptions)
translator.register(MaritalStatus, MaritalstatusTranslationOptions)