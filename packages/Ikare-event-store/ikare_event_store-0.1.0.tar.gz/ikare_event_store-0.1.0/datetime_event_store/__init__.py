"""
Module DatetimeEventStore pour stocker et récupérer des événements associés à des dates.
"""

# Importer et exposer directement la classe DatetimeEventStore
from .event_store import DatetimeEventStore

# Vous pouvez également exposer la classe Event si vous en avez besoin dans vos tests
from .event_store import Event

# Version du package
__version__ = '0.1.0'