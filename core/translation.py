from modeltranslation.translator import translator, TranslationOptions

from search.models import ShippingMethod, Continent, Country


class ShippingMethodTranslationOptions(TranslationOptions):
    fields = ('name',)


class ContinentTranslationOptions(TranslationOptions):
    fields = ('name',)


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(ShippingMethod, ShippingMethodTranslationOptions)
translator.register(Continent, ContinentTranslationOptions)
translator.register(Country, CountryTranslationOptions)
