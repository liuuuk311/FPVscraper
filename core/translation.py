from modeltranslation.translator import translator, TranslationOptions

from search.models import ShippingMethod, Continent, Country, Brand


class ShippingMethodTranslationOptions(TranslationOptions):
    fields = ('name',)


class ContinentTranslationOptions(TranslationOptions):
    fields = ('name',)


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


class BrandTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(ShippingMethod, ShippingMethodTranslationOptions)
translator.register(Continent, ContinentTranslationOptions)
translator.register(Country, CountryTranslationOptions)
translator.register(Brand, BrandTranslationOptions)
