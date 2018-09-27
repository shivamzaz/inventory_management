# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple
from django.shortcuts import render
from itertools import groupby
from operator import itemgetter

import datetime, json
import math

from datetime import timedelta
from datetime import tzinfo
from dateutil import parser
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.core.urlresolvers import resolve
from django.db.models import Count
from django.db.models import F
from django.db.models import Max
from django.db.models import Min
from django.db.models import Q
from django.db.models import Sum
from django.dispatch import receiver
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from user_agents import parse

from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
import re
from django.contrib.auth.models import User


import urllib

from collections import OrderedDict
from collections import defaultdict


from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout

from django.contrib.auth.decorators import login_required


from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

import ast
import copy
import hashlib
import uuid

from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.template import Context
from rest_framework import authentication
from rest_framework import generics
from rest_framework import mixins
from rest_framework import pagination
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from serializers import serializers
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator

from rest_framework import views
from rest_framework_extensions.cache.decorators import (cache_response)

from django.views.decorators.cache import cache_page

import zlib, random, time
from models import UserRole


import logging
logger = logging.getLogger('django')


class ApiRoot(APIView):
	"""
	In some API's authentication is required.

	For clients to authenticate, the token key should be included in the `Authorization HTTP header`.
	The key should be prefixed by the string literal "Token", with whitespace separating the two strings.
	For example:

		Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

	Token will be given in the response of login API.
	"""

	def get(self, request, version, format=None):

		response = OrderedDict()
		response['login'] = {'desc': 'Authenticates user with user email and password', 'url': reverse('api.login', kwargs={'version': 1}, request=request)}
		response['register'] = {'desc': 'Creates a new user', 'url': reverse('api.register', kwargs={'version': 1}, request=request)}
		response['forgot-password'] = {'desc': 'Send email for forgot password', 'url': reverse('api.forgot_password', kwargs={'version': 1}, request=request)}
		
		return Response(response)


class Register(APIView):

	authentication_classes = (
		authentication.TokenAuthentication,
		authentication.SessionAuthentication
	)

	def post(self, request, version, format=None):
		print "request", request.data['email'], request.data, User.objects.filter(email=str(request.data['email'])).count()
		if User.objects.filter(email=request.data['email']).exists():
			return Response({'detail':'Email already exists.', 'Code': 101}, status=status.HTTP_400_BAD_REQUEST)

		serializer = serializers.UserSerializer(data=request.data)
		if serializer.is_valid():			
			serializer.save()
			user = User.objects.get(id=int(serializer.data['id']))
			user.set_password(request.data['password'])
			user.save()
			user_role = UserRole.objects.create(user=user, user_role=request.data['role'])
			token, created = Token.objects.get_or_create(user=user)
			serialized_data = serializer.data
			serialized_data['token'] = token.key
			serialized_data['user_role'] = user_role.user_role

			return Response(serialized_data, status=status.HTTP_201_CREATED)
			
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
	authentication_classes = (
		authentication.TokenAuthentication,
		authentication.SessionAuthentication
	)

	def post(self, request, version, format=None):
		email = request.data['email']
		password = request.data['password']

		user = User.objects.filter(email=email)
		if user.exists():
			user = user.first()
			user = authenticate(username=user.username, password=password)
		else:
			return Response({'detail':'The username or password is incorrect.', 'Code': 202}, status=status.HTTP_400_BAD_REQUEST)


		if user:
			if not user.is_active:
				return Response({'detail':'The password is valid, but the account has been disabled!', 'Code': 201},
					status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({'detail':'The username or password is incorrect.', 'Code': 202}, status=status.HTTP_400_BAD_REQUEST)

		user = User.objects.get(email=email)

		print "user", user

		user_role = UserRole.objects.get(user=user)

		token, created = Token.objects.get_or_create(user=user)
			
		serializer = serializers.UserSerializer(user, context={'request': request})
		serialized_data = serializer.data
		serialized_data['token'] = token.key
		serialized_data['user_role'] = user_role.user_role

		return Response(serialized_data, status=status.HTTP_200_OK)








