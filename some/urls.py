from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views
from some.api.resources import ShowViewSet
from some.views import LogView, OutView, RegView, ShowList, FilmCreateView, PlaceCreateView, ShowCreateView, \
    OrderCreateView, ShowUpdateView, OrderListView, PlaceListView, PlaceUpdateView

router = routers.SimpleRouter()
router.register(r'shows', ShowViewSet)


urlpatterns = [
    path('', ShowList.as_view(), name='main'),
    path('login/', LogView.as_view(), name='login'),
    path('logout/', OutView.as_view(), name='logout'),
    path('registrate/', RegView.as_view(), name='registrate'),
    path('film/', FilmCreateView.as_view(), name='add film'),
    path('place/', PlaceCreateView.as_view(), name='add place'),
    path('places/', PlaceListView.as_view(), name='places'),
    path('place/<int:pk>/', PlaceUpdateView.as_view(), name='update place'),
    path('show/', ShowCreateView.as_view(), name='add show'),
    path('order/', OrderCreateView.as_view(), name='order'),
    path('show/<int:pk>/', ShowUpdateView.as_view(), name='update show'),
    path('orders/', OrderListView.as_view(), name='orders'),
    path('api/auth/', views.obtain_auth_token),
    path('api/', include(router.urls)),
]