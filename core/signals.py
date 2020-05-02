from core import models


def categoria_post_save_signal(sender, instance, action, reverse, *args, **kwargs):
    categorias = models.Categoria.objects.all()
    for s in instance.subcategoria.all():
        for c in categorias:
            if s == c:
                c.is_sub = True
                c.save()
