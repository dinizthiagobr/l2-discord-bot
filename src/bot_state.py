from typing import Dict
from models.notif_category import NotificationCategory

class BotState:
    def __init__(self):
        self.notif_categories: Dict[str, NotificationCategory] = {}