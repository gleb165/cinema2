import datetime

from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.db import models


class TemporaryToken(Token):
    last_action = models.DateTimeField(default=timezone.now())
