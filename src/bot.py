# OAuth2 client secret: sDCCF47d0vK8AghicAUHpTzjCl8fT67s

import discord
from discord.ext import commands

from bot_state import BotState
from cogs.categories import Categories
from cogs.events import Events
from cogs.subscriptions import Subscriptions
from utils import mention_user, quote_message

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)
bot_state = BotState()

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.add_cog(Categories(bot_state))
    await bot.add_cog(Subscriptions(bot_state))
    await bot.add_cog(Events(bot_state))

@bot.command(name='ping', description='pong')
async def ping(ctx):
    await ctx.send(quote_message('pong'))

@bot.command(name='me', description='mention me')
async def ping(ctx):
    await ctx.send(mention_user(ctx.author.id))

@bot.command(name='commands', description='Lists available commands')
async def list_commands(ctx):
    help_text = ''

    for command in bot.commands:
        help_text += f'.{command} -> {command.description}\n'

    await ctx.send(quote_message(help_text))

bot.run('MTExMTQ2MzY4MjI0MTc0MDk3Mw.Gj9U_-.payGnsL3n95qDRjiYFIYH69ECVnxkVTN8AJt_8')