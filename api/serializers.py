from rest_framework.exceptions import NotFound
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum

from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.validators import ValidationError

from .models import *

from django.contrib.auth import get_user_model

User = get_user_model()


from rest_framework import serializers
class LastLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastLogin
        fields = "__all__"

class UserSerializer(serializers.HyperlinkedModelSerializer):
	"""
	Bifrost user writable nested serializer
	"""
	password = serializers.CharField(write_only=True)
	# groups = serializers.SerializerMethodField()
	url = serializers.HyperlinkedIdentityField(view_name="api:user-detail")


	# def get_groups(self, user):
	# 	groups = []
	# 	if user.is_superuser:
	# 		groups.append("admin")
	# 	for group in user.groups.all():
	# 		groups.append(group.name)
	# 	return groups

	class Meta:
		model = User
		fields = ('id',
				  'url',
				  'username',
				  'email',
				  'first_name', 
				  'last_name', 
				  'password',
				  'is_superuser',
				  'is_active',
				  'last_login',
				  'date_joined'
				)
		extra_kwargs = {'password': {'write_only': True}}

	def create(self, validated_data):
		# profile_data = validated_data.pop('profile')
		password = validated_data.pop('password')
		user = User(**validated_data)
		user.set_password(password)
		user.save()
		# UserProfile.objects.create(user=user, **profile_data)
		return user


class RegisterSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(
			required=True,
			validators=[UniqueValidator(queryset=User.objects.all())]
			)

	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
	password2 = serializers.CharField(write_only=True, required=True)

	class Meta:
		model = User
		fields = ('username', 
				  'password', 
				  'password2', 
				  'email', 
				  'first_name', 
				  'last_name',  

				  )
		extra_kwargs = {
			'first_name': {'required': True},
			'last_name': {'required': True},
		}

	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError({"password": "Password fields didn't match."})

		return attrs

	def create(self, validated_data):
		user = User.objects.create(
			username=validated_data['username'],
			email=validated_data['email'],
			first_name=validated_data['first_name'],
			last_name=validated_data['last_name'],
		)

		user.set_password(validated_data['password'])
		user.save()

		return user


class TokenPairSerializer(TokenObtainPairSerializer):

	def getGroups(self, user):
		groups = []
		if user.is_superuser:
			groups.append("admin")
		for group in user.groups.all():
			groups.append(group.name)
		return groups

	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['services'] = [group.name for group in self.user.groups.all()]
		data['is_admin'] = self.user.is_superuser
		data['groups'] = self.getGroups(self.user)
		data['username'] = self.user.username
		data['first_name'] = self.user.first_name
		data['last_name'] = self.user.last_name
		data['email'] = self.user.email
		data['id'] = self.user.id
		logins = LastLogin.objects.all()
		if(logins):
			last_login = logins.first()
			last_login.date = timezone.now()
			last_login.save()
		else:
			LastLogin().save()
		return data




class DomainSerializer(serializers.HyperlinkedModelSerializer):
	url = serializers.HyperlinkedIdentityField(view_name="api:domain-detail")
	class Meta:
		model = Domain
		fields = ('id', 'url', 'name', 'slug', 'date_added')

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = "__all__"
		# depth=2
class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = (
            # 'price',
            'product',
            'quantity',
        )
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        """ override create method """
        items_data = validated_data.pop('items') # remove items from validated_data
        # order create 
        order = Order.objects.create(**validated_data)

        # order_item save 
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order


class DeliverySerializer(serializers.ModelSerializer):
	class Meta:
		model = Delivery
		fields = "__all__"


class ChangePasswordSerializer(serializers.Serializer):
	model = User

	"""
	Serializer for password change endpoint.
	"""
	old_password = serializers.CharField(required=True)
	new_password = serializers.CharField(required=True)
