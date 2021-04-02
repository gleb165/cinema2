from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from some.models import Film, Place, Show, Order, MyUser
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
        exclude = ('busy', )
        widgets = {'show_time_start': MyDateTimeInput(),
                   'show_time_end': MyDateTimeInput(),
                   'free': forms.HiddenInput()}

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('show_time_start')
        end = cleaned_data.get('show_time_end')
        delta = dt.timedelta(0)

        if end - start <= delta:
            raise ValidationError("The end of film shows can't be earlier then its beginning")

        film = cleaned_data.get('film')
        if not (film.begin <= start.date() <= film.end) or \
                not (film.begin <= end.date() <= film.end):
            raise ValidationError('show must be held during film period')

        place = cleaned_data.get('place')
        q1 = Q(place=place, show_time_start__gte=start, show_time_start__lte=end)
        q2 = Q(place=place, show_time_end__gte=start, show_time_end__lte=end)
        query = Show.objects.filter(q1 | q2)

        if len(query) and not self.instance.pk or len(query) > 1:
            raise ValidationError("Some show is already set in the same place simultaneously")


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def is_valid(self):
        self.data = self.data.copy()
        user = MyUser.objects.get(id=self.data.get('user'))
        show = Show.objects.get(id=self.data.get('show_id'))
        self.data.update({'user': user, 'show': show})
        return super().is_valid()

