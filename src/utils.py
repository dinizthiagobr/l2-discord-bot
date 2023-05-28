def quote_message(message: str):
    return f'```{message}```'

def mention_user(user_id: str):
    return f'<@{user_id}>'

def create_timestamp(timestamp: str):
    return f'<t:{timestamp}:R> (<t:{timestamp}:f>)'
