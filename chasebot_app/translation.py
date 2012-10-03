from modeltranslation.translator import translator, TranslationOptions
from chasebot_app.models import Gender, ContactType, Country

class GenderTranslationOptions(TranslationOptions):
    fields = ('gender',)
    
class ContactTypeTranslationOptions(TranslationOptions):
    fields = ('contact_type',)

class CountryTranslationOptions(TranslationOptions):
    fields = ('country_name',)

translator.register(Gender, GenderTranslationOptions)
translator.register(ContactType, ContactTypeTranslationOptions)
translator.register(Country, CountryTranslationOptions)