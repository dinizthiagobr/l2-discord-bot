from utils import create_timestamp


class Event:
    def __init__(self, id, name, timestamp, category_name, owner_id):
        self.id = id
        self.name = name
        self.timestamp = timestamp
        self.category_name = category_name
        self.owner_id = owner_id

    def format_info(self):
        return f'({self.id}) {self.name}: {create_timestamp(self.timestamp)}'