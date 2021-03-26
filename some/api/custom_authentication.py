from rest_framework.authentication import TokenAuthentication

from some.api.custom_token import TemporaryToken


class TemporaryTokenAuthentication(TokenAuthentication):
    model = TemporaryToken

    def authenticate_credentials(self, key):
        try:
            return super().authenticate_credentials(key)
        except:
            pass