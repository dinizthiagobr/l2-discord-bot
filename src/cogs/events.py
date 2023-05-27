import uuid
from discord.ext import commands
from bot_state import BotState
from models.event import Event

from utils import quote_message

class Events(commands.Cog):
    bot_state: BotState

    def __init__(self, bot_state):
        self.bot_state = bot_state

    @commands.group(name='event', description='List available event commands')
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(quote_message('.event [list add delete]'))
            return

    @event.command(name='list', description='List all events from subscribed categories')
    async def list_all_subscribed(self, ctx):
        user_id = ctx.author.id
        user_subscriptions = self.bot_state.member_categories_subscriptions.get(user_id, [])

        help_text = f'future events for {ctx.author.name}:\n'

        for subscribed_category_name in user_subscriptions:
            category_event_ids = self.bot_state.category_events.get(subscribed_category_name, [])
            for event_id in category_event_ids:
                event = self.bot_state.events[event_id]
                help_text += f'({event_id}) {event.name}: {event.timestamp}'

        await ctx.send(quote_message(help_text))

    @event.command(name='add', description='Add event')
    async def add(self, ctx, name: str, category_name: str, timestamp: str):
        if not self.bot_state.notif_categories.get(category_name):
            await ctx.send(quote_message(f'category "{category_name}" does not exist'))
            return
        
        user_id = ctx.author.id
        user_subscriptions = self.bot_state.member_categories_subscriptions.get(user_id, [])

        if not category_name in user_subscriptions:
            await ctx.send(quote_message(f'{ctx.author.name} not subscribed to category "{category_name}"'))
            return

        event_id = uuid.uuid4().hex[:8]

        new_event = Event(event_id, name, timestamp, category_name, user_id)
        self.bot_state.events[event_id] = new_event

        if not self.bot_state.category_events.get(category_name):
            self.bot_state.category_events[category_name] = []

        self.bot_state.category_events[category_name].append(event_id)

        await ctx.send(quote_message(f'{ctx.author.name} created event "{event_id}"'))

    @event.command(name='delete', description='Delete event')
    async def delete(self, ctx, event_id):
        if not self.bot_state.events.get(event_id):
            await ctx.send(quote_message(f'event "{event_id}" does not exist'))
            return
        
        user_id = ctx.author.id
        event = self.bot_state.events.get(event_id)

        if event.owner_id != user_id:
            await ctx.send(quote_message(f'{ctx.author.name} is not the owner of event "{event_id}"'))
            return

        del self.bot_state.events[event_id]
        self.bot_state.category_events.get(event.category_name).remove(event_id)

        await ctx.send(quote_message(f'{ctx.author.name} deleted event "{event_id}"'))

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.event add [name] [category_name] [timestamp]'))

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.event delete [id]'))