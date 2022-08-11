from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import *
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class LastLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastLogin
        fields = "__all__"


class TokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(TokenPairSerializer, self).validate(attrs)
        data['groups'] = [group.name for group in self.user.groups.all()]
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        if self.user.utilisateur.dec:
            var = self.user.utilisateur
            data['dec'] = DecanatSerializer(var.dec, many=False).data
        if self.user.utilisateur.dep:
            var = self.user.utilisateur
            data['dep'] = DepSerializer(var.dep, many=False).data
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
        representation['dec'] = DecanatSerializer(instance.dec, many=False).data
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
        representation['dep'] = DepartementSerializer(instance.dep, many=False).data
        representation['dec'] = DecanatSerializer(instance.dec, many=False).data
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

        instance.dep = validated_data.get('dep', instance.dep)
        instance.dec = validated_data.get('dec', instance.dec)
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
            'order',
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


class ApprovisionnementSerializer(serializers.ModelSerializer):
	class Meta:
		model = Approvisionnement
		fields = "__all__"


class ApprovisionnementSerializer(serializers.ModelSerializer):
	class Meta:
		model = Approvisionnement
		fields = "__all__"


class ApprovisionnementSerializer(serializers.ModelSerializer):
	class Meta:
		model = Approvisionnement
		fields = "__all__"


class LigneApprovisionnementSerializer(serializers.ModelSerializer):
	class Meta:
		model = LigneApprovisionnement
		fields = "__all__"


class ApprovisionnementSerializer(serializers.ModelSerializer):
	class Meta:
		model = Approvisionnement
		fields = "__all__"


class BonDeReceptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = BonDeReception
		fields = "__all__"


class LigneBonDeReceptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = LigneBonDeReception
		fields = "__all__"

class CommandeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Commande
		fields = "__all__"

class LigneCommandeSerializer(serializers.ModelSerializer):
	class Meta:
		model = LigneCommande
		fields = "__all__"

class BonLivraisonSerializer(serializers.ModelSerializer):
	class Meta:
		model = BonLivraison
		fields = "__all__"

class LigneBonLivraisonSerializer(serializers.ModelSerializer):
	class Meta:
		model = LigneBonLivraison
		fields = "__all__"

