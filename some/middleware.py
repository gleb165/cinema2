import datetime

from django.contrib.auth import logout
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from cinema.settings import TIME_TO_LOGOUT


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
