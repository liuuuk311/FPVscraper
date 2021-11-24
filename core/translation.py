from modeltranslation.translator import translator, TranslationOptions

from search.models import ShippingMethod


class ShippingMethodTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(ShippingMethod, ShippingMethodTranslationOptions)