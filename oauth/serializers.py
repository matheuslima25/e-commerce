from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from oauth.compat import get_username_field, PasswordField
from oauth.settings import api_settings
from rest_framework import serializers

from core.models import User
from .compat import Serializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class CreateUserJSONWebTokenSerializer(Serializer):
    """
    Serializer class used to validate a username and password.
    'username' is identified by the custom UserModel.USERNAME_FIELD.
    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    name = serializers.CharField(max_length=60)
    password = PasswordField(write_only=True)

    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(CreateUserJSONWebTokenSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()

    @property
    def username_field(self):
        return get_username_field()

    def save(self):
        credentials = {
            self.username_field: self.validated_data.get(self.username_field),
            'password': self.validated_data.get('password'),
        }

        if all(credentials.values()):
            try:
                validate_password(self.validated_data.get('password'),
                                  User(**{self.username_field: self.validated_data.get(self.username_field)}))
            except DjangoValidationError as err:
                raise serializers.ValidationError('\n'.join(err.messages))

            # Try create new user
            try:
                user = User.objects.create_user(**credentials)

            except IntegrityError:
                raise serializers.ValidationError(_(u'Já existe uma conta com este username.'), code='login_failed')
            except Exception as exc:
                raise serializers.ValidationError(_(u'%s' % exc), code='login_failed')

            if user:
                user.is_active = True
                user.first_name = self.validated_data.get('name').split(' ')[0]
                user.last_name = u' '.join(self.validated_data.get('name').split(' ')[1:])
                user.save()

                payload = jwt_payload_handler(user)
                return jwt_encode_handler(payload), user
            else:
                msg = _(u'Login e/ou senha incorretos!')
                raise serializers.ValidationError(msg, code='login_failed')
        else:
            msg = _(u'Os campos {username_field} e password são obrigatórios.')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg, code='login_failed')


class PasswordResetKeyWebTokenSerializer(Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        if not User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError(_(u'Nenhum usuário encontrado.'), code='login_failed')
        return value.lower()

    def validate(self, attrs):
        username = self.validate_username(attrs.get('username'))
        token_generator = default_token_generator
        user = User.objects.get(username=username)

        context = {
            'user': user,
            'token': token_generator.make_token(user),
        }

        return context


class PasswordResetWebTokenSerializer(Serializer):
    id = serializers.CharField(write_only=True)
    key = serializers.CharField(write_only=True)
    new_password = PasswordField(write_only=True)

    def __init__(self, *args, **kwargs):
        super(PasswordResetWebTokenSerializer, self).__init__(*args, **kwargs)

    def validate(self, attrs):
        token_generator = default_token_generator

        try:
            user = User.objects.get(pk=attrs.get('id'))
        except User.DoesNotExist:
            raise serializers.ValidationError(_(u'Nenhum usuário encontrado.'), code='login_failed')

        # Validar password
        try:
            validate_password(attrs.get('new_password'), user)
        except DjangoValidationError as err:
            raise serializers.ValidationError('\n'.join(err.messages))

        if not token_generator.check_token(user, attrs.get('key')):
            raise serializers.ValidationError(_(u'O link de redefinição de senha expirou, tente novamente!'),
                                              code='login_failed')

        user.is_active = True
        user.set_password(attrs.get('new_password'))
        user.save()

        payload = jwt_payload_handler(user)
        return {
            'token': jwt_encode_handler(payload),
            'user': user
        }
