from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.db.models import Q
from django.forms import ModelForm
from django.template import loader
from django.utils.translation import ugettext as _

from core import models
from core.email import send_email_thread


class PedidoForm(ModelForm):
    class Meta:
        model = models.Pedido
        fields = '__all__'


class RegistrationForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = (
            'username', 'email', 'password1', 'password2'
        )

    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if models.User.objects.filter(Q(email=email)).exists():
            raise forms.ValidationError(_(u'Já existe um usuário com esse email.'))
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.first_name = self.cleaned_data['name'].split(' ')[0]
        user.last_name = u' '.join(self.cleaned_data['name'].split(' ')[1:])
        if commit:
            user.save()

        models.PerfilUsuario.objects.create(usuario=user)
        return user


class PasswordResetFormCustom(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not models.User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Não encontramos nenhum cadastro com esse email.')
        return email

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        send_email_thread(
            subject=subject,
            to=[to_email, ],
            params=context,
            template=email_template_name
        )