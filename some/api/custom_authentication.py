from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from some.api.custom_token import TemporaryToken
from cinema.settings import TIME_TO_LOGOUT


class TemporaryTokenAuthentication(TokenAuthentication):
    model = TemporaryToken

    def authenticate_credentials(self, key):
        try:
            user, token = super().authenticate_credentials(key)
            if not user.is_superuser and not user.is_staff:
                if timezone.now() - token.last_action >= TIME_TO_LOGOUT:
                    token.delete()
                else:
                    token.last_action = timezone.now()
                    token.save()
            return user, token
        except:
            pass
