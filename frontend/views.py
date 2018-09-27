# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple
from django.shortcuts import render
from itertools import groupby
from operator import itemgetter
import string

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.serializers import serialize
from user_agents import parse
from django.core.urlresolvers import resolve
from django.db.models import F, Q
from django.db.models import Sum
from django.dispatch import receiver
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.db.models import Count

import datetime, json, random
from datetime import timedelta, tzinfo
from django.core.urlresolvers import reverse
import math
from dateutil import parser

from collections import defaultdict, OrderedDict


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template.loader import get_template

from django.contrib.auth import login as django_login, authenticate, logout as django_logout

from django.contrib.auth.decorators import login_required


from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
	
from bs4 import BeautifulSoup
from django.template import Context
import copy
import hashlib
from rest_framework.authtoken.models import Token
import requests
from inventory_management import settings



def signup(request):
	ctx ={}
	return render(request, 'authentication/signup.jinja', ctx)

def signin(request):
	ctx ={}
	return render(request, 'authentication/signin.jinja', ctx)

def products(request, id=None):
	ctx ={}
	if id:
		is_id = id
	else:
		is_id = None
			
	token_ = request.META.get('HTTP_AUTHORIZATION', request.GET.get('token', None))
	token = Token.objects.filter(key=token_)
	
	if token.exists():
		user = token.first().user
	else:
		return redirect('inventory.signin')

	if not is_id:
		r = requests.get(settings.env_url+reverse('api.inventory_views',kwargs={"version":1}), headers={'Authorization': 'Token '+ token_})
	else:
		r = requests.get(settings.env_url+reverse('api.inventory_view',kwargs={"version":1, "id":is_id}), headers={'Authorization': 'Token '+ token_})

	response = json.loads(str(r.text))

	ctx = {
		"response": response['detail']
	}
	if not is_id:
		return render(request, 'product/list.jinja', ctx)
	else:
		return render(request, 'product/edit.jinja', ctx)

def product_add(request):
	ctx ={}
	return render(request, 'product/add.jinja', ctx)

def home(request):
	ctx ={}
	return render(request, 'home.jinja', ctx)


def token_remove(request):
	ctx ={}
	token = str(request.GET.get('token'))
	Token.objects.filter(key=token).delete()
	return HttpResponse("ok", content_type='application/json')





