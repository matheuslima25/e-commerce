from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView

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
