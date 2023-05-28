import asyncio
import time

from discord.ext import commands
from bot_state import BotState
from constants import EVENT_NOTIFICATION_THRESHOLD_SECONDS

from utils import quote_message

class Notifications(commands.Cog):
    bot_state: BotState
    bot: commands.Bot
    event_notification_task: asyncio.Task

    def __init__(self, bot, bot_state):
        self.bot_state = bot_state
        self.bot = bot
        self.event_notification_task = asyncio.create_task(self._notify_events())

    @commands.command(name='set_channel', description='Set notification channel', hidden=True)
    @commands.is_owner()
    async def set_channel(self, ctx):
        self.bot_state.notif_channel_id = ctx.channel.id

        if self.event_notification_task is not None:
            self.event_notification_task.cancel()

        self.event_notification_task = asyncio.create_task(self._notify_events())

    async def _notify_events(self):
        notif_channel = self.bot.get_channel(self.bot_state.notif_channel_id)
        if notif_channel is None:
            self.event_notification_task = None
            return

        await notif_channel.send(quote_message('now using this channel for notifications'))

        while True:
            pending_events = self.bot_state.events
            for event in pending_events.values():
                time_until_event_seconds = event.timestamp - time.time()

                if time_until_event_seconds <= EVENT_NOTIFICATION_THRESHOLD_SECONDS:
                    notif_category = self.bot_state.categories.get(event.category_name)

                    # Notify and delete event
                    await notif_channel.send(quote_message('AUTOMATIC NOTIFICATION -- EVENT STARTING SOON!'))
                    await notif_channel.send(event.format_info())
                    if len(notif_category.user_ids) > 0:
                        await notif_channel.send("\n\n" + notif_category.mention_all_users())

                    del self.bot_state.events[event.id]
                    self.bot_state.categoryname_to_events.get(event.category_name).remove(event.id)

                    await asyncio.sleep(5)

            await asyncio.sleep(5)