from django import forms

class DateFilterForm(forms.Form):
    date = forms.DateField(label='Tarih', widget=forms.DateInput(attrs={'type': 'date'}))
