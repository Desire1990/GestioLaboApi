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

import barcode                      # additional imports for bar code
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File

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

class Laboratoire(models.Model):
	id=models.SmallAutoField(primary_key=True)
	name = models.CharField(max_length=200)
	date_added=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.name}'



# cas de stock des Products central
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
		return f"{self.name}-{self.domain.name}"	

class Product(models.Model):
	id=models.SmallAutoField(primary_key=True)
	category = models.ForeignKey(Category,related_name='produit', on_delete=models.CASCADE)
	materiel = models.CharField(max_length=200)
	reference = models.CharField(unique=True,max_length=50)
	designation = models.TextField()
	quantite = models.FloatField(default=0)
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, null=True, blank=True)
	date_reception = models.DateTimeField(_('Caractéristiques complémentaires'),auto_now_add=True)
	date_peremption = models.DateTimeField()
	# barcode = models.ImageField(upload_to='products/codes',blank=True)
	class Meta:
		ordering = ('id',)
		verbose_name = 'product'
		verbose_name_plural = 'products'

	def __str__(self):
		return '{} {}'.format(self.reference, self.quantite)

	def get_absolute_url(self):
		return f'/{self.materiel}/'

	# def save(self, *args, **kwargs):          # overriding save() 
	# 	COD128 = barcode.get_barcode_class('code128')
	# 	rv = BytesIO()
	# 	code = COD128(f'{self.reference}', writer=ImageWriter()).write(rv)
	# 	self.barcode.save(f'{self.reference}.png', File(rv), save=False)
	# 	return super().save(*args, **kwargs)




# commandes pour les Laboratoires vers le stock central

class Commande(models.Model):
	id=models.SmallAutoField(primary_key=True)
	utilisateur = models.ForeignKey("Utilisateur", on_delete=models.CASCADE)
	# laboratoire = models.ForeignKey(Laboratoire, on_delete=models.CASCADE)
	num_commande = models.CharField(max_length=50)
	date_commande = models.DateTimeField(auto_now_add=True)
	date_livraison = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	envoye = models.BooleanField(default=False) # labo
	envoyee = models.BooleanField(default=False)#departement
	envoyeee = models.BooleanField(default=False)#decanat
	
	def __str__(self):
		return f'{self.num_commande}-{self.utilisateur.user.username}'


	class Meta:
		ordering = ('-date_commande',)
class CommandeItem(models.Model):
	id=models.SmallAutoField(primary_key=True)
	commande = models.ForeignKey(Commande,related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_commande = models.FloatField(default=0)
	unite = models.CharField(choices=UNITE_CHOICE, max_length=200, null=True)
	
	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return str(self.commande)    

class BonLivraison(models.Model):
	id=models.SmallAutoField(primary_key=True)
	utilisateur = models.ForeignKey("Utilisateur", on_delete=models.CASCADE)
	# laboratoire = models.ForeignKey(Laboratoire, on_delete=models.CASCADE)
	commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
	num_bon = models.CharField(max_length=50)
	date_commande = models.DateTimeField(auto_now_add=True)
	date_livraison = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')	
	envoye = models.BooleanField(default=False)
	envoyee = models.BooleanField(default=False)
	envoyeee = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.num_bon}-{self.commande.utilisateur.user}'



class BonLivraisonItems(models.Model):
	id=models.SmallAutoField(primary_key=True)
	bonLivraison = models.ForeignKey(BonLivraison,related_name='items_bons', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_livree = models.FloatField(default=0)
	qte_restante = models.FloatField(default=0, editable=False)
	unite = models.CharField(choices=UNITE_CHOICE, max_length=200, null=True)

	class Meta:
		ordering = ('-id',)
	
	def __str__(self):
		return str(self.bonLivraison.utilisateur.user)

# order in labos
class Order(models.Model):
	id=models.SmallAutoField(primary_key=True)
	utilisateur = models.ForeignKey("Utilisateur", on_delete=models.PROTECT)
	num_order = models.CharField(max_length=50)
	bonLivraison = models.ForeignKey(BonLivraison, on_delete=models.CASCADE)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	envoye = models.BooleanField(default=False)
	envoyee = models.BooleanField(default=False)
	
	class Meta:
		ordering = ('-id',)
		
	def __str__(self):
		return self.num_order

class OrderItem(models.Model):
	id=models.SmallAutoField(primary_key=True)
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
	quantity = models.FloatField(default=1)
	unite = models.CharField(choices=UNITE_CHOICE, max_length=200, null=True)


	def __str__(self):
		return f'{self.order} - {self.product}'

	class Meta:
		ordering = ('-id',)
		



# responsable de labo et chef de departema ainsi que le Doyen pour approbation, admin et autres interacteurs
# cas d'extrat pour identifier les beneficieres(laboratoires)

# class Faculte(models.Model):
# 	id = models.SmallAutoField(primary_key=True)
# 	user = models.ForeignKey(User, related_name='user_fac',on_delete=models.PROTECT)
# 	name = models.CharField(max_length=200, null=False, blank=False)
# 	created_date = models.DateTimeField(auto_now_add=True)
	
# 	def __str__(self):
# 		return self.name

class Decanat(models.Model):
	id = models.SmallAutoField(primary_key=True)
	# faculte = models.ForeignKey(Faculte, on_delete=models.PROTECT)
	user = models.ForeignKey(User, related_name='user_decanat',on_delete=models.PROTECT)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.name

class Departement(models.Model):
	id = models.SmallAutoField(primary_key=True)	
	user = models.ForeignKey(User, related_name='user_departement',on_delete=models.PROTECT)
	decanat = models.ForeignKey(Decanat, related_name='decanat_departement', on_delete=models.PROTECT)
	name = models.CharField(max_length=200, null=False, blank=False)
	created_date = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.name
	
	class Meta:
		ordering = ('-id',)
		

class Professeur(models.Model):
	id = models.BigAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)
	departement = models.ForeignKey(Departement, related_name='Utilisateur_prof',on_delete=models.PROTECT, null=True, blank=True)
	date_created=models.DateTimeField(auto_now=True)
	# status=models.BooleanField()    
	  
	def __str__(self):
		return f"{self.user.username}"
	class Meta:
		ordering = ('-id',)
		
class Utilisateur(models.Model):
	id = models.BigAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)
	# professeur = models.ForeignKey(Professeur, related_name='professeur',on_delete=models.PROTECT, null=True, blank=True)
	departement = models.ForeignKey(Departement, related_name='Utilisateur_departement',on_delete=models.PROTECT, null=True, blank=True)
	decanat = models.ForeignKey(Decanat, related_name='Utilisateur_decanat',on_delete=models.PROTECT, null=True, blank=True)
	date = models.DateTimeField(auto_now_add=True)
	reset=models.CharField(max_length=6,null=True,editable=False) 

	def __str__(self):
		return f"{self.user}"
	class Meta:
		ordering = ('-id',)
		