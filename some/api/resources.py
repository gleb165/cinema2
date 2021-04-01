import datetime
from django.contrib.auth import authenticate
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework import viewsets, settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import F, Q, Max, Sum
from rest_framework import status
from rest_framework import generics
from some.api.custom_token import TemporaryToken
from some.api.permissions import IsAdminOrReadOnly
from rest_framework.decorators import api_view
from cinema.settings import AUTH_USER_MODEL
from some.api.serializers import ShowSerializer, SingleOrderSerializer, FilmSerializer, \
    PlaceSerializer, OrderSerializer, DetailShowSerializer, RegSerializer, CreateOrderSerializer, \
    LoginUserSerializer
from some.models import Show, MyUser, Film, Place, Order


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        TemporaryToken.objects.create(user=instance)

@api_view(['POST'])
def create_auth(request):
    serialized = RegSerializer(data=request.data)
    if serialized.is_valid():
        user = serialized.save()
        user.save()
        token = TemporaryToken.objects.get(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = TemporaryToken.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
        })


class ShowViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Show.objects.filter(show_time_start__gte=datetime.datetime.now())
    serializer_class = ShowSerializer

    def get_serializer_class(self):
        x = super().get_serializer_class() if self.request.POST else DetailShowSerializer
        return x

    def update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        show = Show.objects.get(id=pk)
        if show.busy <= show.place.size:
            return Response({'errors': 'U cant modify show with already sold tickets'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        place_name = self.request.query_params.get('place')

        if not self.request.query_params:
            return queryset

        if place_name is not None:
            try:
                place = Place.objects.get(name=place_name)
            except:
                return queryset.none()
            queryset = queryset.filter(place=place)

        day = self.request.query_params.get('day')

        if day and day != 'today' and day != 'tomorrow':
            return queryset.none()
        if day == 'tomorrow':
            first_day = datetime.date.today() + datetime.timedelta(days=1)
            second_day = first_day + datetime.timedelta(days=1)
        else:
            first_day = timezone.now()
            second_day = first_day + datetime.timedelta(days=1)

        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        try:
            start = int(start)
            start_time = datetime.datetime(year=first_day.year, month=first_day.month,
                                           day=first_day.day, hour=start)
        except:
            start_time = first_day

        queryset = queryset.filter(show_time_start__gte=start_time)

        try:
            end = int(end)
        except:
            queryset = queryset.exclude(show_time_end__gte=second_day)
            serializer = ShowSerializer(queryset, many=True)
            return queryset
        end_time = datetime.datetime(year=first_day.year, month=first_day.month,
                                     day=first_day.day, hour=end)
        queryset = queryset.exclude(show_time_end__gte=end_time)
        serializer = ShowSerializer(queryset, many=True)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def create_order(self, request, pk):
        amount = request.data.get('amount')
        user = request.user.id
        serializer = CreateOrderSerializer(data={"amount": amount, "show": pk, "user": user})
        if serializer.is_valid():
            show = Show.objects.get(id=pk)
            if show.show_time_end >= timezone.now():
                return Response({'show error': 'trying to buy ticket for show in past'}, status=status.HTTP_400_BAD_REQUEST)
            show.busy += int(amount)
            if show.busy > show.place.size:
                return Response({'amount error': 'not enough places in hall'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            show.save()
            return Response({'status': 'success'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListAPIView(generics.ListAPIView):
    serializer_class = SingleOrderSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()

    def filter_queryset(self, queryset):
        self.queryset = super().filter_queryset(queryset)
        self.queryset = self.queryset.filter(user=self.request.user)
        return self.queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        total = self.queryset.annotate(total=F('amount') * F('show__price')) \
            .aggregate(Sum('total')).get('total__sum')
        tmp = {'total': total}
        context.update(tmp)
        return context

    def get_serializer(self, *args, **kwargs):
        ser = super().get_serializer(*args, **kwargs)
        total = ser.context.get('total') or 0
        serializer = OrderSerializer(data={'total': total, 'orders': ser.data})
        serializer.is_valid()
        return serializer

    def list(self, request, *args, **kwargs):
        x = super().list(request=request, *args, **kwargs)
        return x


class PlaceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()

    def update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        max = Place.objects.get(id=pk).shows.aggregate(Max('busy'))
        if max.get('busy__max'):
            return Response({'errors': 'U cant modify place with already sold tickets'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
