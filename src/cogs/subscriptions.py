from discord.ext import commands
from bot_state import BotState

from models.notif_category import NotificationCategory
from utils import quote_message

class Subscriptions(commands.Cog):
    bot_state: BotState

    def __init__(self, bot_state):
        self.bot_state = bot_state

    @commands.group(name='subscription', description='List available subscriptions commands')
    async def subscription(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(quote_message('.subscription [list add delete]'))
            return

    @subscription.command(name='list', description='List all subscriptions')
    async def list(self, ctx):
        user_id = ctx.author.id
        user_subscriptions = self.bot_state.userid_to_categories.get(user_id, [])

        if len(user_subscriptions) == 0:
            await ctx.send(quote_message(f'{ctx.author.name} has no subscriptions'))
            return

        help_text = f'{ctx.author.name} is subscribed to:\n'

        for category_name in user_subscriptions:
            category_description = self.bot_state.categories.get(category_name).description
            help_text += f'{category_name}: {category_description}\n'

        await ctx.send(quote_message(help_text))

    @subscription.command(name='add', description='Add subscripton')
    async def add(self, ctx, category_name: str):
        if not self.bot_state.categories.get(category_name):
            await ctx.send(quote_message(f'category "{category_name}" does not exist'))
            return

        user_id = ctx.author.id
        user_subscriptions = self.bot_state.userid_to_categories.get(user_id, [])

        if category_name in user_subscriptions:
            await ctx.send(quote_message(f'{ctx.author.name} is already subscribed to "{category_name}"'))
            return

        user_subscriptions.append(category_name)
        self.bot_state.userid_to_categories[user_id] = user_subscriptions

        await ctx.send(quote_message(f'{ctx.author.name} subscribed to "{category_name}"'))

    @subscription.command(name='delete', description='Remove subscripton')
    async def delete(self, ctx, category_name: str):
        user_id = ctx.author.id
        user_subscriptions = self.bot_state.userid_to_categories.get(user_id, [])

        if not category_name in user_subscriptions:
            await ctx.send(quote_message(f'{ctx.author.name} is not subscribed to "{category_name}"'))
            return

        user_subscriptions.remove(category_name)
        self.bot_state.userid_to_categories[user_id] = user_subscriptions

        await ctx.send(quote_message(f'{ctx.author.name} unsubscribed from "{category_name}"'))
 
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.subscription add [name]'))

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(quote_message('.subscription delete [name]'))