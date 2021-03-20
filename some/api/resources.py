import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework import viewsets, settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import F, Q
from rest_framework import status

from some.api.permissions import IsAdminOrReadOnly

from cinema.settings import AUTH_USER_MODEL
from some.api.serializers import ShowSerializer, OrderSerializer, FilmSerializer
from some.models import Show, MyUser, Film


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ShowViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated, ))
    def create_order(self, request, pk):
        amount = request.data.get('amount')
        user = request.user.id
        serializer = OrderSerializer(data={"amount": amount, "show": pk, "user": user})
        if serializer.is_valid():
            show = Show.objects.get(id=pk)
            show.busy += int(amount)
            if show.busy <= show.place.size:
                serializer.save()
                show.save()
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def filter_day(self, request, first_day, second_day):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        try:
            start = int(start)
            start_time = datetime.datetime(year=first_day.year, month=first_day.month,
                                           day=first_day.day, hour=start)
        except:
            start_time = first_day

        queryset = self.get_queryset().filter(show_time_start__gte=start_time)

        try:
            end = int(end)
        except:
            queryset = queryset.exclude(show_time_end__gte=second_day)
            serializer = ShowSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        end_time = datetime.datetime(year=first_day.year, month=first_day.month,
                                     day=first_day.day, hour=end)
        queryset = queryset.exclude(show_time_end__gte=end_time)
        serializer = ShowSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def today(self, request):
        td = timezone.now()
        tomorrow = td + datetime.timedelta(days=1)
        return self.filter_day(request, td, tomorrow)

    @action(detail=False, methods=['get'])
    def tomorrow(self, request):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        after_tomorrow = tomorrow + datetime.timedelta(days=1)
        return self.filter_day(request, tomorrow, after_tomorrow)
