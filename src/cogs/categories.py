from discord.ext import commands
from bot_state import BotState

from models.notif_category import NotificationCategory
from utils import quote_message

class Categories(commands.Cog):
    bot_state: BotState

    def __init__(self, bot_state):
        self.bot_state = bot_state

    @commands.group(name='category', description='List available categories commands')
    async def category(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(quote_message('.category [list add delete]'))
            return

    @category.command(name='list', description='List all notification categories')
    async def list(self, ctx):
        if len(self.bot_state.categories.keys()) == 0:
            await ctx.send(quote_message('no categories'))
            return

        help_text = ''

        for notif_category in self.bot_state.categories.values():
            help_text += f'{notif_category.name}: {notif_category.description}\n'

        await ctx.send(quote_message(help_text))

    @category.command(name='add', description='Add notification category')
    @commands.is_owner()
    async def add(self, ctx, name: str, description: str):
        if self.bot_state.categories.get(name):
            await ctx.send(quote_message(f'category "{name}" already exists'))
            return

        self.bot_state.categories[name] = NotificationCategory(name, description)
        await ctx.send(quote_message(f'category "{name}" created'))

    @category.command(name='delete', description='Remove notification category')
    @commands.is_owner()
    async def delete(self, ctx, name: str):
        if not self.bot_state.categories.get(name):
            await ctx.send(quote_message(f'category "{name}" does not exist'))
            return

        # Delete existing events for category
        for event_id in self.bot_state.categoryname_to_events.get(name, []):
            del self.bot_state.events[event_id]

        del self.bot_state.categoryname_to_events[name]

        # Delete existing subscriptions to category
        for user_subscriptions in self.bot_state.userid_to_categories.values():
            if name in user_subscriptions:
                user_subscriptions.remove(name)

        del self.bot_state.categories[name]

        await ctx.send(quote_message(f'category "{name}" deleted'))

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.config add [name] [description]'))

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.config delete [name]'))