from django.urls import path, include
from rest_framework import routers
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = routers.DefaultRouter()
router.register("user",UserViewSet)
router.register("utilisateur",UtilisateurViewset)
router.register("groups",GroupViewSet)
router.register("labo",LaboratoireViewSet)
router.register("Departement",DepartementViewset)
router.register("decanat",DecanatViewset)
router.register("domain",DomainViewset)
router.register("category",CategoryViewset)
router.register("produit",ProductViewset)
router.register("order",OrderViewset)
router.register("orderItem",OrderItemViewset)
router.register("commande",CommandeViewset)
router.register("commandeItem",CommandeItemViewset)
router.register("bonLivraison",BonLivraisonViewset)
router.register("bonLivraisonItems",BonLivraisonItemsViewset)


urlpatterns = [
	path('', include(router.urls)),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
	path('api_auth', include('rest_framework.urls')),


]
