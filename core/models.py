import uuid
from random import random

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import Group, AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet, ProtectedError, Q
from django.db.models.signals import m2m_changed
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from core import signals
from core.choices import GENDER_CHOICES, STATE_CHOICES, RATING_CHOICES, QUANTITY_CHOICES


class BaseModelQuerySet(QuerySet):

    def delete(self):
        [x.delete() for x in self]

    def hard_delete(self):
        [x.hard_delete() for x in self]

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)


class BaseModelManager(models.Manager):
    use_for_related_fields = True

    def __init__(self, *args, **kwargs):
        self.active_only = kwargs.pop('active_only', True)
        super(BaseModelManager, self).__init__(*args, **kwargs)

    def all_objects(self):
        return BaseModelQuerySet(self.model)

    def get_queryset(self):
        if self.active_only:
            return BaseModelQuerySet(self.model).filter(is_active=True)
        return BaseModelQuerySet(self.model)

    def hard_delete(self):
        self.get_queryset().hard_delete()


class BaseModel(models.Model):
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)
    is_active = models.BooleanField(
        editable=False, default=True, verbose_name='registro ativo'
    )

    objects = BaseModelManager()
    all_objects = BaseModelManager(active_only=False)

    def _on_delete(self):
        for relation in self._meta._relation_tree:
            on_delete = getattr(relation.remote_field, 'on_delete')

            if on_delete in [None, models.DO_NOTHING]:
                continue

            filter = {relation.name: self}
            related_queryset = relation.model.objects.filter(**filter)

            if on_delete == models.CASCADE:
                relation.model.objects.filter(**filter).delete()
            elif on_delete == models.SET_NULL:
                for r in related_queryset.all():
                    related_queryset.update(**{relation.name: None})
            elif on_delete == models.PROTECT:
                if related_queryset.count() > 0:
                    raise ProtectedError('Cannot remove this instances',
                                         related_queryset.all())
            else:
                raise NotImplementedError()

    def delete(self):
        self.is_active = False
        self.save()
        self._on_delete()

    def hard_delete(self):
        super(BaseModel, self).delete()

    class Meta:
        abstract = True


class Perfil(Group):
    class Meta:
        proxy = True
        verbose_name = _('Perfil')


class User(AbstractUser, BaseModel):
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['is_superuser', 'username', 'is_active']

    first_name = models.CharField(_('first name'), max_length=150)
    groups = models.ManyToManyField(
        Perfil, verbose_name=_(u'Perfis'), blank=True,
        help_text='Os perfis que este usuário pertence.'
                  + ' Um usuário terá todas as permissões concedidas a'
                  + ' cada um dos seus perfis.', related_name="user_set",
        related_query_name="user"
    )
    telefone = models.CharField(
        _(u'Telefone'), max_length=14, blank=True, null=True
    )
    celular = models.CharField(
        _(u'Celular'), max_length=15, blank=True, null=True
    )
    is_staff = models.BooleanField(
        _(u'Membro'), default=True, help_text=_(
            _(u'Indica que usuário consegue acessar este site.')
        ),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class PerfilUsuario(BaseModel):
    class Meta:
        verbose_name = _(u'Perfil')
        ordering = ('usuario__first_name',)
        select_on_save = True

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nascimento = models.DateField(_(u'Data de nascimento'), blank=True, null=True)
    telefone = models.CharField(_(u'Telefone'), max_length=20, blank=True, null=True)
    genero = models.CharField(_(u'Sexo'), max_length=16, choices=GENDER_CHOICES, blank=True, null=True)
    pais = models.CharField(_(u'País'), max_length=20, blank=True, null=True)
    cep = models.CharField(_(u'CEP'), max_length=16, blank=True, null=True)
    estado = models.CharField(_(u'Estado'), max_length=120, blank=True, null=True, choices=STATE_CHOICES)
    cidade = models.CharField(_(u'Cidade'), max_length=120, blank=True, null=True)
    rua = models.CharField(_(u'Rua'), max_length=255, blank=True, null=True)
    numero = models.CharField(_(u'Número'), max_length=10, blank=True, null=True)
    bairro = models.CharField(_(u'Bairro'), max_length=120, blank=True, null=True)
    complemento = models.CharField(_(u'Complemento'), max_length=255, blank=True, null=True)
    avatar = CloudinaryField(_(u'Avatar'), null=True, blank=True)
    lista = models.ManyToManyField('core.Produto', blank=True, verbose_name=_(u'Carrinho de Compras'),
                                   related_name='carrinho')
    favoritos = models.ManyToManyField('core.Produto', blank=True, verbose_name=_(u'Meus Favoritos'),
                                       related_name='favoritos')

    def cleaned_phone(self):
        def _only_numbers(value):
            value = value or ''
            return ''.join(val for val in value if val.isdigit())

        if self.telefone:
            phone = _only_numbers(self.telefone)
            if len(phone) >= 12:
                return u'+%s' % phone
            return u'+55%s' % phone
        return u'+558130346132'

    def cleaned_addr_cep(self):
        def _only_numbers(value):
            value = value or ''
            return ''.join(val for val in value if val.isdigit())

        return _only_numbers(self.cep)

    def name(self):
        return self.usuario.first_name

    def email(self):
        return self.usuario.email

    def __str__(self):
        return u'%s' % self.usuario


class Categoria(BaseModel):
    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')

    titulo = models.CharField(_('Titulo'), max_length=150)
    subcategoria = models.ManyToManyField('core.Categoria', blank=True)
    is_sub = models.BooleanField(_('É subcategoria?'), default=False, editable=False)
    slug = models.CharField(_('Slug'), max_length=20, null=True, blank=True, editable=False)

    def clean(self):
        if Categoria.objects.filter(Q(titulo=self.titulo) & ~Q(id=self.id)).exists():
            raise ValidationError('Já existe uma categoria com este nome, por favor, escolha outro')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titulo)
        super(Categoria, self).save(*args, **kwargs)

    def __str__(self):
        return self.titulo


