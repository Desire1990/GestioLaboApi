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
	slug = models.SlugField(max_length=200, null=True)
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
	# user = models.ForeignKey(User, on_delete=models.CASCADE)
	materiel = models.CharField(max_length=200)
	reference = models.CharField(unique=True,max_length=50)
	designation = models.TextField()
	quantite = models.IntegerField()
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICE, null=True, blank=True)
	date_reception = models.DateTimeField(_('Caractéristiques complémentaires'),auto_now_add=True)
	date_peremption = models.DateTimeField(auto_now_add=True)
	# price = models.DecimalField(max_digits=8, decimal_places=2)
	# supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
	class Meta:
		ordering = ('-date_reception',)
		verbose_name = 'product'
		verbose_name_plural = 'products'

	def __str__(self):
		return '{} '.format(self.reference)


# place d'approvisionnement
class Approvisionnement(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	num_approvisionnement = models.CharField(max_length=50, unique=True)
	date_approvisionnement = models.DateTimeField(auto_now_add=True)
	date_reception = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.date_approvisionnement)

class LigneApprovisionnement(models.Model):
	approvisionnement = models.ForeignKey(Approvisionnement, on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantite = models.IntegerField()
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	# prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
	# prix_total = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
		
	
	def __str__(self):
		return str(self.quantite)
class BonDeReception(models.Model):
	num_bon_reception = models.CharField(max_length=50, unique=True)
	date_bon_reception = models.DateTimeField(auto_now_add=True)
	approvisionnement = models.ForeignKey(Approvisionnement, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.date_bon_reception)   
	
class LigneBonDeReception(models.Model):
	bon_de_reception = models.ForeignKey(BonDeReception, on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_commandee = models.IntegerField()
	qte_recue = models.IntegerField()
	qte_restante = models.IntegerField()
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.bon_de_reception)         

# commandes pour les Laboratoires
class Commande(models.Model):
	num_commande = models.CharField(max_length=50, default='')
	date_commande = models.DateTimeField(auto_now_add=True)
	date_livraison = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return str(self.num_commande)   
	
class LigneCommande(models.Model):
	commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_commande = models.IntegerField(default=0)
	qte_livree = models.IntegerField(default=0)
	qte_restante = models.IntegerField(default=0)
	# prix_unitaire =models.IntegerField(default=0)
	# prix_total = models.IntegerField(default=0)
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	# @property
	# def prix_total_commande(self):
	#     return self.qte_commande * self.prix_unitaire
	
	
	def __str__(self):
		return str(self.commande)   
class BonLivraison(models.Model):
	num_bon_livraison = models.CharField(max_length=50, default='')
	date_bon_livraison = models.DateField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return str(self.num_bon_livraison)
	
class LigneBonLivraison(models.Model):
	bon_livraison = models.ForeignKey(BonLivraison, on_delete=models.CASCADE)
	produit = models.ForeignKey(Product, on_delete=models.CASCADE)
	qte_bon_livraison = models.IntegerField(default=0)
	qte_livree = models.IntegerField(default=0)
	qte_restante = models.IntegerField(default=0)
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	
	def __str__(self):
		return str(self.bon_livraison)

# cas des commandes externe
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
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
	quantity = models.IntegerField(default=0)
	unite = models.CharField(max_length=20, choices=UNITE_CHOICE, null=True, blank=True)

	def __str__(self):
		return f'{self.order} - {self.product}'


class Delivery(models.Model):
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

