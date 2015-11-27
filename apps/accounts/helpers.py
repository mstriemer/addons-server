import json

from django.conf import settings

import jinja2
from jingo import register


@register.function
@jinja2.contextfunction
def fxa_config(context):
    request = context['request']
    config = {camel_case(key): value
              for key, value in settings.FXA_CONFIG.iteritems()
              if key != 'client_secret'}
    set_fxa_state(request)
    config['state'] = request.session['fxa_state']
    return config


def set_fxa_state(request):
    if needs_fxa_state(request):
        request.session['fxa_state'] = json.dumps(fxa_state(request.user))


def needs_fxa_state(request):
    def load_fxa_state():
        return json.loads(request.session['fxa_state'])

    try:
        return ('fxa_state' not in request.session or
                load_fxa_state()['user_id'] != request.user.pk)
    except ValueError:
        return True


def fxa_state(user):
    return {
        'user_id': user.pk,
    }


def camel_case(snake):
    parts = snake.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])