''''post_save.connect(signals.categoria_post_save_signals, sender=Categoria)'''''
m2m_changed.connect(signals.categoria_post_save_signal, sender=Categoria.subcategoria.through)


class Produto(BaseModel):
    class Meta:
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')

    titulo = models.CharField(_('Titulo'), max_length=150)
    preco = models.DecimalField(_('Preço'), max_digits=6, decimal_places=2)
    descricao = models.TextField(_('Descrição'), null=True)
    avaliacao = models.CharField(_(u'Avaliação'), max_length=11, choices=RATING_CHOICES, blank=True, null=True,
                                 editable=False)
    destaque = models.BooleanField(_('Destaque'), default=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    promocao = models.DecimalField(_('Preço Promocional'), max_digits=6, decimal_places=2, null=True, blank=True)
    desconto = models.DecimalField(_('Desconto'), max_digits=4, decimal_places=2, null=True, blank=True, editable=False)
    estoque = models.BooleanField(_('Em estoque?'), null=True, blank=True)
    slug = models.CharField(_('Slug'), max_length=20, null=True, blank=True, editable=False)
    peso = models.PositiveIntegerField(_('Peso do produto'), null=True)
    image = CloudinaryField(_('Imagem'))

    def clean(self):
        if self.promocao:
            if self.promocao > self.preco:
                raise ValidationError(_('O preço promocional não pode ser maior que o preço inicial.'))

    def save(self, *args, **kwargs):
        if self.promocao:
            tmp = self.preco - self.promocao
            self.desconto = (tmp / self.preco) * 100

        self.slug = slugify(self.titulo)
        super(Produto, self).save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class ProdutoImagem(BaseModel):
    class Meta:
        verbose_name = _('Imagem')
        verbose_name_plural = _('Imagens')

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    image = CloudinaryField(_('Imagem'), blank=True)

    def save(self, *args, **kwargs):
        super(ProdutoImagem, self).save(*args, **kwargs)

    def __str__(self):
        return self.produto.titulo


class Item(BaseModel):
    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Itens')

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.CharField(_(u'Quantidade'), max_length=11, choices=QUANTITY_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.produto.titulo


def codigo():
    t = u''.join(random.sample('0123456789QWERTYUIOPASDFGHJKLZXCVBNM', 6))
    return u'%s%s' % (t[:3], t[3:6],)


class Pedido(BaseModel):
    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')

    codigo = models.CharField(_(u'Código'), max_length=7, unique=True, default=codigo)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True)
    itens = models.ManyToManyField(Item)

    def __str__(self):
        return self.codigo
