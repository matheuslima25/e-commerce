import os

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


def validate_file(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            u'Extenção não suportada. Por favor, insira um conteúdo com uma das seguintes extensões: .jpeg, .jpg, .png,')


def file_size(value):
    filesize = value.size

    if filesize > 5242880:
        raise ValidationError(_(u'O limite de upload é de 5MB.'))
    else:
        return value
