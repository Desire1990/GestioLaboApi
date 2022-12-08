from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

# class LastLoginSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = LastLogin
# 		fields = "__all__"

class LaboratoireSerializer(serializers.ModelSerializer):

	class Meta:
		model = Laboratoire
		fields = ('id', 'name')

class TokenPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['groups'] = [group.name for group in self.user.groups.all()]
		data['id'] = self.user.id
		data['username'] = self.user.username
		data['first_name'] = self.user.first_name
		data['last_name'] = self.user.last_name
		if self.user.utilisateur.decanat:
			var = self.user.utilisateur
			data['decanat'] = DecanatSerializer(var.decanat, many=False).data
		if self.user.utilisateur.departement:
			var = self.user.utilisateur
			data['departement'] = DepartementSerializer(var.departement, many=False).data
		data['is_staff'] = self.user.is_staff
		return data


class GroupSerializer(serializers.ModelSerializer):

	class Meta:
		model = Group
		fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
	@transaction.atomic()
	def update(self, instance, validated_data):
		user = instance
		username = validated_data.get('username')
		first_name = validated_data.get('first_name')
		last_name = validated_data.get('last_name')
		nouv_password = validated_data.get('nouv_password')
		anc_password = validated_data.get('anc_password')
		if check_password(anc_password, self.context['request'].user.password):
			if username:
				user.username = username
			if first_name:
				user.first_name = first_name
			if last_name:
				user.last_name = last_name
			if password:
				user.set_password(password)
			user.save()
			return user
		return user

	class Meta:
		model = User
		read_only_fields = "is_active", "is_staff"
		exclude = "last_login", "is_staff", "date_joined"
		extra_kwargs = {
			'username': {
				'validators': [UnicodeUsernameValidator()]
			}
		}



class DecanatSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['user'] = UserSerializer(instance.user, many=False).data
		user = UserSerializer(instance.user, many=False).data
		representation['user'] = {'id': user.get(
			'id'), 'username': user.get('username')}
		return representation

	class Meta:
		model = Decanat
		fields = "__all__"


class DepartementSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['user'] = UserSerializer(instance.user, many=False).data
		representation['decanat'] = DecanatSerializer(instance.decanat, many=False).data
		return representation

	class Meta:
		model = Departement
		fields = "__all__"


class UtilisateurSerializer(serializers.ModelSerializer):
	def to_representation(self, instance):
		representation = super().to_representation(instance)
		user = User.objects.get(id=instance.user.id)
		group = [group.name for group in user.groups.all()]
		representation['user'] = {'id': user.id, 'username': user.username,
								  'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'groups': group}
		representation['departement'] = DepartementSerializer(instance.departement, many=False).data
		representation['decanat'] = DecanatSerializer(instance.decanat, many=False).data
		return representation
	user = UserSerializer()

	def update(self, instance, validated_data):
		user = instance.user
		print(validated_data)
		user_data = validated_data.pop('user')
		username = user_data.get('username')
		first_name = user_data.get('first_name')
		last_name = user_data.get('last_name')
		email = user_data.get('email')
		password = user_data.get('password')

		if username:
			user.username = username
		if first_name:
			user.first_name = first_name
		if last_name:
			user.last_name = last_name
		if email:
			user.email = email
		if password:
			user.set_password(password)

		instance.departement = validated_data.get('departement', instance.departement)
		instance.decanat = validated_data.get('decanat', instance.decanat)
		group_user = user_data.get('groups')
		print(user)
		print(group_user)
		user.groups.clear()
		user.groups.add(group_user[0])
		user.save()
		instance.save()
		return instance

	class Meta:
		model = Utilisateur
		fields = "__all__"


class PasswordResetSerializer(serializers.Serializer):
	reset_code = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id','category','status','unite','status', 'materiel','designation','reference', 'quantite','unite', 'get_absolute_url', 'date_peremption')
		# fields = '__all__'
		depth=1


class CategorySerializer(serializers.ModelSerializer):
	produit = ProductSerializer(many=True, read_only=True)
	class Meta:
		model = Category
		fields = ('id', 'name','produit', 'domain')
		depth=1
class DomainSerializer(serializers.HyperlinkedModelSerializer):
	# url = serializers.HyperlinkedIdentityField(view_name="api:domain-detail")
	category = CategorySerializer(many=True, read_only=True)
	class Meta:
		model = Domain
		fields = "__all__"
		fields = ('id','category', 'name','get_thumbnail', 'date_added')
		depth=1

class BonLivraisonItemsSerializer(serializers.ModelSerializer):
	class Meta:
		model = BonLivraisonItems
		fields = "__all__"
		# fields = ('produit','bonLivraison','qte_livree','qte_restante',)
		depth=2

class BonLivraisonSerializer(serializers.ModelSerializer):
	items_bons = BonLivraisonItemsSerializer(many=True)
	class Meta:
		model = BonLivraison
		fields='__all__'
		# fields = ('items_bons','user', 'laboratoire', 'date_livraison', 'num_bon')
		depth=2

	def create(self, validated_data):
		""" override create method """
		items_data = validated_data.pop('items_bons') # remove items from validated_data
		# order create 
		order = BonLivraison.objects.create(**validated_data)

		# order_item save 
		for item_data in items_data:
			BonLivraisonItem.objects.create(order=order, **item_data)
		return order

class CommandeItemSerializer(serializers.ModelSerializer):

	class Meta:
		model = CommandeItem
		fields = (
			'commande',
			# 'item',
			'product',
			'qte_commande',
			'unite',
		)
		depth=1



class CommandeSerializer(serializers.ModelSerializer):
	items = CommandeItemSerializer(many=True)
	
	class Meta:
		model = Commande
		fields='__all__'
		depth=2

	def create(self, validated_data):
		""" override create method """
		items_data = validated_data.pop('items') # remove items from validated_data
		# order create 
		commande = Commande.objects.create(**validated_data)

		# order_item save 
		for item in items_data:
			CommandeItem.objects.create(commande=commande, **item)
		return commande

class OrderItemSerializer(serializers.ModelSerializer):

	class Meta:
		model = OrderItem
		fields ="__all__"
		depth=3



class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True)
	class Meta:
		model = Order
		fields = '__all__'
		depth=3
	def create(self, validated_data):
		""" override create method """
		items_data = validated_data.pop('items') # remove items from validated_data
		# order create 
		order = Order.objects.create(**validated_data)

		# order_item save 
		for item_data in items_data:
			OrderItem.objects.create(order=order, **item_data)
		return order



class ChangePasswordSerializer(serializers.Serializer):
	model = User

	"""
	Serializer for password change endpoint.
	"""
	old_password = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)


