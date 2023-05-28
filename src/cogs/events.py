import uuid
import datetime
import re

from discord.ext import commands
from bot_state import BotState
from constants import TIME_DELTA_REGEX
from models.event import Event

from utils import create_timestamp, quote_message

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
        user_subscriptions = self.bot_state.userid_to_categories.get(user_id, [])

        help_text = quote_message(f'future events for {ctx.author.name}:\n\n')

        for subscribed_category_name in user_subscriptions:
            category_event_ids = self.bot_state.categoryname_to_events.get(subscribed_category_name, [])
            for event_id in category_event_ids:
                event = self.bot_state.events[event_id]
                help_text += event.format_info() + "\n"

        await ctx.send(help_text)

    @event.command(name='add', description='Add event')
    async def add(self, ctx, name: str, category_name: str, deltaTime: str = None):
        if not self.bot_state.categories.get(category_name):
            await ctx.send(quote_message(f'category "{category_name}" does not exist'))
            return
        
        user_id = ctx.author.id
        user_subscriptions = self.bot_state.userid_to_categories.get(user_id, [])

        if not category_name in user_subscriptions:
            await ctx.send(quote_message(f'{ctx.author.name} not subscribed to category "{category_name}"'))
            return

        event_id = uuid.uuid4().hex[:8]
        
        event_timestamp = self._get_timestamp(deltaTime)
        if event_timestamp is None:
            await ctx.send(quote_message(f'{ctx.author.name} invalid event delta time, must be (0-99)d(0-99)h(0-99)m'))
            return

        new_event = Event(event_id, name, event_timestamp, category_name, user_id)
        self.bot_state.events[event_id] = new_event

        if not self.bot_state.categoryname_to_events.get(category_name):
            self.bot_state.categoryname_to_events[category_name] = []

        self.bot_state.categoryname_to_events[category_name].append(event_id)

        await ctx.send(f'{ctx.author.name} created event {new_event.format_info()}')

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
        self.bot_state.categoryname_to_events.get(event.category_name).remove(event_id)

        await ctx.send(quote_message(f'{ctx.author.name} deleted event "{event_id}"'))

    @event.command(name='notify', description='Notify event')
    async def notify(self, ctx, event_id):
        if not self.bot_state.events.get(event_id):
            await ctx.send(quote_message(f'event "{event_id}" does not exist'))
            return
        
        user_id = ctx.author.id
        event = self.bot_state.events.get(event_id)

        if event.owner_id != user_id:
            await ctx.send(quote_message(f'{ctx.author.name} is not the owner of event "{event_id}"'))
            return

        notif_category = self.bot_state.categories.get(event.category_name)
        
        await ctx.send(quote_message('MANUAL NOTIFICATION'))
        await ctx.send(event.format_info())
        if len(notif_category.user_ids) > 0:
            await ctx.send("\n\n" + notif_category.mention_all_users())

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.event add [name] [category_name] [deltaTime]'))
        else:
            raise error

    @notify.error
    async def notify_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.event notify [id]'))
        else:
            raise error

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.event delete [id]'))
        else:
            raise error

    def _get_timestamp(self, deltaTime: str):
        event_timestamp = datetime.datetime.now()

        if deltaTime is None:
            return round(event_timestamp.timestamp())

        matches = re.match(TIME_DELTA_REGEX, deltaTime)
        if not matches or not matches.group(0):
            return None
        
        # Add days
        if matches.group(1):
            days = int(matches.group(1)[:-1])
            event_timestamp = event_timestamp + datetime.timedelta(days=days)

        # Add hours
        if matches.group(2):
            hours = int(matches.group(2)[:-1])
            event_timestamp = event_timestamp + datetime.timedelta(hours=hours)

        # Add minutes
        if matches.group(3):
            minutes = int(matches.group(3)[:-1])
            event_timestamp = event_timestamp + datetime.timedelta(minutes=minutes)

        return round(event_timestamp.timestamp())