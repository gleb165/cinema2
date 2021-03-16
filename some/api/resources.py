from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import viewsets, settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from cinema.settings import AUTH_USER_MODEL
from some.api.serializers import ShowSerializer
from some.models import Show


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class ShowViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
