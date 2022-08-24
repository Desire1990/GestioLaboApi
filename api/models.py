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

# cas de stock des Products central
class Laboratoire(models.Model):
	id=models.SmallAutoField(primary_key=True)
	name = models.CharField(max_length=200)
	# utilisateur=models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
	date_added=models.DateTimeField(auto_now_add=True)

class Domain(models.Model):
	id=models.SmallAutoField(primary_key=True)
	name=models.CharField(max_length=200)
	image = models.ImageField(upload_to='uploads/domains/', null=True, blank=True)
	thumbnail = models.ImageField(upload_to='uploads/domains/thumbnail/', null=True,  blank=True)
	date_added=models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('id',)
		verbose_name = 'domain'
		verbose_name_plural = 'domains'


	def __str__(self):
		return f"{self.name}"

	def get_absolute_url(self):
		return f'domain/{self.id}/'

	def get_image(self):
		if self.image:
			return self.image.url
		return '' 

	def get_thumbnail(self):
		if self.thumbnail:
			return self.thumbnail.url
		else:
			if self.image:
				self.thumbnail = (self.image)
				self.save()

				return self.thumbnail.url
			else:
				return ''

	def make_thumbnail(self, image, size=(200, 100)):
		""" make 300x200 px thumbnail from given image"""
		img = Image.open(image, encoding='UTF-16')
		img.convert('RGB')
		img.thumbnail(size)
		
		thumb_io = BytesIO()
		img.save(thumb_io, 'JPEG', quality=85)

		thumbnail = File(thumb_io, name=image.name)
		return thumbnail

class Category(models.Model):
	id=models.SmallAutoField(primary_key=True)
	domain=models.ForeignKey(Domain, related_name='category', on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('id',)
		verbose_name = 'category'
		verbose_name_plural = 'categories'

	
	def __str__(self):
		return f"{self.name}"	

class Product(models.Model):
	id=models.SmallAutoField(primary_key=True)
	category = models.ForeignKey(Category,related_name='produit', on_delete=models.CASCADE)
	materiel = models.CharField(max_length=200)
	reference = models.CharField(unique=True,max_length=50)
	designation = models.TextField()
	quantite = models.IntegerField()
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, null=True, blank=True)
	date_reception = models.DateTimeField(_('Caractéristiques complémentaires'),auto_now_add=True)
	date_peremption = models.DateTimeField(auto_now_add=True)
	class Meta:
		ordering = ('id',)
		verbose_name = 'product'
		verbose_name_plural = 'products'

	def __str__(self):
		return '{} '.format(self.reference)


# commandes pour les Laboratoires vers le stock central
class Commande(models.Model):
	id=models.SmallAutoField(primary_key=True)
	user = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
	num_commande = models.CharField(max_length=50)
	date_commande = models.DateTimeField(auto_now_add=True)
	date_livraison = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')	
	
	def __str__(self):
		return f'{self.num_commande}'



class CommandeItem(models.Model):
	id=models.SmallAutoField(primary_key=True)
	commande = models.ForeignKey(Commande,related_name='items', on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_commande = models.IntegerField(default=0)
	
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		produit = self.produit
		produit.quantite -= self.qte_commande
		produit.save()

	
	def __str__(self):
		return str(self.commande)   

class BonLivraison(models.Model):
	id=models.SmallAutoField(primary_key=True)
	num_bon_livraison = models.CharField(max_length=50, default='')
	date_bon_livraison = models.DateField()
	# labo = models.ForeignKey(Laboratoire, on_delete=models.CASCADE)
	commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return str(self.num_bon_livraison)
	
class LigneBonLivraison(models.Model):
	id=models.SmallAutoField(primary_key=True)
	bon_livraison = models.ForeignKey(BonLivraison, related_name='ligne', on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_livree = models.IntegerField(default=0)
	qte_restante = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return str(self.bon_livraison)

# cas des commandes externe de dri lies aux labo
class Order(models.Model):
	id=models.SmallAutoField(primary_key=True)
	num_order = models.CharField(max_length=50)
	user = models.ForeignKey('Utilisateur', related_name='orders', on_delete=models.CASCADE)
	professeur = models.ForeignKey('Professeur', related_name='orders', on_delete=models.CASCADE)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.num_order)

	
	# def save(self, *args, **kwargs):
	# 	super().save(*args, **kwargs)
	# 	commande = self.commande
	# 	commande.qte_commande -= self.quantity
	# 	commande.save()

class OrderItem(models.Model):
	id=models.SmallAutoField(primary_key=True)

	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	commande = models.ForeignKey(CommandeItem, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return f'{self.order} - {self.product} - {self.product}'


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
	user = models.ForeignKey(User, related_name='user_departement',on_delete=models.PROTECT, editable=False, null=True, blank=True)
	decanat = models.ForeignKey(Decanat, related_name='decanat_departement', on_delete=models.PROTECT, editable=False, null=True, blank=True)
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

class Professeur(models.Model):
	id = models.BigAutoField(primary_key=True)
	name=models.CharField(max_length=50,null=True)
	email=models.CharField(max_length=50)
	contact=models.CharField(max_length=50)
	date_created=models.DateTimeField(auto_now=True)
	# status=models.BooleanField()    
	  
	def __str__(self):
		return self.name