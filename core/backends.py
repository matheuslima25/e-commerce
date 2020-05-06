from core import models


class EmailBackend(object):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = models.User.objects.get(email=username)
        except models.User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
            else:
                return None

    def get_user(self, user_id):
        try:
            return models.User.objects.get(pk=user_id)
        except models.User.DoesNotExist:
            return None
