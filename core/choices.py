from django.utils.translation import ugettext as _

GENDER_CHOICES = [
    ('male', _(u'Masculino')),
    ('female', _(u'Feminino')),
    ('other', _(u'Outros')),
]

STATE_CHOICES = [
    ('AC', u'Acre'),
    ('AL', u'Alagoas'),
    ('AP', u'Amapá'),
    ('AM', u'Amazonas'),
    ('BA', u'Bahia'),
    ('CE', u'Ceará'),
    ('DF', u'Distrito Federal'),
    ('ES', u'Espirito Santo'),
    ('GO', u'Goiás'),
    ('MA', u'Maranhão'),
    ('MT', u'Mato Grosso'),
    ('MS', u'Mato Grosso do Sul'),
    ('MG', u'Minas Gerais'),
    ('PA', u'Pará'),
    ('PB', u'Paraíba'),
    ('PR', u'Paraná'),
    ('PE', u'Pernambuco'),
    ('PI', u'Piauí'),
    ('RJ', u'Rio de Janeiro'),
    ('RN', u'Rio Grande do Norte'),
    ('RS', u'Rio Grande do Sul'),
    ('RO', u'Rondônia'),
    ('RR', u'Roraima'),
    ('SC', u'Santa Catarina'),
    ('SP', u'São Paulo'),
    ('SE', u'Sergipe'),
    ('TO', u'Tocantins'),
]

RATING_CHOICES = [
    ('1', _(u'1 Estrela')),
    ('2', _(u'2 Estrelas')),
    ('3', _(u'3 Estrelas')),
    ('4', _(u'4 Estrelas')),
    ('5', _(u'5 Estrelas')),
]

STATUS_CHOICES = [
    ('1', _(u'Aguardando pagamento')),
    ('2', _(u'Em produção')),
    ('3', _(u'Em trânsito')),
    ('4', _(u'Entregue')),
]

QUANTITY_CHOICES = [
    ('1', _(u'1')),
    ('2', _(u'2')),
    ('3', _(u'3')),
    ('4', _(u'4')),
    ('5', _(u'5')),
]
