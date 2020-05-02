from core import models


def get_categories(request):
    categorias = models.Categoria.objects.filter(is_sub=False)
    return {'categorias': categorias}
