import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from some.models import MyUser, Place, Film, Show, Order


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MyUser


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'

    def validate(self, data):
        if data['begin'] > data['end']:
            raise serializers.ValidationError('finish must occur after start')
        return data


class ShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Show
        fields = '__all__'
        #read_only_fields = ('busy', )

    def validate(self, cleaned_data):
        show_start = cleaned_data.get('show_time_start')
        show_end = cleaned_data.get('show_time_end')

        if show_start and show_end:

            if show_start < timezone.now():
                raise serializers.ValidationError('show cant be held in past')

            if show_start >= show_end:
                raise serializers.ValidationError('finish must occur after start')

        film = cleaned_data.get('film')

        if film:
            film_start = film.begin
            film_end = film.end

            if not (film_start <= show_start.date() <= film_end) or \
                    not (film_start <= show_end.date() <= film_end):
                raise serializers.ValidationError('show must be held during film period')

        show_busy = cleaned_data.get('busy', 0)
        place = cleaned_data.get('place')

        if place and show_busy > place.size:
            raise serializers.ValidationError('can\'t buy more tickets than the size of place')

        if place and show_start and show_end:

            q1 = Q(place=place, show_time_start__gte=show_start, show_time_start__lte=show_end)
            q2 = Q(place=place, show_time_end__gte=show_start, show_time_end__lte=show_end)
            query = Show.objects.filter(q1 | q2)

            if len(query) > 1:
                raise serializers.ValidationError("Some show is already set "
                                                  "in the same place simultaneously")

        return cleaned_data

    def create(self, validated_data):
        place = validated_data.pop('place')
        film = validated_data.pop('film')
        return Show.objects.create(place=place, film=film, **validated_data)


    def update(self, instance, validated_data):
        x = 5
        instance.place = validated_data.get('place', instance.place)
        instance.film = validated_data.get('film', instance.film)
        instance.show_time_start = validated_data.get('show_time_start', instance.show_time_start)
        instance.show_time_end = validated_data.get('show_time_end', instance.show_time_end)
        instance.busy = validated_data.get('busy', instance.busy)
        instance.price = validated_data.get('price', instance.price)
        return instance



    '''def update(self, instance, validated_data):
        place = validated_data.get('place', instance.place)
        film = validated_data.get('film', instance.film)
        instance.show_time_start = validated_data.get('show_time_start', instance.show_time_start)
        instance.show_time_end = validated_data.get('show_time_end', instance.show_time_end)

        place_inst = Place.objects.get(id=place.id, invoice=instance)
        film_inst = Film.objects.get(id=film.id, invoice=instance)

        return instance'''


class OrderSerializer(serializers.ModelSerializer):
    user = MyUserSerializer
    show = ShowSerializer

    class Meta:
        model = Order
        fields = '__all__'
