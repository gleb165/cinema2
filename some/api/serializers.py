from django.db.models import Q
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
    place = PlaceSerializer(read_only=True)
    film = FilmSerializer(read_only=True)
    busy = serializers.IntegerField(read_only=True)

    class Meta:
        model = Show
        fields = '__all__'

    def validate(self, data):
        cleaned_data = super().validate(data)
        show_start = cleaned_data['show_time_start']
        show_end = cleaned_data['show_time_end']

        if show_start >= show_end:
            raise serializers.ValidationError('finish must occur after start')

        film = FilmSerializer(self.initial_data.get('film'))
        if film.is_valid(raise_exception=True):
            film_start = film.validated_data.get('begin')
            film_end = film.validated_data.get('begin')

        if not (film_start <= show_start.date() <= film_end) or \
                not (film_start <= show_end.date() <= film_end):
            raise serializers.ValidationError('show must be held during film period')

        show_busy = cleaned_data['busy']

        place = PlaceSerializer(self.initial_data.get('place'))
        place_size = place['size']

        start = cleaned_data.get('show_time_start')
        end = cleaned_data.get('show_time_end')

        if show_busy > place_size:
            raise serializers.ValidationError('can\'t buy more tickets than the size of place')

        place = cleaned_data.get('place')
        q1 = Q(place=place, show_time_start__gte=start, show_time_start__lte=end)
        q2 = Q(place=place, show_time_end__gte=start, show_time_end__lte=end)
        query = Show.objects.filter(q1 | q2)

        if len(query) > 1:
            raise serializers.ValidationError("Some show is already set "
                                              "in the same place simultaneously")

        return cleaned_data

    def create(self, validated_data):
        place_data = validated_data.pop('place')
        new_place = Place.objects.get_or_create(**place_data)
        film_data = validated_data.pop('film')
        new_film = Film.objects.get_or_create(**film_data)

        show = Show.objects.create(place=new_place, film=new_film, **validated_data)
        return show

    def update(self, instance, validated_data):
        place = validated_data.get('place', instance.place)
        film = validated_data.get('film', instance.film)
        instance.show_time_start = validated_data.get('show_time_start', instance.show_time_start)
        instance.show_time_end = validated_data.get('show_time_end', instance.show_time_end)

        place_inst = Place.objects.get(id=place.id, invoice=instance)
        film_inst = Film.objects.get(id=film.id, invoice=instance)

        return instance

class OrderSerializer(serializers.ModelSerializer):
    user = MyUserSerializer
    show = ShowSerializer

    class Meta:
        model = Order
        fields = '__all__'
