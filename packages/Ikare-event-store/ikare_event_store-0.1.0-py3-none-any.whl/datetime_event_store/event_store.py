"""
DatetimeEventStore avec stockage MongoDB - Un module pour stocker et récupérer des événements associés à des dates.
"""

import datetime
from typing import Any, List, Generator, Optional, Dict
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

class Event:
    """
    Classe représentant un événement avec sa date, son nom et son importance.
    """
    
    def __init__(self, at: datetime.datetime, name: str, importance: str = "normal", event_id: Optional[str] = None):
        """
        Initialise un événement.
        
        Args:
            at: Date et heure de l'événement
            name: Nom ou description de l'événement
            importance: Niveau d'importance de l'événement (défaut: "normal")
            event_id: Identifiant unique de l'événement (optionnel)
        """
        self.at = at
        self.name = name
        self.importance = importance
        self.id = event_id
        
    def __str__(self) -> str:
        """
        Représentation textuelle de l'événement.
        """
        return f"Event(id={self.id}, at={self.at}, name='{self.name}', importance='{self.importance}')"
    
    def __repr__(self) -> str:
        """
        Représentation formelle de l'événement.
        """
        return self.__str__()
    
    @classmethod
    def from_document(cls, doc: Dict) -> 'Event':
        """
        Crée un événement à partir d'un document MongoDB.
        """
        return cls(
            at=doc['at'],
            name=doc['name'],
            importance=doc['importance'],
            event_id=str(doc['_id'])
        )
    
    def to_document(self) -> Dict:
        """
        Convertit l'événement en document MongoDB.
        """
        doc = {
            'at': self.at,
            'name': self.name,
            'importance': self.importance
        }
        if self.id:
            doc['_id'] = ObjectId(self.id)
        return doc


class DatetimeEventStore:
    """
    Classe pour stocker et récupérer des événements liés à des dates, avec stockage MongoDB.
    """
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/", 
                 db_name: str = "datetime_events", collection_name: str = "events"):
        """
        Initialise le magasin d'événements avec MongoDB.
        
        Args:
            connection_string: URL de connexion MongoDB
            db_name: Nom de la base de données
            collection_name: Nom de la collection pour les événements
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.events_collection = self.db[collection_name]
        
        # Création d'un index sur le champ 'at' pour des recherches plus rapides
        self.events_collection.create_index("at")
    
    def store_event(self, at: datetime.datetime, name: str, importance: str = "normal") -> Event:
        """
        Stocke un événement associé à une date et heure.
        
        Args:
            at: Date et heure de l'événement
            name: Nom ou description de l'événement
            importance: Niveau d'importance de l'événement (défaut: "normal")
            
        Returns:
            Event: L'événement créé avec son ID
        """
        # Validation du type de 'at'
        if not isinstance(at, datetime.datetime):
            raise TypeError("Le paramètre 'at' doit être une instance de datetime.datetime")
        
        # Création de l'événement
        event = Event(at, name, importance)
        
        # Conversion en document et insertion dans MongoDB
        doc = event.to_document()
        result = self.events_collection.insert_one(doc)
        
        # Mise à jour de l'ID de l'événement
        event.id = str(result.inserted_id)
        
        return event
    
    def get_events(self, start: datetime.datetime, end: datetime.datetime) -> Generator[Event, None, None]:
        """
        Récupère les événements dans une plage de dates spécifiée.
        
        Args:
            start: Date et heure de début de la période
            end: Date et heure de fin de la période
            
        Returns:
            Generator: Générateur d'événements dans la plage spécifiée
        """
        # Gestion des dates invalides
        if start > end:
            start, end = end, start
            
        # Requête MongoDB pour trouver les événements dans la plage de dates
        query = {"at": {"$gte": start, "$lte": end}}
        
        # Tri par date (ordre croissant)
        cursor = self.events_collection.find(query).sort("at", pymongo.ASCENDING)
        
        # Conversion des documents en objets Event
        for doc in cursor:
            yield Event.from_document(doc)
    
    def delete_event(self, event_id: str) -> bool:
        """
        Supprime un événement par son ID.
        
        Args:
            event_id: Identifiant de l'événement à supprimer
            
        Returns:
            bool: True si l'événement a été supprimé, False sinon
        """
        try:
            result = self.events_collection.delete_one({"_id": ObjectId(event_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erreur lors de la suppression de l'événement: {e}")
            return False
    
    def update_event(self, event_id: str, name: Optional[str] = None, 
                     at: Optional[datetime.datetime] = None, 
                     importance: Optional[str] = None) -> Optional[Event]:
        """
        Met à jour un événement existant.
        
        Args:
            event_id: Identifiant de l'événement à mettre à jour
            name: Nouveau nom (optionnel)
            at: Nouvelle date/heure (optionnel)
            importance: Nouvelle importance (optionnel)
            
        Returns:
            Event: L'événement mis à jour ou None si non trouvé
        """
        try:
            # Préparer les champs à mettre à jour
            update_fields = {}
            if name is not None:
                update_fields["name"] = name
            if at is not None:
                update_fields["at"] = at
            if importance is not None:
                update_fields["importance"] = importance
            
            if not update_fields:
                return None  # Rien à mettre à jour
            
            # Effectuer la mise à jour
            result = self.events_collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                return None  # Aucun document n'a été modifié
            
            # Récupérer et retourner l'événement mis à jour
            doc = self.events_collection.find_one({"_id": ObjectId(event_id)})
            if doc:
                return Event.from_document(doc)
            return None
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'événement: {e}")
            return None
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """
        Récupère un événement par son ID.
        
        Args:
            event_id: Identifiant de l'événement
            
        Returns:
            Event: L'événement trouvé ou None si non trouvé
        """
        try:
            doc = self.events_collection.find_one({"_id": ObjectId(event_id)})
            if doc:
                return Event.from_document(doc)
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'événement: {e}")
            return None
    
    def clear_all_events(self) -> int:
        """
        Supprime tous les événements de la collection.
        
        Returns:
            int: Nombre d'événements supprimés
        """
        result = self.events_collection.delete_many({})
        return result.deleted_count
    
    def count_events(self, start: Optional[datetime.datetime] = None, 
                     end: Optional[datetime.datetime] = None) -> int:
        """
        Compte le nombre d'événements, éventuellement dans une plage de dates.
        
        Args:
            start: Date et heure de début (optionnel)
            end: Date et heure de fin (optionnel)
            
        Returns:
            int: Nombre d'événements
        """
        query = {}
        if start or end:
            query["at"] = {}
            if start:
                query["at"]["$gte"] = start
            if end:
                query["at"]["$lte"] = end
        
        return self.events_collection.count_documents(query)
    
    def close(self):
        """
        Ferme la connexion à MongoDB.
        """
        self.client.close()