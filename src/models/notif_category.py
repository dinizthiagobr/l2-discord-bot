from utils import mention_user


class NotificationCategory:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.user_ids = []

    def mention_all_users(self):
        result = ''

        for user in self.user_ids:
            result += mention_user(user)

        return result