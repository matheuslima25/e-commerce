from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from threading import Thread


def send_email_thread(subject='', from_email=settings.DEFAULT_FROM_EMAIL, to=[], params={}, template='', mimetype='text/html; charset=UTF-8', headers={}):
    def _send_email_thread(subject='', to=[], params={}, template='', mimetype='text/html; charset=UTF-8', headers={}):
        text_content = subject
        html_content = loader.render_to_string(template, params)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to, headers=headers)
        msg.attach_alternative(html_content, mimetype)
        msg.send()

    th=Thread(target=_send_email_thread, args=(subject, to, params, template, mimetype, headers))
    th.start()