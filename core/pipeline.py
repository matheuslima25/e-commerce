from core import models


def get_avatar(backend, strategy, details, response, user=None, *args, **kwargs):
    url = None
    try:
        profile = models.PerfilUsuario.objects.get(usuario=user)
    except models.PerfilUsuario.DoesNotExist:
        profile = models.PerfilUsuario.objects.create(usuario=user)
    if backend.name == 'facebook':
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
    if backend.name == 'twitter':
        url = response.get('profile_image_url', '').replace('_normal', '')
    if backend.name == 'google-oauth2':
        url = response['picture']
    if url:
        profile.avatar_url = url
        profile.save()
