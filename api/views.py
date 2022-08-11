from .dependency import *

class Pagination(PageNumberPagination):
	page_size = 15
	def get_paginated_response(self, data):
		return Response(OrderedDict([
			('next', self.get_next_link()),
			('previous', self.get_previous_link()),
			('count', self.page.paginator.count),
			('page', self.page.number),
			('num_page', self.page.paginator.num_pages),
			('results', data)
		]))

class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer


class GroupViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Group.objects.all()
	serializer_class = GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all().order_by('-id')
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	# modification mot de passe

	@transaction.atomic()
	def update(self, request, pk):
		user = self.get_object()
		print(user)
		data = request.data
		username = data.get('username')
		first_name = data.get('first_name')
		last_name = data.get('last_name')
		nouv_password = data.get('nouv_password')
		anc_password = data.get('anc_password')
		if user.check_password(anc_password):
			print("checked")
			user.username = username
			user.first_name = first_name
			user.last_name = last_name
			user.set_password(nouv_password)
			user.save()
			return Response({"status": "Utilisateur modifié avec success"}, 201)
		return Response({"status": "Ancien mot de passe incorrect"}, 400)

# Views for Admins

class DecanatViewset(viewsets.ModelViewSet):
	serializer_class = DecanatSerializer
	queryset = Decanat.objects.all().order_by('name')
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	search_fields = ['name']
	filterset_fields = ['name']

	def get_queryset(self):
		queryset = Decanat.objects.all().order_by('name')
		du = self.request.query_params.get('du')
		au = self.request.query_params.get('au')

		if du is not None:
			queryset = queryset.filter(date__gte=du, date__lte=au)
		return queryset

	@transaction.atomic()
	def create(self, request):
		data = request.data
		name = data.get('name')
		decanat: Decanat = Decanat(
			user=request.user,
			decanat=decanat
		)
		dpe.save()
		serializer = DecanatSerializer(dpe, many=False).data
		return Response({"status": "Decanat cree avec succès"}, 201)


class DepartementViewset(viewsets.ModelViewSet):
	serializer_class = DepartementSerializer
	queryset = Departement.objects.all().order_by('decanat__name', 'name')
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'decanat': ['exact'],
	}
	search_fields = ['name', 'decanat__name']

	@transaction.atomic()
	def create(self, request):
		data = request.data
		dec: Decanat = Decanat.objects.get(id=int(data.get('dec')))
		name = data.get('name')
		dep: Departement = Departement(
			user=request.user,
			dec=dec,
			name=name
		)
		dep.save()
		serializer = DCESerializer(dep, many=False).data
		return Response({"status": "Departement cree avec succès"}, 201)


class UtilisateurViewset(viewsets.ModelViewSet):
	serializer_class = UtilisateurSerializer
	queryset = Utilisateur.objects.all().order_by('-id')
	#authentication_classes = [JWTAuthentication, SessionAuthentication]
	#permission_classes = IsAuthenticated,
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	search_fields = ['user__username', 'user__first_name',
					 'user__last_name', 'departement__name', 'decanat__name']

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		departement = serializer.validated_data['departement']
		decanat = serializer.validated_data['decanat']
		user = User(
			username=serializer.validated_data['user']['username'],
			first_name=serializer.validated_data['user']['first_name'],
			last_name=serializer.validated_data['user']['last_name'],
			email=serializer.validated_data['user']['email']
		)
		user.set_password(serializer.validated_data['user']['password'])
		utilisateur = Utilisateur(
			user=user,
			decanat=decanat,
			departement=departement,
		)
		user.save()
		groups = serializer.validated_data['user']['groups']
		print(serializer.validated_data['user'])
		for group in groups:
			user.groups.add(group)
			user.save()
		utilisateur.save()
		serializer = UtilisateurSerializer(utilisateur, many=False).data
		return Response({"status": "Utilisateur cree avec succès"}, 201)

	@transaction.atomic()
	@action(methods=['GET'], detail=False, url_path=r"reset/(?P<email>[a-zA-Z0-9.@]+)", url_name=r'reset')
	def rest_password(self, request, email):
		queryset = User.objects.filter(email=email)
		if(not queryset):
			return Response({"details": "email invalide"}, 400)

		user: user = queryset.first()

		# if (user.utilisateur.reset !=None):
		# 	return Response({"details":"compte en pleine reinitialisation"},400)

		utilisateur: Utilisateur = user.utilisateur
		reset = randint(100000, 999999)
		utilisateur.reset = reset
		utilisateur.save()

		send_mail(
			subject=f"{reset} est votre code de réinitialisation de votre compte Approsco",
			message=f"Nous avons reçu une demande de réinitialisation de votre mot de passe Approsco. \nEntrez le code de réinitialisation du mot de passe suivant: \n\n{reset}\n\nVous n'avez pas demandé ce changement?\nSi vous n'avez pas demandé de nouveau mot de passe, veuillez signaler votre Administrateur.",
			from_email=None,
			recipient_list=[email],
			fail_silently=False,
		)
		return Response({'status': 'reussie'}, 200)

	@transaction.atomic()
	@action(methods=['POST'], detail=False, url_path=r"changePassword", url_name=r'changePassword', serializer_class=PasswordResetSerializer)
	def changepassword(self, request):
		reset_code = request.data['reset_code']
		new_password = request.data['new_password']

		utilisateurs = Utilisateur.objects.filter(reset=reset_code)
		if utilisateurs:
			utilisateur = utilisateurs.first()
			user = utilisateur.user
			user.set_password(new_password)
			user.save()
			utilisateur.reset = None
			utilisateur.save()
			return Response({"status": "succes"}, 200)
		else:
			return Response({"status": "echec"}, 401)




class DomainViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Domain.objects.all()
	pagination_class = Pagination
	serializer_class = DomainSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('name',)

class CategoryViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Category.objects.all()
	pagination_class = Pagination
	serializer_class = CategorySerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'domain': ['exact'],
	}
	search_fields = ['name', 'domain__name']

class ProductViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Product.objects.all()
	pagination_class = Pagination
	serializer_class = ProductSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'category': ['exact'],
	}
	search_fields = ['name', 'category__name']

	@transaction.atomic
	def create(self, request):
		data = self.request.data
		category: Category = Category.objects.get(id=(data.get('category')))
		materiel = (data.get('materiel'))
		reference = (data.get('reference'))
		designation = (data.get('designation'))
		quantite = (data.get('quantite'))
		unite = (data.get('unite'))
		date_peremption = (data.get('date_peremption'))
		product = Product(
			category=category,
			materiel=materiel,
			reference=reference,
			designation=designation,
			quantite=quantite,
			unite=unite,
			date_peremption=date_peremption,
			)

		product.save()
		serializer = ProductSerializer(product, many=False, context={"request":request}).data
		return Response(serializer,200)

	def update(self, request):
		pass
	def destroy():
		pass

class OrderViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Order.objects.all()
	pagination_class = Pagination
	serializer_class = OrderSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('name',)


class OrderItemViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = OrderItem.objects.all()
	pagination_class = Pagination
	serializer_class = OrderItemSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('quantity',)

class DeliveryViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Delivery.objects.all()
	pagination_class = Pagination
	serializer_class = DeliverySerializer
	filter_backends = (filters.SearchFilter,)
	# search_fields = ('name',)

class ChangePasswordView(generics.UpdateAPIView):
	"""
	An endpoint for changing password.
	"""
	serializer_class = ChangePasswordSerializer
	model = User
	permission_classes = (IsAuthenticated,)

	def get_object(self, queryset=None):
		obj = self.request.user
		return obj

	def update(self, request, *args, **kwargs):
		self.object = self.get_object()
		serializer = self.get_serializer(data=request.data)

		if serializer.is_valid():
			# Check old password
			if not self.object.check_password(serializer.data.get("old_password")):
				return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
			# set_password also hashes the password that the user will get
			self.object.set_password(serializer.data.get("new_password"))
			self.object.save()
			response = {
				'status': 'success',
				'code': status.HTTP_200_OK,
				'message': 'Password updated successfully',
				'data': []
			}

			return Response(response)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
	email_plaintext_message = "Copy the token value in token field in your reset password page.\n Your token is ={}".format(reset_password_token.key)

	send_mail(
		# title:
		"Password Reset for {title}".format(title="initializing the logins"),
		# message:
		email_plaintext_message,
		# from:
		"noreply@somehost.local",
		# 'support@redgoldinvest.com',
		# to:
		[reset_password_token.user.email]
	)



class CommandeViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Commande.objects.all()
	pagination_class = Pagination
	serializer_class = CommandeSerializer
	filter_backends = (filters.SearchFilter,)

	search_fields = ('num_commande',)

class CommandeItemViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = CommandeItem.objects.all()
	pagination_class = Pagination
	serializer_class = CommandeItemSerializer
	filter_backends = (filters.SearchFilter,)

	search_fields = ('qte_commande',)