from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from some.models import Film, Place, Show
import datetime as dt


class MyDateInput(forms.DateInput):
    input_type = 'date'


class MyDateTimeInput(forms.DateInput):
    input_type = 'datetime-locale'


class RegForm(forms.Form):
    name = forms.CharField(label='username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='password')
    confirm = forms.CharField(label='confirm', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm'):
            raise ValidationError("passwords do not match")


class FilmForm(ModelForm):
    #begin = forms.DateField(widget=forms.DateInput, input_formats=['%y %m %d'], label='begin')
    #end = forms.DateField(widget=forms.DateInput, input_formats=['%y %m %d'], label='end')

    class Meta:
        model = Film
        widgets = {'begin': MyDateInput(), 'end': MyDateInput()}
        initials = {'begin': dt.date.today, 'end': dt.date.today}
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        begin = cleaned_data.get('begin')
        end = cleaned_data.get('end')
        if begin - dt.date.today() < dt.timedelta(0) or end - dt.date.today() < dt.timedelta(0):
            raise ValidationError("End or Beginning of film shows can't be set in past")
        if end - begin < dt.timedelta(0):
            raise ValidationError("The end of film shows can't be earlier then its beginning")


class PlaceForm(ModelForm):
    class Meta:
        model = Place
        exclude = ['busy']


class ShowForm(ModelForm):
    class Meta:
        model = Show
        fields = '__all__'
        widgets = {'show_time_start': MyDateTimeInput(),
                   'show_time_end': MyDateTimeInput()}

    '''def clean(self):
        cleaned_data = super().clean()
        begin = cleaned_data.get('show_time_start')
        end = cleaned_data.get('show_time_end')
        delta = dt.timedelta(0)
        if end - begin < delta:
            raise ValidationError("The end of film shows can't be earlier then its beginning")'''
