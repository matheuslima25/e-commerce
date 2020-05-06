from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN, PasswordResetConfirmView, \
    PasswordChangeView, PasswordResetView, LoginView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, RedirectView, CreateView, DetailView

from core import models, serializers, forms
from core.forms import PasswordResetFormCustom

from core import models


class IndexView(TemplateView):
    template_name = 'index.html'
    success_url = 'home'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['produtos'] = models.Produto.objects.all()
        context['categorias_p'] = models.Categoria.objects.all()
        context['latest_products'] = models.Produto.objects.all().order_by('-created_at')[:5]
        return context


def load_products(request):
    produtos = models.Produto.objects.all()
    paginator = Paginator(produtos, 12)
    page = request.GET.get('page', 1)

    try:
        produtos = paginator.page(page)
    except PageNotAnInteger:
        produtos = paginator.page(1)
    except EmptyPage:
        produtos = paginator.page(paginator.num_pages)

    context = {
        'paginator': paginator,
        'produtos': produtos,
    }

    if request.method == 'POST':
        page_n = request.POST.get('n_page', None)
        serializer = serializers.ProdutosSerializer(paginator.page(page_n).object_list, many=True)
        return JsonResponse(serializer.data, safe=False)

    return render(request, 'product_list.html', context)


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


'''Registration'''


class LoginAuthView(LoginView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors_msgs = []
            errors_fields = []
            for field, errors in dict(form.errors).items():
                errors_fields.append(field)
                for error in errors:
                    if error == u'Este campo é obrigatório.':
                        errors_msgs.append(u'Preencha todos os campos.')
                    else:
                        errors_msgs.append(error)
            data = {
                'status': False,
                'fields': errors_fields,
                'error': list(set(errors_msgs)),
            }
            return JsonResponse(status=404, data=data)
        return HttpResponseRedirect(u'%s' % reverse('home'))

    def form_valid(self, form):
        if 'remember_me' in self.request.POST.keys():
            remember_me = self.request.POST.get('remember_me')  # get remember me data from cleaned_data of form
        else:
            remember_me = ''
        if remember_me:
            self.request.session.set_expiry(0)  # if remember me is
            self.request.session.modified = True
        auth_login(self.request, form.get_user())
        if self.request.is_ajax():
            data = {
                'status': True,
                'msg': u'Seja bem vindo!',
            }
            return JsonResponse(data=data)
        return HttpResponseRedirect(reverse(u'%s' % 'home'))


class PasswordView(PasswordChangeView):
    template_name = 'registration/password-change.html'
    success_url = 'home'
    form_class = PasswordChangeForm

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors_msgs = []
            errors_fields = []
            for field, errors in dict(form.errors).items():
                errors_fields.append(field)
                for error in errors:
                    if error == u'Este campo é obrigatório.':
                        errors_msgs.append(u'Preencha todos os campos.')
                    else:
                        errors_msgs.append(error)
            data = {
                'status': False,
                'fields': errors_fields,
                'error': list(set(errors_msgs)),
            }
            return JsonResponse(status=500, data=data)
        return HttpResponseRedirect(u'%s' % reverse('home'))

    def form_valid(self, form):
        form.save()
        if (update_session_auth_hash is not None and
                not settings.LOGOUT_ON_PASSWORD_CHANGE):
            update_session_auth_hash(self.request, form.user)
        if self.request.is_ajax():
            data = {
                'status': True,
                'msg': u'Senha atualizada com sucesso!',
            }
            return JsonResponse(data=data)
        return HttpResponseRedirect(u'%s' % reverse('home'))


class ForgetView(PasswordResetView):
    template_name = 'registration/forget-password.html'
    email_template_name = 'emails/password-recover.html',
    token_generator = default_token_generator
    form_class = PasswordResetFormCustom

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors_msgs = []
            errors_fields = []
            for field, errors in dict(form.errors).items():
                errors_fields.append(field)
                for error in errors:
                    errors_msgs.append(error)
            data = {
                'status': False,
                'fields': errors_fields,
                'error': list(set(errors_msgs)),
            }
            return JsonResponse(status=404, data=data)
        return super(ForgetView, self).form_invalid(form)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'email_template_name': self.email_template_name,
            'subject_template_name': 'registration/password_reset_subject.txt',
            'request': self.request,
        }
        form.save(**opts)
        if self.request.is_ajax():
            data = {
                'status': True,
                'msg': u'Um email foi enviado com um link para recuperar sua senha!',
            }
            return JsonResponse(data=data)
        return HttpResponseRedirect(reverse('home'))


class PasswordChangeView(PasswordResetConfirmView):
    template_name = 'registration/password-change-confirm.html'
    template_name_ajax = 'love2cook/new-password.html'
    success_url = reverse_lazy('home')

    def get_template_names(self):
        if self.request.is_ajax():
            return self.template_name_ajax
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        context['uidb64'] = self.kwargs.get('uidb64')
        context['token'] = self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        return context

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors_msgs = []
            errors_fields = []
            for field, errors in dict(form.errors).items():
                errors_fields.append(field)
                for error in errors:
                    errors_msgs.append(error)
            data = {
                'status': False,
                'fields': errors_fields,
                'error': list(set(errors_msgs)),
            }
            return JsonResponse(status=404, data=data)
        return super(PasswordChangeView, self).form_invalid(form)

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        if self.request.is_ajax():
            data = {
                'status': True,
                'msg': u'Senha resetada com sucesso!',
            }
            return JsonResponse(data=data)
        return HttpResponseRedirect(self.success_url)


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = forms.RegistrationForm
    success_url = 'home'

    def form_invalid(self, form):
        if self.request.is_ajax():
            errors_msgs = []
            errors_fields = []
            for field, errors in dict(form.errors).items():
                errors_fields.append(field)
                for error in errors:
                    if error == u'Este campo é obrigatório.':
                        errors_msgs.append(u'Preencha todos os campos.')
                    else:
                        errors_msgs.append(error)
            data = {
                'status': False,
                'fields': errors_fields,
                'error': list(set(errors_msgs)),
            }
            return JsonResponse(status=404, data=data)
        return HttpResponseRedirect(u'%s' % reverse('home'))

    def form_valid(self, form):
        account = form.save()
        user = models.User.objects.get(pk=account.pk)
        user.save()
        auth_login(self.request, user, backend='core.backends.EmailBackend')
        if self.request.is_ajax():
            data = {
                'status': True,
                'msg': u'Cadastro realizado com sucesso!',
            }
            return JsonResponse(data=data)
        return HttpResponseRedirect(reverse(u'%s' % 'home'))


class LogoutView(RedirectView):
    url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
