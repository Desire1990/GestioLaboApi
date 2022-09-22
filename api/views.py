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

class LaboratoireViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Laboratoire.objects.all()
	serializer_class = LaboratoireSerializer



class UserViewSet(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = User.objects.all()
	serializer_class = UserSerializer

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data
		user = User(
			username = data.get("username"),
			first_name = data.get("first_name"),
			last_name = data.get("last_name"),
		)
		user.set_password("password")
		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 201)

	@transaction.atomic
	def update(self, request, *args, **kwargs):
		data = request.data
		user = self.get_object()
		if not request.user.is_superuser:
			if(user.id != request.user.id):
				return Response(
					{'status': "permissions non accordée"}
				, 400)

		username = data.get("username")
		if username:user.username = username

		last_name = data.get("last_name")
		if last_name : user.last_name = last_name

		first_name = data.get("first_name")
		if first_name : user.first_name = first_name

		password = data.get("password")
		if password : user.set_password(password)

		is_active = data.get("is_active")
		if is_active!=None : user.is_active = is_active

		group = data.get("group")
		if group:
			user.groups.clear()
			user.is_superuser = False
			if group == "admin":
				user.is_superuser = True
			else:
				try:
					group = Group.objects.get(name=group)
					user.groups.add(group)
				except:
					return Response({"status":"groupe invalide"}, 400)

		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 200)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		user = self.get_object()
		user.is_active = False
		user.save()
		return Response({'status': 'success'}, 204)

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
	search_fields = ['name', 'domain__id']

class ProductViewset(mixins.ListModelMixin,
					mixins.UpdateModelMixin,
					mixins.RetrieveModelMixin,
					mixins.CreateModelMixin,
					viewsets.GenericViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated]
	queryset = Product.objects.all()
	pagination_class = Pagination
	serializer_class = ProductSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'category': ['exact'],
	}
	search_fields = ['category__name','materiel','designation','reference', 'quantite', 'date_peremption', 'unite']
	
	def get_queryset(self):
		queryset = Product.objects.all().order_by('-id')
		du = self.request.query_params.get('du')
		au = self.request.query_params.get('au')

		if du is not None:
			queryset = queryset.filter(date__gte=du, date__lte=au)
		return queryset


	@transaction.atomic
	def create(self, request, *args, **kwargs):
		data = request.data
		cat = data.get("category")
		category = None
		if(cat.get("name")):
			category, created = Category.objects.get_or_create(
				name = cat.get("name")
			)
			category.save()
		designation = data.get("designation")
		materiel = data.get("materiel")
		quantite = int(data.get("quantite"))
		reference = data.get("reference")
		status = data.get("status")
		date_peremption = data.get("date_peremption")
		unite = data.get("unite")
		produit = Product(
			date_peremption=date_peremption,status=status,unite=unite,designation=designation, materiel=materiel,quantite=quantite,reference=reference, category=category
		)
		produit.save()
		serializer = ProductSerializer(produit, many=False)
		return Response(serializer.data, 201)


class BonLivraisonViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = BonLivraison.objects.all()
	pagination_class = Pagination
	serializer_class = BonLivraisonSerializer
	filter_backends = (filters.SearchFilter,)
	filterset_fields = {
		'produit': ['exact'],
	}
	search_fields = ['num_commande','produit__reference']

	def get_queryset(self):
		return BonLivraison.objects.filter(user=self.request.user)

class BonLivraisonItemsViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = BonLivraisonItems.objects.all()
	pagination_class = Pagination
	serializer_class = BonLivraisonItemsSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'bonLivraison': ['exact'],
	}
	search_fields = ['qte_livree', 'bonLivraison__id']


class CommandeViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Commande.objects.all()
	pagination_class = Pagination
	serializer_class = CommandeSerializer
	filter_backends = (filters.SearchFilter,)
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'user': ['exact'],
	}

	search_fields = ['num_commande','date_commande','laboratoire__name', 'user__username']

	def get_queryset(self):
		return Commande.objects.filter(user=self.request.user)

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		data = request.data
		labo = data.get("laboratoire")
		laboratoire = None
		if(labo.get("name")):
			laboratoire, created = Laboratoire.objects.get_or_create(
				name = labo.get("name")
			)
			laboratoire.save()
		num_commande = data.get("num_commande")
		commande = Commande(
			user=request.user, num_commande=num_commande, laboratoire=laboratoire
		)
		commande.save()		
		for item in data.get("items"):
			product:Product = Product.objects.get(id=item.get("product"))
			quantite = int(item.get("quantity"))
			commandeitems = CommandeItem(
				product=product, commande=commande, qte_commande=quantite
			)
			commandeitems.save()
			# if product.quantite<quantite:
			# 	return Response({"status":"quantite demande est insuffisant en stock"}, 403)
			# else:
				# product.quantite-=quantite
				# product.save();
				
			product.quantite-=quantite
			product.save();
			serializer = CommandeItemSerializer(CommandeItem, many=False)
		commande.save()
		serializer = CommandeSerializer(commande, many=False)
		return Response(serializer.data, 201)

class CommandeItemViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = CommandeItem.objects.all()
	pagination_class = Pagination
	serializer_class = CommandeItemSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'commande': ['exact'],
	}
	search_fields = ['quantity', 'commande__id']


class OrderViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = Order.objects.all()
	pagination_class = Pagination
	serializer_class = OrderSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('name',)

	# def get_queryset(self):
	# 	return Order.objects.filter(professeur=self.request.professeur)



class OrderItemViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = OrderItem.objects.all()
	pagination_class = Pagination
	serializer_class = OrderItemSerializer
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'order': ['exact'],
	}
	search_fields = ['quantity', 'order__id']






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
