from django.forms import forms


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()