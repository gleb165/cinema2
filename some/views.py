from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from some.models import MyUser, Show, Film, Place

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView

from some.forms import RegForm, FilmForm, PlaceForm, ShowForm


class LogView(LoginView):
    success_url = reverse_lazy('main')
    template_name = 'log.html'

    def get_success_url(self):
        return self.success_url

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('main'))
        return super().get(request=self.request, *args, **kwargs)


class RegView(FormView):
    form_class = RegForm
    template_name = 'log.html'
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        username = form.cleaned_data['name']
        password = form.cleaned_data['password']
        MyUser.objects.create_user(username=username, password=password, email=None)
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super().form_valid()


class OutView(LogoutView):
    next_page = 'main'


class ShowList(ListView):
    model = Show
    template_name = 'shows.html'


class FilmCreateView(CreateView, PermissionRequiredMixin):
    permission_required = 'request.user.is_superuser'
    model = Film
    success_url = reverse_lazy('main')
    form_class = FilmForm
    template_name = 'form.html'


class PlaceCreateView(CreateView, PermissionRequiredMixin):
    permission_required = 'request.user.is_superuser'
    model = Place
    success_url = reverse_lazy('main')
    form_class = PlaceForm
    template_name = 'form.html'


class ShowCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'request.user.is_superuser'
    model = Show
    success_url = reverse_lazy('main')
    form_class = ShowForm
    template_name = 'form.html'

    def form_valid(self, form):
        x = 5
        return super().form_valid(form)
