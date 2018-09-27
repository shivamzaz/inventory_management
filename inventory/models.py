# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import URLValidator
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from django.urls import reverse
from jsonfield import JSONField, JSONCharField
from django.conf import settings
import random, string
import urllib2
import BeautifulSoup


# Create your models here.



class UserRole(models.Model):
	MANAGER = 1
	ASSISTANT = 0

	ROLE_CHOICES = (
		(ASSISTANT, 'Assistant'),
		(MANAGER, 'Manager')

	)
	user_role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
	user = models.ForeignKey(User, null=True, blank=True)

	class Meta:
		db_table = 'user_inventory_role'

	def __unicode__(self):
		return '%s (id:%s)' % (self.name, self.id)


@receiver(pre_save, sender=User)
def make_username(sender, instance, **kwargs):
     if not instance.username:
         instance.username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
         User.objects.filter(id=instance.id).update(username=instance.username)


class Product(models.Model):

	PENDING = 0
	Approved = 1

	STATUS_CHOICES = (
		(Approved, 'Approved'),
		(PENDING, 'Pending')

	)

	name = models.CharField(max_length=255, null=True, blank=True)
	vendor = models.CharField(max_length=255, null=True, blank=True)
	mrp = models.IntegerField(null=True, blank=True)
	batch_num = models.CharField(max_length=255, unique=True)
	batch_date = models.CharField(max_length=255, null=True, blank=True)
	quantity = models.IntegerField(null=True, blank=True)
	status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True, blank=True)

	added_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	user = models.ForeignKey(User, null=True, blank=True)


	class Meta:
		db_table= 'product'

	def __unicode__(self):
		return '(id:%s) %s' % (self.id, self.name)


@receiver(post_save, sender=Product)
def update_status(sender, instance=None, created=False, **kwargs):
	if instance.user:
		print "ok"
		if UserRole.objects.get(user=instance.user).user_role==UserRole.ASSISTANT:
			Product.objects.filter(user=instance.user).update(status=0)
		else:
			Product.objects.filter(user=instance.user).update(status=1)

