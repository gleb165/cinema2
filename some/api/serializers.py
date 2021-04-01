import datetime

from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from some.models import MyUser, Place, Film, Show, Order

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


'''class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MyUser'''


class RegSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField()

    class Meta:
        fields = '__all__'
        model = MyUser

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise  serializers.ValidationError('passwords must match')
        return data

    def create(self, validated_data):
        user = MyUser.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        return user


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'

    def validate(self, data):
        if data['begin'] >= data['end']:
            raise serializers.ValidationError('finish must occur after start')
        return data


class DetailShowSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    film = FilmSerializer()

    class Meta:
        model = Show
        fields = '__all__'


class ShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Show
        fields = '__all__'
        read_only_fields = ('busy', )

    def validate(self, cleaned_data):
        show_start = cleaned_data.get('show_time_start')
        show_end = cleaned_data.get('show_time_end')

        if show_start and show_end:

            if show_start < timezone.now():
                raise serializers.ValidationError('show cant be held in past')

            if show_start >= show_end:
                raise serializers.ValidationError('finish must occur after start')

        film = cleaned_data.get('film')
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

            if len(query) and not self.instance or len(query) > 1:
                raise serializers.ValidationError("Some show is already set "
                                                  "in the same place simultaneously")

        return cleaned_data

    def create(self, validated_data):
        place = validated_data.pop('place')
        film = validated_data.pop('film')
        return Show.objects.create(place=place, film=film, **validated_data)

    def update(self, instance, validated_data):
        instance.place = validated_data.get('place', instance.place)
        instance.film = validated_data.get('film', instance.film)
        instance.show_time_start = validated_data.get('show_time_start', instance.show_time_start)
        instance.show_time_end = validated_data.get('show_time_end', instance.show_time_end)
        instance.busy = validated_data.get('busy', instance.busy)
        instance.price = validated_data.get('price', instance.price)
        return instance


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class SingleOrderSerializer(serializers.ModelSerializer):
    show = ShowSerializer()

    class Meta:
        model = Order
        exclude = ['user']


class OrderSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    orders = SingleOrderSerializer(many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
