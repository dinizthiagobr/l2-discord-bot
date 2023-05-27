from typing import Dict, List
from models.event import Event
from models.notif_category import NotificationCategory

class BotState:
    def __init__(self):
        self.categories: Dict[str, NotificationCategory] = {}
        self.userid_to_categories: Dict[str, List[str]] = {}
        self.categoryname_to_events: Dict[str, List[str]] = {}
        self.events: Dict[str, Event] = {}