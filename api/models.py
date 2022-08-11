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
	)
STATUS_CHOICES = (
	('pending', 'Pending'),
	('decline', 'Decline'),
	('approved', 'Approved'),
	('processing', 'Processing'),
	('complete', 'Complete')
)

class LastLogin(models.Model):
	id = models.SmallAutoField(primary_key=True)
	date = models.DateTimeField(auto_now_add=True)

# cas de stock des Products

class Domain(models.Model):
	id=models.SmallAutoField(primary_key=True)
	name=models.CharField(max_length=200)
	date_added=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name}"	
class Category(models.Model):
	id=models.SmallAutoField(primary_key=True)
	domain=models.ForeignKey(Domain, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('name',)
		verbose_name = 'category'
		verbose_name_plural = 'categories'

	
	def __str__(self):
		return f"{self.name}"	

class Product(models.Model):
	id=models.SmallAutoField(primary_key=True)
	category = models.ForeignKey(Category,on_delete=models.CASCADE)
	materiel = models.CharField(max_length=200)
	reference = models.CharField(unique=True,max_length=50)
	designation = models.TextField()
	quantite = models.IntegerField()
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, null=True, blank=True)
	date_reception = models.DateTimeField(_('Caractéristiques complémentaires'),auto_now_add=True)
	date_peremption = models.DateTimeField(auto_now_add=True)
	class Meta:
		ordering = ('-date_reception',)
		verbose_name = 'product'
		verbose_name_plural = 'products'

	def __str__(self):
		return '{} '.format(self.reference)


# commandes pour les Laboratoires
class Commande(models.Model):
	id=models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	num_commande = models.CharField(max_length=50)
	date_commande = models.DateTimeField(auto_now_add=True)
	date_livraison = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return str(self.num_commande)   
	  
class CommandeItem(models.Model):
	id = models.SmallAutoField(primary_key=True)
	commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_commande = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


# cas des commandes externe de dri lies aux labo
class Order(models.Model):
	id=models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	designation= models.CharField(max_length=50)
	date_order = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username

class OrderItem(models.Model):
	id=models.SmallAutoField(primary_key=True)
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	commande = models.ForeignKey(Commande, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
	quantity = models.IntegerField(default=0)
	created_date = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f'{self.order} - {self.product}'


class Delivery(models.Model):
	id=models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	courier_name = models.CharField(max_length=120)
	date_delivery = models.DateTimeField(auto_now_add=True)
	created_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.courier_name

# cas d'extrat pour identifier les beneficieres(laboratoires)
class Decanat(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, related_name='user_decanat',on_delete=models.PROTECT, editable=False, null=True, blank=True)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name

class Departement(models.Model):
	id = models.SmallAutoField(primary_key=True)
	decanat = models.ForeignKey('Decanat', related_name='decanat_departement', on_delete=models.PROTECT, editable=False, null=True, blank=True)
	user = models.ForeignKey(User, related_name='user_departement',on_delete=models.PROTECT, editable=False, null=True, blank=True)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name


# responsable de labo et chef de departema ainsi que le Doyen pour approbation, admin et autres interacteurs
class Utilisateur(models.Model):
	id = models.BigAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)
	departement = models.ForeignKey(Departement, related_name='Utilisateur_departement',on_delete=models.PROTECT, null=True, blank=True)
	decanat = models.ForeignKey(Decanat, related_name='Utilisateur_decanat',on_delete=models.PROTECT, null=True, blank=True)
	date = models.DateTimeField(auto_now_add=True)
	reset=models.CharField(max_length=6,null=True,editable=False) 

	def __str__(self):
		return f"{self.user}"
