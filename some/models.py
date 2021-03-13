from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime as dt
from django.utils import timezone

now = timezone.now


# Create your models here.

class MyUser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)


class Place(models.Model):
    name = models.CharField(max_length=40, unique=True)
    size = models.PositiveSmallIntegerField(default=1)
    busy = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Film(models.Model):
    name = models.CharField(max_length=100, unique=True)
    begin = models.DateField()
    end = models.DateField()

    def __str__(self):
        return self.name


class Show(models.Model):
    place = models.ForeignKey('Place', on_delete=models.CASCADE, related_query_name='shows')
    film = models.ForeignKey('Film', on_delete=models.CASCADE, related_query_name='shows')
    show_time_start = models.DateTimeField(default=now)
    show_time_end = models.DateTimeField(default=now)
    price = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.film} on {self.show_time_start}'
