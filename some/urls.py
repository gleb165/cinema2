from django.http import HttpResponse
from django.urls import path

from some.views import LogView, OutView, RegView, ShowList, FilmCreateView, PlaceCreateView, ShowCreateView, \
    OrderCreateView, ShowUpdateView, OrderListView

urlpatterns = [
    path('', ShowList.as_view(), name='main'),
    path('login/', LogView.as_view(), name='login'),
    path('logout/', OutView.as_view(), name='logout'),
    path('registrate/', RegView.as_view(), name='registrate'),
    path('film/', FilmCreateView.as_view(), name='add film'),
    path('place/', PlaceCreateView.as_view(), name='add place'),
    path('show/', ShowCreateView.as_view(), name='add show'),
    path('order/', OrderCreateView.as_view(), name='order'),
    path('show/<int:pk>/', ShowUpdateView.as_view(), name='update show'),
    path('orders/', OrderListView.as_view(), name='orders'),
]