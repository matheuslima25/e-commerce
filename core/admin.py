from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from core import models


class PerfilUsuarioInline(admin.StackedInline):
    model = models.PerfilUsuario
    extra = 1
    verbose_name = 'Perfil do usuário'


@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_active',)
    list_filter = ('groups', 'is_active',)
    fieldsets_superuser = (
        (None,
         {'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'telefone', 'celular', 'uuid')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), }),
        ('Datas importantes', {'fields': (('last_login', 'date_joined',),)}),
    )
    fieldsets = (
        (None,
         {'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'telefone', 'celular')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'groups',), }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups',)
    readonly_fields = ('last_login', 'date_joined', 'uuid')
    inlines = (PerfilUsuarioInline, )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            return self.fieldsets_superuser
        return super().get_fieldsets(request, obj)


admin.site.unregister(Group)


@admin.register(models.Perfil)
class PerfilAdmin(GroupAdmin):
    def changelist_view(self, request, extra_context=None):
        for name in ('Supervisor', 'Colaborados',):
            models.Perfil.objects.get_or_create(name=name)
        return super().changelist_view(request, extra_context)


@admin.register(models.Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'is_sub')
    search_fields = ('titulo',)


class ImagemInline(admin.StackedInline):
    model = models.ProdutoImagem
    verbose_name = 'Imagem'
    verbose_name_plural = 'Imagens'
    extra = 3


@admin.register(models.Produto)
class ProdutoAdmin(admin.ModelAdmin):
    inlines = (ImagemInline, )
    list_display = ('titulo', 'preco', 'categoria', 'promocao', 'estoque', 'image', 'destaque')
    search_fields = ('titulo', 'categoria', 'destaque')

    fieldsets = (
        (None, {'fields': ('titulo', 'preco', 'destaque', 'categoria', 'estoque', 'image')}),
        ('Promoção', {'fields': ('promocao',)}),
        ('Descrição', {'fields': ('descricao',)}),
    )

    readonly_fields = ('avaliacao', 'slug')


# Custom admin name
admin.site.site_title = u'O Rei das Capas'
admin.site.site_headr = u'O Rei das Capas'
admin.site.index_title = u'O Rei das Capas'
