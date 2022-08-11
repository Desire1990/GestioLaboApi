from django.urls import path, include, re_path
from rest_framework import routers
from .views import *
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView, UserDetailsView

router = routers.DefaultRouter()
router.register("user",UserViewSet)
router.register("utilisateur",UtilisateurViewset)
router.register("groups",GroupViewSet)
router.register("Departement",DepartementViewset)
router.register("decanat",DecanatViewset)
router.register("domain",DomainViewset)
router.register("category",CategoryViewset)
router.register("product",ProductViewset)
router.register("order",OrderViewset)
router.register("orderItem",OrderItemViewset)
router.register("delivery",DeliveryViewset)
router.register("commande",CommandeViewset)
router.register("commandeItem",CommandeItemViewset)


app_name='api'

urlpatterns = [
	path("", include(router.urls)),
	path('change-password/', ChangePasswordView.as_view(), name='change-password'),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
	path('logout/', LogoutView.as_view()),
	path('password/reset/', PasswordResetView.as_view()),
	path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
	path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
	# path('register/', RegisterView.as_view(), name='auth_register'),
	# path('reset/', views.Reset),
]