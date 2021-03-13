from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from some.models import MyUser, Show, Film, Place, Order
from django.db.models import Q

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, ListView, CreateView, UpdateView

from some.forms import RegForm, FilmForm, PlaceForm, ShowForm, OrderForm


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

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('main'))
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data['name']
        password = form.cleaned_data['password']
        MyUser.objects.create_user(username=username, password=password, email=None)
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)


class OutView(LogoutView):
    next_page = 'main'


class ShowList(ListView):
    model = Show
    template_name = 'shows.html'


class OrderCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'request.user.is_superuser'
    http_method_names = ['post']
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        show_free = form.cleaned_data['show'].free
        user_amount = form.cleaned_data['amount']
        if show_free - user_amount < 0:
            messages.error(self.request, f'Not enough free places, maximum is {show_free}')
            return HttpResponseRedirect(reverse('main'))
        return super().form_valid()


class ShowUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'request.user.is_superuser'
    model = Show
    form_class = ShowForm
    success_url = reverse_lazy('main')
    template_name = 'form.html'


class FilmCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'request.user.is_superuser'
    model = Film
    success_url = reverse_lazy('main')
    form_class = FilmForm
    template_name = 'form.html'


class PlaceCreateView(PermissionRequiredMixin, CreateView):
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
        start = form.cleaned_data.get('show_time_start')
        end = form.cleaned_data.get('show_time_end')
        place = form.cleaned_data.get('place')
        q1 = Q(place=place, show_time_start__gte=start, show_time_start__lte=end)
        q2 = Q(place=place, show_time_end__gte=start, show_time_end__lte=end)

        if len(Show.objects.filter(q1 | q2)) != 0:
            messages.error(self.request, "Some show is already set in the same place simultaneously")
            return HttpResponseRedirect(reverse('add show'))
        return super().form_valid(form)
