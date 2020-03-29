from django import forms


class ContactForm(forms.Form):
    navn = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(help_text='Din e-mailadresse bliver kun delt internt', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    emne = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    besked = forms.CharField(max_length=2400, widget=forms.Textarea(attrs={'class': 'form-control'}))


class LookupEditForm(forms.Form):
    link = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    antal_besøg = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}))
    oprettet = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True}, format='%d %B %Y %H:%M'), input_formats=('%d %B %Y %H:%M',))
    redigeret = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True}, format='%d %B %Y %H:%M'), input_formats=('%d %B %Y %H:%M',))
    deaktiveret_siden = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True}, format='%d %B %Y %H:%M'), input_formats=('%d %B %Y %H:%M',))
    nøgle = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))