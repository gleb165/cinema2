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

    class Meta:
        model = Show
        fields = '__all__'

    def validate(self, data):
        show_start = data['show_time_start']
        show_end = data['show_time_end']
        if show_start > show_end:
            raise serializers.ValidationError('finish must occur after start')
        film_start = data['film']['begin']
        film_end = data['film']['end']
        if not (film_start <= show_start.date() <= film_end) or \
                not (film_start <= show_end.date() <= film_end):
            raise serializers.ValidationError('show must be held during film period')

        show_busy = data['busy']
        place_size = data['place']['size']
        if show_busy > place_size:
            raise serializers.ValidationError('can\'t buy more tickets than the size of place')
        return data

    def create(self, validated_data):
        place_data = validated_data.pop('place')
        new_place = Place.objects.get_or_create(**place_data)
        film_data = validated_data.pop('film')
        new_film = Film.objects.get_or_create(**film_data)

        show = Show.objects.create(place=new_place, film=new_film, **validated_data)
        return show


class OrderSerializer(serializers.ModelSerializer):
    user = MyUserSerializer
    show = ShowSerializer

    class Meta:
        model = Order
        fields = '__all__'
