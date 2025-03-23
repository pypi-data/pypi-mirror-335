# Documentation du projet DatetimeEventStore

## Présentation

DatetimeEventStore est une bibliothèque Python permettant de stocker et récupérer efficacement des événements liés à des dates. Cette solution est conçue pour être simple, performante et facilement intégrable dans n'importe quel projet Python nécessitant une gestion temporelle d'événements.

## Fonctionnalités

- Stockage d'événements associés à des dates et heures précises
- Récupération efficace d'événements par plage de dates
- Maintien automatique du tri des événements par date
- Gestion des événements avec nom et niveau d'importance
- Optimisation pour les recherches par plage temporelle

## Architecture

L'architecture du projet est délibérément simple mais efficace, privilégiant la facilité d'utilisation et la maintenance:

### Structure principale

- Classe `Event`: Représentation d'un événement avec date/heure, nom et importance
- Classe `DatetimeEventStore`: Stockage et récupération des événements

### Structure technique

Le projet utilise une implémentation basée sur des listes triées et des algorithmes de recherche binaire:

- Stockage parallèle des événements et de leurs timestamps
- Recherche binaire pour l'insertion et la récupération
- Utilisation de générateurs pour une récupération efficace en mémoire

### Performances

La solution offre les caractéristiques de performance suivantes:

- Insertion: O(log n) en moyenne
- Recherche par plage: O(log n + k) où k est le nombre d'événements dans la plage demandée
- Empreinte mémoire optimisée

## Conception et choix techniques

### Approche de conception

L'implémentation actuelle reflète une approche pragmatique:

- Structure de données simple mais efficace pour les volumes attendus
- Pas de dépendances externes pour maximiser la portabilité
- Interface claire et intuitive
- Possibilité d'extension future

### Choix de structure de données

Plusieurs options ont été évaluées:

1. **Listes parallèles avec recherche binaire** (choix retenu)

   - Excellent rapport simplicité/performance
   - Facilité de maintenance
   - Performances adaptées aux volumes décrits

2. **Bases de données** (SQLite, etc.)

   - Plus complexes à implémenter et maintenir
   - Dépendances externes
   - Seraient préférables pour des volumes très importants (millions d'événements)

3. **Structures d'arbre équilibré**
   - Complexité d'implémentation plus élevée
   - Bénéfices marginaux pour les volumes attendus

### Patterns et principes appliqués

- **Encapsulation**: Isolation des détails d'implémentation
- **Iterator pattern**: Utilisation de générateurs Python
- **Single Responsibility Principle**: Séparation claire des responsabilités
- **Immutabilité** des événements après insertion

## Installation et utilisation

### Installation

```bash
# Installation depuis un dépôt Git
git clone https://github.com/votre-compte/datetime_event_store.git
cd datetime_event_store
pip install -e .

# Ou depuis PyPI (lorsque publié)
pip install datetime-event-store
```

### Utilisation basique

```python
import datetime
from datetime_event_store import DatetimeEventStore

# Créer une instance
store = DatetimeEventStore()

# Stocker des événements
store.store_event(
    at=datetime.datetime(2023, 5, 15, 14, 30),
    name="Réunion d'équipe",
    importance="haute"
)

# Récupérer des événements sur une période
start = datetime.datetime(2023, 5, 1)
end = datetime.datetime(2023, 5, 31)

for event in store.get_events(start, end):
    print(f"{event.at}: {event.name} (Importance: {event.importance})")
```

### Exemples avancés

```python
# Filtrer les événements par importance
high_priority_events = [
    event for event in store.get_events(start, end)
    if event.importance in ["haute", "critique"]
]

# Utilisation avec d'autres bibliothèques
import pandas as pd

# Convertir les événements en DataFrame pandas
events = list(store.get_events(start, end))
df = pd.DataFrame([
    {"date": e.at, "nom": e.name, "importance": e.importance}
    for e in events
])

# Analyse des événements
print(df.groupby("importance").count())
```

## Tests et qualité du code

Le projet inclut une suite de tests unitaires complète:

```bash
# Exécuter tous les tests
pytest

# Vérifier la couverture du code
pytest --cov=datetime_event_store
```

## CI/CD et déploiement

Le projet est configuré avec plusieurs outils CI/CD:

- **GitHub Actions**: Tests automatiques et déploiement sur différentes versions de Python
- **GitLab CI/CD**: Pipeline complet avec lint, test, build et deploy
- **Docker**: Conteneurisation pour faciliter le déploiement et les tests

## Limitations actuelles et évolutions futures

### Limitations

- Stockage uniquement en mémoire (pas de persistance)
- Pas d'indexation multi-attributs (uniquement par date)
- Pas d'optimisation spécifique pour une concurrence intensive

### Évolutions potentielles

1. **Persistance des données**

   - Sauvegarde/chargement vers JSON, pickle ou SQLite

2. **Indexation avancée**

   - Recherche par attributs supplémentaires (ex: importance)

3. **API étendue**

   - Méthodes pour suppression, mise à jour, agrégation

4. **Optimisations de performance**

   - Structure alternative pour très grands volumes
   - Optimisation mémoire avec `__slots__`

5. **Support de concurrence**
   - Verrouillage fin ou structures sans verrou

## Conclusion

DatetimeEventStore est une solution efficace et légère pour la gestion d'événements temporels en Python. Sa conception privilégie la simplicité et l'efficacité pour les cas d'usage courants, tout en restant flexible pour des évolutions futures.

Pour les applications nécessitant des volumes très importants ou des fonctionnalités avancées (persistance, requêtes complexes, haute concurrence), une évolution vers une solution basée sur une base de données pourrait être envisagée.
