from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView

from core import models


class IndexView(LoginView, TemplateView):
    template_name = 'index.html'
    success_url = 'home'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['produtos'] = models.Produto.objects.all()
        context['categorias_p'] = models.Categoria.objects.all()
        context['produtos'] = models.Produto.objects.all()
        context['latest_products'] = models.Produto.objects.all().order_by('-created_at')[:5]
        return context

    def form_valid(self, form):
        remember = False
        if 'remember_me' in self.request.POST:
            remember = True
        if not remember:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        auth_login(self.request, form.get_user())
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('home')


class ProductDetail(DetailView):
    model = models.Produto
    context_object_name = 'produto'
    template_name = 'product.html'

    def get_queryset(self):
        return models.Produto.objects.filter(id=self.kwargs.get(self.pk_url_kwarg, None))

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        produto = models.Produto.objects.get(id=self.kwargs.get(self.pk_url_kwarg, None))
        context['produtos_relacionados'] = models.Produto.objects.filter(categoria=produto.categoria)
        context['imagens'] = models.ProdutoImagem.objects.filter(produto_id=self.kwargs.get(self.pk_url_kwarg, None))
        return context


class ProductCategoryView(ListView):
    model = models.Produto
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['categoria'] = models.Categoria.objects.get(slug=self.kwargs.get('slug', None))
        context['produtos'] = models.Produto.objects.filter(categoria__slug=self.kwargs.get('slug', None))
        return context
