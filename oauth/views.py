from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .serializers import (
    CreateUserJSONWebTokenSerializer, PasswordResetKeyWebTokenSerializer, PasswordResetWebTokenSerializer, )
from .settings import api_settings

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class JSONWebTokenAPIView(APIView):
    """
    Base API View that various JWT interactions inherit from.
    """
    permission_classes = ()
    authentication_classes = ()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self,
        }

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__)
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response({
            'status': 'error',
            'message': 'Impossível fazer login com as credenciais fornecidas.'
        }, status=status.HTTP_401_UNAUTHORIZED)


class ObtainJSONWebToken(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        API View that receives a POST with a user's username and password.
        Returns a JSON Web Token that can be used for authenticated requests.
        """
        return super(ObtainJSONWebToken, self).post(request, *args, **kwargs)


class CreateUserAndObtainJSONWebToken(JSONWebTokenAPIView):
    serializer_class = CreateUserJSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        API View that receives a POST with a user's username and password.
        Create accout and returns a JSON Web Token that can be used for authenticated requests.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            token, user = serializer.save() or request.user
            # Access log
            # self.create_access_log(request, user=user)
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    response.data['token'],
                                    expires=expiration,
                                    httponly=True)

            response['authorization'] = response_data['token']
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetKeyWebToken(JSONWebTokenAPIView):
    serializer_class = PasswordResetKeyWebTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        API View that receives a POST with a user's email.
        Send email to user, to reset password.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'status': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetWebToken(JSONWebTokenAPIView):
    serializer_class = PasswordResetWebTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        API View that receives a POST with a id, key and new_password.
        Change pawwsord and returns a JSON Web Token that can be used for authenticated requests.
        """
        return super(PasswordResetWebToken, self).post(request, *args, **kwargs)
