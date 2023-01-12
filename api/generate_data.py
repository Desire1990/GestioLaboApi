from uuid import uuid4
from faker import Faker
from faker.providers import BaseProvider
from datetime import datetime
import random
import csv

class DomainProvider(BaseProvider):
    def product_domain(self):
        return random.choice(['Appareillage', 'Vannerie et Associe', 'Classe de terrain', 'Science de la Terre', 'Produit chimique', 'Materiel de laboratoire ', 'Medias', 'Lames minces'])

class CategoriesProvider(BaseProvider):
    def product_categories(self):
        return random.choice(['Observation', 'mesures', 'ExAO', 'Multimedia', 'Experimentation', 'Divers', 'Vanneries', 'associes','materiel dissection','etres vivants', 'culture-elevage', 'Modeles-anatomies','Kits pedagogiques', 'Roches', 'Mineraux', 'Fossiles/prehistoires', 'Modeles', 'cartes', 'Observation', 'recoltes geographiques','recoltes biologiques', 'traitement recoltes', 'securites', 'Produit\'organiques', 'Produit mineral', 'Enzymes/hormones', 'colorants', 'entretien', 'appareil de labo', 'fournitures', 'Mobiliers','logiciels', 'manuels scolaires', 'livres sciientifiques','Geologie', 'Botaniques', 'Zoologie', 'Histologie', 'Developpement', 'Microbiologie'])

class UnitProvider(BaseProvider):
    def get_unit(self):
        return random.choice(['l', 'ml', 'g', 'kg', 'pc(s)', 'lot(s)'])

fake = Faker()

fake.add_provider(DomainProvider)
fake.add_provider(UnitProvider)
fake.add_provider(CategoriesProvider)

# Some of this is a bit verbose now, but doing so for the sake of completion
def mef(m):
    def _mef(x):
        return getattr(x, m)()
    return _mef

def get_product_name():
    words = fake.words()
    capitalized_words = list(map(mef('capitalize'), words))
    return ' '.join(capitalized_words)

def get_date():
    return datetime.strftime(fake.date_time_this_decade(), "%B %d, %Y")

def get_product_quantity():
    return random.randrange(50, 1500)

def get_product_reference():
    return random.randrange(500, 15000)


def get_price():
    return round(random.uniform(100000.0, 5000000.0), 50)

domains = ['Appareillage', 'Vannerie et Associe', 'Classe de terrain', 'Science de la Terre', 'Produit chimique', 'Materiel de laboratoire ', 'Medias', 'Lames minces']
def get_commandeId():
    for domain in domains:
        unique_id = str(uuid4())
        return unique_id

def generate_data():
    return [
            get_date(), 
            get_product_reference(), 
            fake.product_domain(), 
            fake.product_categories(),
            get_product_name(),
            get_commandeId(),
            get_product_quantity(), 
            get_price(), 
            fake.get_unit()
            ]

with open('commande_data.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date','CommandeId','Domain','Categorie','materiel','Reference','Quantite','Prix','Unite'])
    for n in range(1, 10000):
        writer.writerow(generate_data())
