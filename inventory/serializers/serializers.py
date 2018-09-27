# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import serializers
import ast
import urllib, re
from collections import OrderedDict
from copy import deepcopy
from rest_framework.settings import api_settings
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from django.db.models import Q, Max, Min
from django.conf import settings

from django.contrib.auth.models import User



from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from datetime import datetime

from django.db.models import Count
from collections import defaultdict
import random
from inventory.models import Product



class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True)



	class Meta:
		model = User
		fields = (
			'id','email', 'first_name', 'last_name', 
			'password'
		)


class ProductSerializer(serializers.ModelSerializer):


	class Meta:
		model = Product
		fields = (
			'id','name','vendor', 'mrp', 'batch_num', 
			'batch_date', 'quantity', 'status'
		)
