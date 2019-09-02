from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField

from webapp.models import Advertisement, Currency

def get_currency_choices():
    return [(i['id'], i['name']) for i in Currency.objects.values()]

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = PhoneNumberField()

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class AdForm(forms.Form):
    selling = forms.ChoiceField(label='Type of ad', choices=[(True, "Selling"), (False, "Buying")])
    ad_text = forms.CharField(label='Advertisement title', max_length=100)
    price = forms.IntegerField(label='Price', min_value=0)
    markup = forms.IntegerField(label='Markup', min_value=0)
    min_volume = forms.IntegerField(label='Minimum volume', min_value=0)
    max_volume = forms.IntegerField(label='Maximum volume', min_value=0)
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'placeholder':"Enter a Location", 'autocomplete':"off"}))
    place_id = forms.CharField()
    currency = forms.ChoiceField(label='Currency', choices=get_currency_choices)

    def clean(self):
        form_data = self.cleaned_data
        if form_data['min_volume'] > form_data['max_volume']:
            self._errors["min_volume"] = ["Minimum volume must be less than maximum volume"]
            self._errors["max_volume"] = ["Maximum volume must be greater than minimum volume"]
        return form_data

class ReviewForm(forms.Form):
    title = forms.CharField(label='Review Title', max_length=50)
    score = forms.ChoiceField(label='Score', widget=forms.RadioSelect, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    comment = forms.CharField(label='Leave a comment', widget=forms.Textarea, max_length=200)

class SearchAdsForm(forms.Form):

    def get_search_currency_choices():
        return [('any', 'Any')] + get_currency_choices()
    
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'placeholder':"Enter a Location", 'autocomplete':"off"}))
    radius = forms.IntegerField(label='Search Radius', min_value=10, max_value=500, initial=100, widget=forms.NumberInput(attrs={'type':'range', 'step': '10', 'min': '10', 'max': '500'}))
    place_id = forms.CharField()
    currency = forms.ChoiceField(label='Currency', choices=get_search_currency_choices)

    # def __init__(self, initial_country, initial_region, *args, **kwargs):
    #     # Dynamically populate the choices in the form
    #     self.initial_country = initial_country
    #     self.initial_region = initial_region
    #     super(SearchAdsForm, self).__init__(*args, **kwargs)
    #     self.fields['country'].initial = self.initial_country
    #     self.fields['region'].initial = self.initial_region


class ImportReputationForm(forms.Form):
    localbitcoins_username = forms.CharField(label='LocalBitcoins Username', max_length=50, required=False)
    paxful_username = forms.CharField(label='Paxful Username', max_length=50, required=False)

    def __init__(self, initial_localbitcoins, initial_paxful, disabled_localbitcoins, disabled_paxful, *args, **kwargs):
        # Dynamically populate the choices in the form
        super(ImportReputationForm, self).__init__(*args, **kwargs)
        self.fields['localbitcoins_username'].initial = initial_localbitcoins
        self.fields['paxful_username'].initial = initial_paxful
        self.fields['localbitcoins_username'].disabled = disabled_localbitcoins
        self.fields['paxful_username'].disabled = disabled_paxful