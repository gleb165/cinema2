import datetime

from django.contrib.auth import logout
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from cinema.settings import TIME_TO_LOGOUT
from some.api.custom_token import TemporaryToken


class AutoLogout(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            form = "%Y %m %d %H:%M:%S"
            user_time = request.session.get('time')
            if user_time:
                user_time = datetime.datetime.strptime(user_time, form)
                if datetime.datetime.now() - user_time < TIME_TO_LOGOUT:
                    request.session['time'] = timezone.now().strftime(form)
                else:
                    logout(request)
            else:
                request.session['time'] = datetime.datetime.now().strftime(form)


class AutoLogoutToken(MiddlewareMixin):

    def process_request(self, request):
        token_request = request.META.get('HTTP_AUTHORIZATION')
        if token_request:
            token_request = (token_request.split())[1]
            form = "%Y %m %d %H:%M:%S"
            try:
                token = TemporaryToken.objects.get(key=token_request)
                if not token.user.is_superuser or not token.user.is_staff:
                    if timezone.now() - token.last_action <= TIME_TO_LOGOUT:
                        token.delete()
                    else:
                        token.last_action = datetime.datetime.now()
                        token.save()
            except TemporaryToken.DoesNotExist:
                return
