import jwt
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from six import text_type
from django.utils.translation import ugettext as _
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from oauth.settings import api_settings

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class BaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed(code='authentication_failed')

        user = self.authenticate_credentials(payload)

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _(u'Token inválido.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _(u'Token inválido.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')

        if not user.is_active:
            msg = _(u'Usuário inativo.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')

        return user


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:
        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_authorization_header(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', request.META.get('HTTP_TOKEN', b''))
        if isinstance(auth, text_type):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def get_jwt_value(self, request):
        auth = self.get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _(u'Token inválido. Nenhuma credencial fornecida.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')
        elif len(auth) > 2:
            msg = _(u'Token inválido. A sequência de credenciais não deve conter espaços.')
            raise exceptions.AuthenticationFailed(msg, code='authentication_failed')

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)
