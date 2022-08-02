from .dependency import *

class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer

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

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	pagination_class = Pagination
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated,IsAdminUser ]

	def get_queryset(self):
		return User.objects.filter(email = self.request.user)

	# Add this code block
	def get_permissions(self):
		permission_classes = []
		if self.action == 'create':
			permission_classes = [AllowAny]
		elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
			permission_classes = [IsLoggedInUserOrAdmin]
		elif self.action == 'list' :
			permission_classes = [IsLoggedInUserOrAdmin]		
		elif self.action == 'destroy':
			permission_classes = [IsAdminUser]
		return [permission() for permission in permission_classes]


class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	permission_classes = (AllowAny,)
	serializer_class = RegisterSerializer
	

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
		status = (data.get('status'))
		date_peremption = (data.get('date_peremption'))
		product = Product(
			category=category,
			materiel=materiel,
			reference=reference,
			designation=designation,
			quantite=quantite,
			unite=unite,
			status=status,
			date_peremption=date_peremption,
			)

		product.save()
		serializer = ProductSerializer(product, many=False, context={"request":request}).data
		return Response(serializer,200)


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
	search_fields = ('quantite',)

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
		# "noreply@somehost.local",
		'support@redgoldinvest.com',
		# to:
		[reset_password_token.user.email]
	)

