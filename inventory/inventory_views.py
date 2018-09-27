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
from inventory.models import Product




import logging
logger = logging.getLogger('django')


class Inventory(APIView):
	"""
	Available methods: `POST`

	Authentication Required: `Yes`

	Post data: num_questions, exam_uri_slug, chapter_id[], test_type
	
	"""

	authentication_classes = (
		authentication.TokenAuthentication,
		authentication.SessionAuthentication
	)

	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, version, format=None, *args, **kwargs):

		is_id = kwargs.get('id', None)

		allow_products_status = self.request.query_params.get('approved', self.request.query_params.get('not_approved', None))

		if is_id:	
			products = Product.objects.filter(id=is_id)
		else:
			products = Product.objects.all()

		if allow_products_status:
			products = products.filter(status=allow_products_status)

		serializer = serializers.ProductSerializer(products, many=True)

		return Response({"detail": serializer.data}, status=status.HTTP_200_OK)


	def post(self, request, version, format=None, *args, **kwargs):

		is_id = kwargs.get('id', None)

		if is_id:
			print "is_id", is_id
			product = Product.objects.get(id=int(is_id))
			print str(request.data['batch_date']), request.data['status']
			product = Product.objects.filter(id=int(is_id))
			product.update(batch_date = str(request.data['batch_date']),
							batch_num = request.data['batch_num'],
							mrp = request.data['mrp'],
							name = request.data['name'],
							quantity = request.data['quantity'],
							status = request.data['status'],
							vendor = request.data['vendor']
						   )
			return Response(request.data, status=status.HTTP_200_OK)

		serializer = serializers.ProductSerializer(data=request.data)

		if serializer.is_valid():		

			serializer.save()

			product = Product.objects.get(batch_num=serializer.data['batch_num'])
			product.user = request.user
			product.save()

		return Response(serializer.data, status=status.HTTP_200_OK)


	def put(self, request, version, format=None):

		product_id = request.data['product_id']
		product_status = int(request.data.get('status', 1))

		if not product_id:
			return Response({'detail':'Product Id is required.', 'Code': 202}, status=status.HTTP_400_BAD_REQUEST)

		product = Product.objects.filter(id=product_id)

		if product.exists():
			product.update(status=product_status)

		return Response({'detail': "OK"}, status=status.HTTP_200_OK)


	def delete(self, request, version, format=None, *args, **kwargs):

		product_id = kwargs.get('id', None)

		product = Product.objects.filter(id=product_id)

		if product.exists():
			product.delete()
		else:
			return Response({'detail':'Product is not present.', 'Code': 202}, status=status.HTTP_400_BAD_REQUEST)

		return Response({'detail': "OK"}, status=status.HTTP_200_OK)


