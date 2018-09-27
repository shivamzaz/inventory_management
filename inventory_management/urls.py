# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""inventory_management URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static
from django.views.static import serve

from rest_framework.routers import SimpleRouter, DefaultRouter
from inventory import auth_views as api_views
from inventory import inventory_views as inventory_views
from frontend import views as frontend_views



#####
#for frontend code
#####
urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^$', frontend_views.home, name='inventory.home'),    
	url(r'^signup/$', frontend_views.signup, name='inventory.signup'),
	url(r'^signin/$', frontend_views.signin, name='inventory.signin'),
	url(r'^products/(?P<id>.+)$', frontend_views.products, name='inventory.products.edit'),
	url(r'^products/$', frontend_views.products, name='inventory.products'),
	url(r'^product-add/$', frontend_views.product_add, name='inventory.product_add'),
	url(r'^token-remove/$', frontend_views.token_remove, name='user.token.remove'),

]

#####
#API code
#####

#API Urls
router_v1 = SimpleRouter()

urlpatterns += [
	url(r'^api/(?P<version>[1])/', include(router_v1.urls)),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
	url(r'^api/(?P<version>[1])/auth/register/', api_views.Register.as_view(), name='api.register'),
	url(r'^api/(?P<version>[1])/auth/login/', api_views.Login.as_view(), name='api.login'),
	url(r'^api/(?P<version>[1])/auth/products/(?P<id>.+)', inventory_views.Inventory.as_view(), name='api.inventory_view'),
	url(r'^api/(?P<version>[1])/auth/products/', inventory_views.Inventory.as_view(), name='api.inventory_views'),
	url(r'^api/(?P<version>[1])/$', api_views.ApiRoot.as_view(), name='api.root'), # should be at the last of api urls

]