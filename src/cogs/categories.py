from discord.ext import commands
from bot_state import BotState

from models.notif_category import NotificationCategory

class Categories(commands.Cog):
    bot_state: BotState

    def __init__(self, bot_state):
        self.bot_state = bot_state

    @commands.group(name='category', description='List notification categories')
    async def category(self, ctx):
        if ctx.invoked_subcommand is None:
            help_text = '```'

            for notif_category in self.bot_state.notif_categories.values():
                help_text += f'{notif_category.name}: {notif_category.description}\n'

            help_text += '```'

            await ctx.send(help_text)

    @category.command(name='add', description='Add notification category')
    @commands.is_owner()
    async def add(self, ctx, name: str, description: str):
        self.bot_state.notif_categories[name] = NotificationCategory(name, description)
        await ctx.send(f'"{name}" category created')