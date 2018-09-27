# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.sessions.models import Session
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.conf import settings
from importlib import import_module
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.template.response import ContentNotRenderedError
import urllib
import ast, random
from django.db.models import F, Q
from django.utils.encoding import force_text
from django.shortcuts import get_object_or_404
from random import shuffle



engine = import_module(settings.SESSION_ENGINE)

from django.template import Template, Context
# from django.template import Context
# from jinja2.environment import Template, Context

from django.utils.deprecation import MiddlewareMixin


class CachedTemplateMiddleware(MiddlewareMixin):

	def custom_url(self, name, **kwargs):
		return reverse(name, kwargs=kwargs)

	def process_view(self, request, view_func, view_args, view_kwargs):
		#webp support check and set for request object
		if request.META.get('HTTP_ACCEPT'):
			setattr(request, 'is_webp_supported', ("webp" in request.META['HTTP_ACCEPT']))

		#amp support check and set for request object
		setattr(request, 'is_amp', False)
		if '/amp' in request.get_full_path():
			setattr(request, 'is_amp', True)

		setattr(request, 'is_from_android_app', False)


		if request.META.get('HTTP_USER_AGENT'):
			if request.META.get('HTTP_USER_AGENT')=='entrancecorner-user-agent':
				setattr(request, 'is_from_android_app', True)

		cached_views = settings.CACHED_VIEWS.keys()


		ctx = {
			'request': request,
			'csrf_token': get_token(request),
			'static': staticfiles_storage.url,
			'url':self.custom_url,
			'MEDIA_URL': settings.MEDIA_URL,
		}
		if view_func.func_name in cached_views and request.method == 'GET':
			if request.is_amp:
				cache_key = 'templatecaching||' + self._get_url_for_caching(request, view_func) + "_amp"
			else:
				cache_key = 'templatecaching||' + self._get_url_for_caching(request, view_func)

			response = None
			if 'magicflag' not in request.GET:
				response = cache.get(cache_key, None)
			if response is None:
				response = view_func(request, *view_args, **view_kwargs)
				cache_time = settings.CACHED_VIEWS[view_func.func_name]
				cache.set(cache_key, response, cache_time)
		else:
			response = view_func(request, *view_args, **view_kwargs)

		view_ctx = self._get_ctx_for_view(request, view_func, view_kwargs)
		ctx.update(view_ctx)

		if response and 'text' in response.get('content-type'):
			try:
				t = Template(response.content.decode('utf-8'))
				# response.content = t.render(ctx)
				response.content = t.render(Context(ctx))
			except Exception: # for django templates
				pass

		return response

	def _get_url_for_caching(self, request, view_func):
		allowed_query_params = {
			'home': ['q'],
			'stream': ['page','level'],
			'featured': ['page'],
			'latest': ['page'],
		}

		url = request.path

		if view_func.func_name in allowed_query_params and len(request.GET) > 0:
			params_dict = {}
			for key,value in request.GET.iteritems():
				if key in allowed_query_params[view_func.func_name]:
					params_dict[key] = value

			if params_dict:
				url += '?' + urllib.urlencode(params_dict).encode('ascii', 'ignore').decode('ascii')

		return url