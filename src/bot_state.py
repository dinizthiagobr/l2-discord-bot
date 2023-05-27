from typing import Dict, List
from models.event import Event
from models.notif_category import NotificationCategory

class BotState:
    def __init__(self):
        self.notif_categories: Dict[str, NotificationCategory] = {}
        self.member_categories_subscriptions: Dict[str, List[str]] = {}
        self.category_events: Dict[str, List[str]] = {}
        self.events: Dict[str, Event] = {}