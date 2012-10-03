from modeltranslation.translator import translator, TranslationOptions
from chasebot_app.models import Gender, ContactType, Country, DealStatus

class GenderTranslationOptions(TranslationOptions):
    fields = ('gender',)
    
class ContactTypeTranslationOptions(TranslationOptions):
    fields = ('contact_type',)

class CountryTranslationOptions(TranslationOptions):
    fields = ('country_name',)

class DealstatusTranslationOptions(TranslationOptions):
    fields = ('deal_status',)


translator.register(Gender, GenderTranslationOptions)
translator.register(ContactType, ContactTypeTranslationOptions)
translator.register(Country, CountryTranslationOptions)
translator.register(DealStatus, DealstatusTranslationOptions)