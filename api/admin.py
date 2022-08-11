from django.contrib import admin
from .models import*

# Register your models here.
admin.site.register(Domain)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(LastLogin)
admin.site.register(Order)
admin.site.register(Delivery)
admin.site.register(OrderItem)
admin.site.register(Decanat)
admin.site.register(Departement)
admin.site.register(Commande)
admin.site.register(LigneCommande)
admin.site.register(BonLivraison)
admin.site.register(LigneBonLivraison)
admin.site.register(Approvisionnement)
admin.site.register(LigneApprovisionnement)
admin.site.register(BonDeReception)
admin.site.register(LigneBonDeReception)
