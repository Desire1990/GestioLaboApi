from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import timedelta
# ----
from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from datetime import datetime, date
from django.utils import timezone
from django.core.files import File
from django.db import models
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.db import transaction

UNITE_CHOICE=(
		('--------', '-------------'),
		('pc(s)','pc(s)'),
		('kg', 'kg'),
		('g', 'g'),
		('mg', 'mg'),
		('l', 'l'),
		('ml', 'ml')
	)
STATUS_CHOICE=(
		('fonctionel', 'fonctionel'),
		('non-fonctionel', 'non-fonctionel'),
		('reparable', 'reparable'),
		('', '')
	)

class LastLogin(models.Model):
	id = models.SmallAutoField(primary_key=True)
	date = models.DateField(default=date.today)

class User(AbstractUser):
	username = models.CharField(blank=True, null=True, max_length=10, unique=True)
	email = models.EmailField(_('email address'), unique=True, null=True)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

	def __str__(self):
		return "{}".format(self.email)
	
	class Meta:
		ordering = '-id',

# class Supplier(models.Model):
# 	id=models.SmallAutoField(primary_key=True)
# 	name = models.CharField(max_length=200, null=False, blank=True)
#     address = models.CharField(max_length=220)
#     phone = models.CharField(max_length=20)
#     created_date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return self.user.username

class Domain(models.Model):
	id=models.SmallAutoField(primary_key=True)
	name=models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, null=True)
	date_added=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name}"	
class Category(models.Model):
	id=models.SmallAutoField(primary_key=True)
	domain=models.ForeignKey(Domain, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateField(auto_now_add=True)

	class Meta:
		ordering = ('name',)
		verbose_name = 'category'
		verbose_name_plural = 'categories'

	
	def __str__(self):
		return f"{self.name}"	

class Product(models.Model):
	id=models.SmallAutoField(primary_key=True)
	category = models.ForeignKey(Category,on_delete=models.CASCADE)
	# user = models.ForeignKey(User, on_delete=models.CASCADE)
	materiel = models.CharField(max_length=200)
	reference = models.CharField(unique=True,max_length=50)
	designation = models.TextField()
	quantite = models.IntegerField()
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, null=True, blank=True)
	date_reception = models.DateTimeField(_('Caractéristiques complémentaires'),auto_now_add=True)
	date_peremption = models.DateField(_('Sécurité et informations complémentaires(date de peremption'))#expiry date
	# price = models.DecimalField(max_digits=8, decimal_places=2)
	# supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
	class Meta:
		ordering = ('-date_reception',)
		verbose_name = 'product'
		verbose_name_plural = 'products'

	def __str__(self):
		return '{} '.format(self.reference)

class Order(models.Model):
	STATUS_CHOICE = (
		('pending', 'Pending'),
		('decline', 'Decline'),
		('approved', 'Approved'),
		('processing', 'Processing'),
		('complete', 'Complete')
	)
	id=models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	# supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
	# product = models.ForeignKey(Product, on_delete=models.CASCADE)
	designation= models.CharField(max_length=50)
	status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='pending')
	created_date = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.user.username

class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return f'{self.order} - {self.product}'



class Delivery(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	courier_name = models.CharField(max_length=120)
	created_date = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.courier_name

